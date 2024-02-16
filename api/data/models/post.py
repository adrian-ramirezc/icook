from sqlalchemy import Column, Integer, String

from data.database import Base


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False)
    description = Column(String(255), nullable=False)
    picture = Column(String(255))

    def __init__(
        self,
        username: str,
        description: str,
        picture: str = "",
    ):
        self.username = username
        self.description = description
        self.picture = picture

    def __repr__(self):
        return f"Post(author={self.username}, description={self.description})"

    def from_dict(user_dict: dict):
        return Post(**user_dict)
