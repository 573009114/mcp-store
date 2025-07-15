from pydantic import BaseModel
from typing import Optional

class ArticleCreate(BaseModel):
    title: str
    content: str
    author: Optional[str] = "anonymous"

class ArticleUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    author: Optional[str] 