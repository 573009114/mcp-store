import requests
import time
from .config import WECHAT_APPID, WECHAT_APPSECRET

_WECHAT_TOKEN_CACHE = {"access_token": None, "expires_at": 0}

# 获取access_token，自动缓存
def get_access_token():
    now = int(time.time())
    if _WECHAT_TOKEN_CACHE["access_token"] and _WECHAT_TOKEN_CACHE["expires_at"] > now:
        return _WECHAT_TOKEN_CACHE["access_token"]
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_APPID}&secret={WECHAT_APPSECRET}"
    resp = requests.get(url).json()
    if "access_token" in resp:
        _WECHAT_TOKEN_CACHE["access_token"] = resp["access_token"]
        _WECHAT_TOKEN_CACHE["expires_at"] = now + resp.get("expires_in", 7200) - 100
        return resp["access_token"]
    raise Exception(f"获取access_token失败: {resp}")

# 上传图片，返回media_id
def upload_image(image_path: str) -> str:
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={get_access_token()}&type=image"
    with open(image_path, "rb") as f:
        files = {"media": f}
        resp = requests.post(url, files=files).json()
    if "media_id" in resp:
        return resp["media_id"]
    raise Exception(f"图片上传失败: {resp}")

# 上传图文素材到草稿箱（支持封面）
def upload_article_to_draft(title, content, author="anonymous", digest=None, cover_media_id=None):
    access_token = get_access_token()
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    article = {
        "title": title,
        "author": author,
        "content": content,
        "digest": digest or title,
        "need_open_comment": 0,
        "only_fans_can_comment": 0
    }
    if cover_media_id:
        article["thumb_media_id"] = cover_media_id
    data = {"articles": [article]}
    resp = requests.post(url, json=data).json()
    if "media_id" in resp:
        return resp["media_id"]
    raise Exception(f"上传草稿失败: {resp}")

# 发布草稿为群发消息（全量）
def publish_draft(media_id):
    access_token = get_access_token()
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"
    data = {"media_id": media_id}
    resp = requests.post(url, json=data).json()
    if "publish_id" in resp:
        return resp["publish_id"]
    raise Exception(f"群发失败: {resp}")

# 定向群发（按标签/tag_id 或 openid_list）
def mass_send(media_id, tag_id=None, openid_list=None):
    access_token = get_access_token()
    if openid_list:
        # openid_list 群发
        url = f"https://api.weixin.qq.com/cgi-bin/message/mass/send?access_token={access_token}"
        data = {
            "touser": openid_list,
            "mpnews": {"media_id": media_id},
            "msgtype": "mpnews",
            "send_ignore_reprint": 0
        }
    elif tag_id is not None:
        # 按标签群发
        url = f"https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={access_token}"
        data = {
            "filter": {"is_to_all": False, "tag_id": tag_id},
            "mpnews": {"media_id": media_id},
            "msgtype": "mpnews",
            "send_ignore_reprint": 0
        }
    else:
        # 全量群发
        return publish_draft(media_id)
    resp = requests.post(url, json=data).json()
    if "msg_id" in resp:
        return resp
    raise Exception(f"定向群发失败: {resp}") 