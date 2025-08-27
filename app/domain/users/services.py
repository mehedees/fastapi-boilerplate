from sqlmodel import Session


class UserService:
    def __init__(self, session: Session):
        self.session = session
