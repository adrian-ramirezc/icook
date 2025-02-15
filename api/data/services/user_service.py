from typing import Dict, List, Optional

from data.models.user import User
from data.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create(self, user_dict: dict) -> bool:
        user = User.from_dict(user_dict)
        user.hash_password()
        return self.user_repository.create(user=user)

    def get(self, username: str) -> Optional[User]:
        return self.user_repository.get(username=username)

    def log_in(self, username: str, password: str) -> str:
        return self.user_repository.log_in(username=username, password=password)

    def get_many(self, usernames: List[str]) -> List[User]:
        return self.user_repository.get_many(usernames=usernames)

    def update(self, user_dict: Dict[str, str]):
        username = user_dict["username"]
        user_dict.pop("username")
        return self.user_repository.update(username=username, keys=user_dict)
