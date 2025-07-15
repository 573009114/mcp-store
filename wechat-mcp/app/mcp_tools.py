from fastmcp import FastMCP
from .crud import (
    create_article, delete_article, update_article,
    get_article, get_articles
)
from .wechat_api import upload_article_to_draft, publish_draft, upload_image, mass_send
from typing import Optional, List

mcp = FastMCP("微信工作平台MCP工具")

@mcp.tool("发布文章")
# 创建一篇新文章，需提供标题、内容和作者。
def publish_article(title: str, content: str, author: Optional[str] = "anonymous") -> dict:
    """创建一篇新文章，需提供标题、内容和作者。"""
    return create_article(title, content, author)

@mcp.tool("删除文章")
# 根据文章ID删除指定文章。
def remove_article(article_id: int) -> dict:
    """根据文章ID删除指定文章。"""
    return delete_article(article_id)

@mcp.tool("编辑文章")
# 根据文章ID修改文章的标题、内容或作者。
def edit_article(article_id: int, title: Optional[str] = None, content: Optional[str] = None, author: Optional[str] = None) -> dict:
    """根据文章ID修改文章的标题、内容或作者。"""
    return update_article(article_id, title, content, author)

@mcp.tool("文章详情")
# 获取指定文章的详细信息。
def article_detail(article_id: int) -> dict:
    """获取指定文章的详细信息。"""
    return get_article(article_id)

@mcp.tool("文章列表")
# 分页获取所有文章列表。
def article_list(skip: int = 0, limit: int = 20) -> list:
    """分页获取所有文章列表。"""
    return get_articles(skip, limit)

# 新增：上传图片到微信素材库
@mcp.tool("上传图片")
# 上传本地图片到微信素材库，返回media_id。
def upload_image_tool(image_path: str) -> dict:
    """上传本地图片到微信素材库，返回media_id。"""
    try:
        media_id = upload_image(image_path)
        return {"media_id": media_id}
    except Exception as e:
        return {"error": str(e)}

# 新增：高级发布到公众号，支持封面、定向群发
@mcp.tool("发布到公众号（高级）")
# 支持封面图片、按标签或用户定向群发文章到公众号。
def publish_to_wechat_advanced(
    article_id: int,
    thumb_image_path: Optional[str] = None,
    tag_id: Optional[int] = None,
    openid_list: Optional[List[str]] = None
) -> dict:
    """支持封面图片、按标签或用户定向群发文章到公众号。"""
    article = get_article(article_id)
    if not article or "error" in article:
        return {"error": "未找到文章"}
    try:
        thumb_media_id = None
        if thumb_image_path:
            thumb_media_id = upload_image(thumb_image_path)
        media_id = upload_article_to_draft(
            title=article["title"],
            content=article["content"],
            author=article.get("author", "anonymous"),
            cover_media_id=thumb_media_id
        )
        if openid_list:
            resp = mass_send(media_id, openid_list=openid_list)
        elif tag_id is not None:
            resp = mass_send(media_id, tag_id=tag_id)
        else:
            publish_id = publish_draft(media_id)
            resp = {"msg": "已提交全量群发", "publish_id": publish_id}
        return resp
    except Exception as e:
        return {"error": str(e)}

@mcp.tool("发布到公众号")
# 将指定文章全量群发到微信公众号订阅号。
def publish_to_wechat(article_id: int) -> dict:
    """将指定文章全量群发到微信公众号订阅号。"""
    article = get_article(article_id)
    if "error" in article:
        return {"error": "未找到文章"}
    try:
        media_id = upload_article_to_draft(
            title=article["title"],
            content=article["content"],
            author=article.get("author", "anonymous")
        )
        publish_id = publish_draft(media_id)
        return {"msg": "已提交群发", "publish_id": publish_id}
    except Exception as e:
        return {"error": str(e)} 