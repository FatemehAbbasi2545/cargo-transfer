from src.domain.interfaces.repositories.user_repository import IUserRepository
from src.domain.interfaces.business.user_business_management import IUserBusinessManagement
from src.domain.utils.user_constraints import UserConstraints
from src.domain.utils.security_util import SecurityUtil
from src.domain.exceptions import DatabaseError
from src.domain.DTO.response import Response
from src.domain.entities.user import User

class UserBusinessService(IUserBusinessManagement):
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def register(self, user: User) -> Response:
        if not UserConstraints.validate_phone_number(user.phone_number):
                    return Response(False, "Invalid Mobile Phone!")

        if not UserConstraints.validate_password(user.password):
            msg = '> The password must:\n> Be at least 8 characters long.\n> Contain both uppercase and lowercase English letters.\n'
            msg += '> Include numbers (0-9).\n'
            msg += '> Include at least one of the following characters: * or @.'  
            return Response(False, message=msg)

        user.password = SecurityUtil.hash_password(user.password)
        
        try:
            self.user_repository.save(user)  
            return Response(True, message=f"User {user.user_name} registered successfully", data=user)
        except DatabaseError as error:
            return Response(False, message=error.message) 

    def login(self, user_name: str, password: str) -> Response:
        try:
            user = self.user_repository.get_by_username(user_name)

            if not user:
                return Response(False, message="No user found with this username.")
            
            if not SecurityUtil.verify(password, user.password):
                return Response(False, message="Invalid password.")
            
            return Response(True, data=user)
        except DatabaseError as error:
            return Response(False, message=error.message) 
        
    def Update_password(self, user_id: int, new_password: str) -> Response:
        if not UserConstraints.validate_password(new_password):
            msg = '> The password must:\n> Be at least 8 characters long.\n> Contain both uppercase and lowercase English letters.\n'
            msg += '> Include numbers (0-9).\n'
            msg += '> Include at least one of the following characters: * or @.'  
            return Response(False, message=msg)
        
        new_password = SecurityUtil.hash_password(new_password)

        try:
            if not self.user_repository.update_password(user_id, new_password):
                return Response(False, message="No user found with this ID.")
            return Response(True, message="Operation successful")
        except DatabaseError as error:
            return Response(False, message=error.message)
