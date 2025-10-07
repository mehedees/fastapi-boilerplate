class BaseScript:
    def __init__(self):
        print("Initializing Base Script")

    def __enter__(self):
        print("Entering Base Script")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting Base Script")
