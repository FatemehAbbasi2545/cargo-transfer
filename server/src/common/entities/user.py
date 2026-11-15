from src.common.enums import UserRole

class User:
    def __init__(self, user_id: int = None, name: str = None, user_name: str = None, password: str = None,
            phone_number: str = None, role: UserRole = None, created_at: str = None):
        self.user_id = user_id
        self.name = name
        self.user_name = user_name
        self.password = password
        self.phone_number = phone_number
        self.role = role
        self.created_at = created_at

    def __repr__(self):
        return f'id: {self.user_id}, {self.user_name}, {self.phone_number}, {self.role}'
