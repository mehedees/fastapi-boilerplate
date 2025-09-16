import base64
import hashlib
import hmac
import secrets

import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class SecureHashManager:
    def __init__(self, secret_key: str):
        """
        Initialize hash manager with secret key (pepper)

        Args:
            secret_key: Application-wide secret key for additional security
        """
        self.secret_key = secret_key

    @property
    def argon2_password_hasher(self) -> PasswordHasher:
        # Initialize Argon2 hasher with secure parameters
        return PasswordHasher(
            time_cost=3,  # Number of iterations
            memory_cost=65536,  # Memory usage in KiB (64MB)
            parallelism=1,  # Number of parallel threads
            hash_len=32,  # Length of hash in bytes
            salt_len=16,  # Length of salt in bytes
        )

    @staticmethod
    def make_hmac(key: bytes, message: bytes) -> str:
        """Create HMAC using SHA256"""
        return hmac.new(key, message, hashlib.sha256).hexdigest()

    def _apply_pepper(self, password: str, salt: bytes) -> str:
        """
        Apply secret key (pepper) to password using HMAC

        This adds application-wide secret that attackers won't have
        even if they compromise the database
        """
        # Combine password and salt
        password_salt = password.encode("utf-8") + salt

        # Apply HMAC with secret key
        peppered: str = SecureHashManager.make_hmac(
            self.secret_key.encode("utf-8"),
            password_salt,
        )

        return peppered

    def hash_password_argon2(self, password: str) -> str:
        """
        Hash password using Argon2id with pepper

        Returns: Base64 encoded string containing salt + hash
        """
        # Generate random salt
        salt = secrets.token_bytes(16)

        # Apply pepper (HMAC with secret key)
        peppered_password = self._apply_pepper(password, salt)

        # Hash with Argon2
        hash_result = self.argon2_password_hasher.hash(peppered_password)

        # Encode salt + hash for storage
        # Format: base64(salt) + "$" + argon2_hash
        salt_b64 = base64.b64encode(salt).decode("utf-8")
        stored_hash = f"{salt_b64}${hash_result}"

        return stored_hash

    def verify_password_argon2(self, password: str, stored_hash: str) -> bool:
        """
        Verify password against stored Argon2 hash
        """
        try:
            # Extract salt and hash
            salt_b64, argon2_hash = stored_hash.split("$", 1)
            salt = base64.b64decode(salt_b64)

            # Apply same pepper
            peppered_password = self._apply_pepper(password, salt)

            # Verify with Argon2
            self.argon2_password_hasher.verify(argon2_hash, peppered_password)
            return True

        except (VerifyMismatchError, ValueError):
            return False

    def hash_password_bcrypt(self, password: str) -> str:
        """
        Hash password using bcrypt with pepper

        Returns: Base64 encoded string containing salt + hash
        """
        # Generate random salt
        salt = secrets.token_bytes(16)

        # Apply pepper
        peppered_password = self._apply_pepper(password, salt)

        # Hash with bcrypt (bcrypt generates its own salt internally)
        bcrypt_hash = bcrypt.hashpw(
            peppered_password.encode("utf-8"), bcrypt.gensalt(rounds=12)
        )

        # Store our salt + bcrypt hash
        salt_b64 = base64.b64encode(salt).decode("utf-8")
        bcrypt_b64 = base64.b64encode(bcrypt_hash).decode("utf-8")
        stored_hash = f"{salt_b64}${bcrypt_b64}"

        return stored_hash

    def verify_password_bcrypt(self, password: str, stored_hash: str) -> bool:
        """
        Verify password against stored bcrypt hash
        """
        try:
            # Extract salt and hash
            salt_b64, bcrypt_b64 = stored_hash.split("$", 1)
            salt = base64.b64decode(salt_b64)
            bcrypt_hash = base64.b64decode(bcrypt_b64)

            # Apply same pepper
            peppered_password = self._apply_pepper(password, salt)

            # Verify with bcrypt
            return bcrypt.checkpw(peppered_password.encode("utf-8"), bcrypt_hash)

        except (ValueError, TypeError):
            return False

    def hash_password_pbkdf2(self, password: str, iterations: int = 100000) -> str:
        """
        Hash password using PBKDF2 with pepper

        Args:
            iterations: Number of PBKDF2 iterations (higher = more secure but slower)
        """
        # Generate random salt
        salt = secrets.token_bytes(32)

        # Apply pepper first
        peppered_password = self._apply_pepper(
            password, salt[:16]
        )  # Use first 16 bytes for pepper

        # Apply PBKDF2
        hash_result = hashlib.pbkdf2_hmac(
            "sha256",
            peppered_password.encode("utf-8"),
            salt,
            iterations,
            64,  # Hash length
        )

        # Store salt + iterations + hash
        salt_b64 = base64.b64encode(salt).decode("utf-8")
        hash_b64 = base64.b64encode(hash_result).decode("utf-8")
        stored_hash = f"{salt_b64}${iterations}${hash_b64}"

        return stored_hash

    def verify_password_pbkdf2(self, password: str, stored_hash: str) -> bool:
        """
        Verify password against stored PBKDF2 hash
        """
        try:
            # Extract components
            parts = stored_hash.split("$")
            salt_b64, iterations_str, hash_b64 = parts[0], parts[1], parts[2]

            salt = base64.b64decode(salt_b64)
            iterations = int(iterations_str)
            expected_hash = base64.b64decode(hash_b64)

            # Apply same pepper
            peppered_password = self._apply_pepper(password, salt[:16])

            # Compute hash
            computed_hash = hashlib.pbkdf2_hmac(
                "sha256", peppered_password.encode("utf-8"), salt, iterations, 64
            )

            # Constant-time comparison
            return hmac.compare_digest(expected_hash, computed_hash)

        except (ValueError, IndexError):
            return False


