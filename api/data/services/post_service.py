from typing import List

from data.models.post import Post
from data.models.user import User
from data.repositories.post_repository import PostRepository


class PostService:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository

    def create(self, post_dict: dict) -> bool:
        post = Post.from_dict(post_dict)
        return self.post_repository.create(post=post)

    def get_by_username(self, username: str) -> List[Post]:
        return self.post_repository.get_by_username(username=username)

    def get_for_username(self, username: str) -> List[Post]:
        return self.post_repository.get_for_username(username=username)

    def delete(self, id: int) -> bool:
        return self.post_repository.delete(id=id)

    def append_user_to_liked_by(self, id: int, username: str):
        return self.post_repository.append_user_to_liked_by(id=id, username=username)

    def pop_user_from_liked_by(self, id: int, username: str):
        return self.post_repository.pop_user_from_liked_by(id=id, username=username)
