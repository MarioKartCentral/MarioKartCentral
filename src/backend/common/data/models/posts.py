from dataclasses import dataclass
from common.data.models.player_basic import PlayerBasic

@dataclass
class PostBasic:
    id: int
    title: str
    is_public: bool
    is_global: bool
    creation_date: int
    created_by: PlayerBasic | None

@dataclass
class Post(PostBasic):
    content: str

@dataclass
class PostS3Fields:
    content: str

@dataclass
class PostFilter:
    page: int | None = None

@dataclass
class PostList:
    posts: list[PostBasic]
    count: int
    page_count: int

@dataclass
class CreateEditPostRequestData:
    title: str
    content: str
    is_public: bool