# # Example usage and testing
# if __name__ == "__main__":
#     # Initialize with secret key
#     SECRET_KEY = "your-super-secret-application-key-keep-this-safe"
#     pm = SecureHashManager(SECRET_KEY)
#
#     # Test password
#     test_password = "MySecurePassword123!"
#
#     print("=== Password Hashing Examples ===\n")
#
#     # Argon2 example (RECOMMENDED)
#     print("1. Argon2id (RECOMMENDED):")
#     argon2_hash = pm.hash_password_argon2(test_password)
#     print(f"Hash: {argon2_hash}")
#     print(f"Verification: {pm.verify_password_argon2(test_password, argon2_hash)}")
#     print(f"Wrong password: {pm.verify_password_argon2('wrong', argon2_hash)}")
#     print()
#
#     # bcrypt example
#     print("2. bcrypt:")
#     bcrypt_hash = pm.hash_password_bcrypt(test_password)
#     print(f"Hash: {bcrypt_hash}")
#     print(f"Verification: {pm.verify_password_bcrypt(test_password, bcrypt_hash)}")
#     print()
#
#     # PBKDF2 example
#     print("3. PBKDF2:")
#     pbkdf2_hash = pm.hash_password_pbkdf2(test_password)
#     print(f"Hash: {pbkdf2_hash}")
#     print(f"Verification: {pm.verify_password_pbkdf2(test_password, pbkdf2_hash)}")
#     print()
#
#     # Security demonstration
#     print("=== Security Features ===")
#     print("✓ Each hash uses unique random salt")
#     print("✓ Secret key (pepper) adds application-wide protection")
#     print("✓ Constant-time comparison prevents timing attacks")
#     print("✓ Strong hashing algorithms (Argon2/bcrypt/PBKDF2)")
#     print("✓ Configurable iterations/memory costs")
#
#
# # Integration example for web applications
# class UserAuthentication:
#     """
#     Example integration for user registration and login
#     """
#
#     def __init__(self, secret_key: str):
#         self.pm = SecureHashManager(secret_key)
#         # In real app, this would be a database
#         self.users = {}
#
#     def register_user(self, username: str, password: str) -> bool:
#         """Register a new user with hashed password"""
#         if username in self.users:
#             return False
#
#         # Hash password (using Argon2 - most secure)
#         password_hash = self.pm.hash_password_argon2(password)
#
#         self.users[username] = {
#             'password_hash': password_hash,
#             'created_at': os.time.time()
#         }
#
#         return True
#
#     def authenticate_user(self, username: str, password: str) -> bool:
#         """Authenticate user login"""
#         if username not in self.users:
#             return False
#
#         stored_hash = self.users[username]['password_hash']
#         return self.pm.verify_password_argon2(password, stored_hash)
#
#     def change_password(self, username: str, old_password: str, new_password: str) -> bool:
#         """Change user password"""
#         if not self.authenticate_user(username, old_password):
#             return False
#
#         new_hash = self.pm.hash_password_argon2(new_password)
#         self.users[username]['password_hash'] = new_hash
#
#         return True
