from dataclasses import dataclass
from common.data.command import Command
from common.data.db import DBWrapper
from common.data.models import *
from datetime import datetime, timezone
import msgspec
from typing import Any

from common.data.s3 import POST_BUCKET, S3Wrapper

@dataclass
class CreatePostCommand(Command[int]):
    title: str
    content: str
    is_public: bool
    is_global: bool
    player_id: int | None
    series_id: int | None = None
    tournament_id: int | None = None

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> int:
        async with db_wrapper.connect() as db:
            creation_date = int(datetime.now(timezone.utc).timestamp())
            row = await db.execute_insert("""INSERT INTO posts(title, is_public, is_global, creation_date, created_by)
                VALUES(?, ?, ?, ?, ?)""", (self.title, self.is_public, self.is_global, creation_date, self.player_id))
            if row is None:
                raise Problem("Failed to create post")
            post_id = row[0]
            if self.series_id:
                await db.execute("INSERT INTO series_posts(series_id, post_id) VALUES(?, ?)", (self.series_id, post_id))
            if self.tournament_id:
                await db.execute("INSERT INTO tournament_posts(tournament_id, post_id) VALUES(?, ?)", (self.tournament_id, post_id))
            await db.commit()
        
        s3_body = PostS3Fields(self.content)
        s3_message = bytes(msgspec.json.encode(s3_body))
        await s3_wrapper.put_object(POST_BUCKET, f"{post_id}.json", s3_message)
        return post_id
    
@dataclass
class EditPostCommand(Command[None]):
    id: int
    title: str
    content: str
    is_public: bool
    is_global: bool
    series_id: int | None = None
    tournament_id: int | None = None

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""UPDATE posts SET title = :title, is_public = :is_public, is_global = :is_global
                                WHERE id = :id
                                AND (:series_id IS NULL OR id IN (
                                    SELECT sp.post_id FROM series_posts sp WHERE sp.series_id = :series_id
                                ))
                                AND (:tournament_id IS NULL OR id IN (
                                    SELECT tp.post_id FROM tournament_posts tp WHERE tp.tournament_id = :tournament_id
                                ))""", {"title": self.title, "is_public": self.is_public, "is_global": self.is_global,
                                    "id": self.id, "series_id": self.series_id, "tournament_id": self.tournament_id}) as cursor:
                rowcount = cursor.rowcount
                if not rowcount:
                    raise Problem("Post not found", status=404)
            await db.commit()
        s3_body = PostS3Fields(self.content)
        s3_message = bytes(msgspec.json.encode(s3_body))
        await s3_wrapper.put_object(POST_BUCKET, f"{self.id}.json", s3_message)

@dataclass
class ListPostsCommand(Command[PostList]):
    filter: PostFilter
    is_global: bool
    is_privileged: bool
    series_id: int | None = None
    tournament_id: int | None = None

    async def handle(self, db_wrapper: DBWrapper):
        filter = self.filter
        query = """SELECT DISTINCT p.id, p.title, p.is_public, p.is_global, p.creation_date, pl.id, pl.name, pl.country_code
                    FROM posts p
                    LEFT JOIN players pl ON p.created_by = pl.id
                    WHERE (is_global = :is_global)
                    AND (p.is_public = 1 OR :is_privileged = 1)
                    AND (:series_id IS NULL OR p.id IN (
                        SELECT sp.post_id FROM series_posts sp WHERE sp.series_id = :series_id
                    ))
                    AND (:tournament_id IS NULL OR p.id IN (
                        SELECT tp.post_id FROM tournament_posts tp WHERE tp.tournament_id = :tournament_id
                    ))
                    ORDER BY p.creation_date DESC
                    """
        query_dict: dict[str, Any] = {"is_global": self.is_global, "series_id": self.series_id, "tournament_id": self.tournament_id, "is_privileged": self.is_privileged}
        
        limit:int = 10
        offset:int = 0
        if filter.page is not None:
            offset = (filter.page - 1) * limit
        posts: list[PostBasic] = []
        async with db_wrapper.connect(readonly=True) as db:
            post_query = f"{query} LIMIT :limit OFFSET :offset"
            async with db.execute(post_query, {**query_dict, "limit": limit, "offset": offset}) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    post_id, title, is_public, is_global, creation_date, player_id, player_name, player_country = row
                    created_by = None
                    if player_id:
                        created_by = PlayerBasic(player_id, player_name, player_country)
                    posts.append(PostBasic(post_id, title, bool(is_public), bool(is_global), creation_date, created_by))

            count_query = f"SELECT COUNT(*) FROM ({query})"
            count = 0
            page_count = 0
            async with db.execute(count_query, query_dict) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                count = int(row[0])
            
            page_count = int(count / limit) + (1 if count % limit else 0)
            return PostList(posts, count, page_count)
        
@dataclass
class GetPostCommand(Command[Post]):
    id: int
    is_privileged: bool
    is_global: bool
    series_id: int | None
    tournament_id: int | None

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        query = """SELECT p.id, p.title, p.is_public, p.is_global, p.creation_date, pl.id, pl.name, pl.country_code
                    FROM posts p
                    LEFT JOIN players pl ON p.created_by = pl.id
                    WHERE p.id = :id
                    AND p.is_global = :is_global
                    AND (p.is_public = 1 OR :is_privileged = 1)
                    AND (:series_id IS NULL OR p.id IN (
                        SELECT sp.post_id FROM series_posts sp WHERE sp.series_id = :series_id
                    ))
                    AND (:tournament_id IS NULL OR p.id IN (
                        SELECT tp.post_id FROM tournament_posts tp WHERE tp.tournament_id = :tournament_id
                    ))"""
        async with db_wrapper.connect() as db:
            async with db.execute(query, {"id": self.id, "is_privileged": self.is_privileged, "series_id": self.series_id, 
                                          "tournament_id": self.tournament_id, "is_global": self.is_global}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Post not found", status=404)
                post_id, title, is_public, is_global, creation_date, player_id, player_name, player_country = row
                created_by = None
                if player_id:
                    created_by = PlayerBasic(player_id, player_name, player_country)
        s3_body = await s3_wrapper.get_object(POST_BUCKET, f"{self.id}.json")
        if not s3_body:
            raise Problem("Failed to get post S3 data")
        post_data = msgspec.json.decode(s3_body, type=PostS3Fields)
        post = Post(post_id, title, bool(is_public), bool(is_global), creation_date, created_by, post_data.content)
        return post