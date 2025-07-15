from .db import get_conn
from datetime import datetime

def create_article(title, content, author):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO articles (title, content, author, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
              (title, content, author, datetime.now(), datetime.now()))
    conn.commit()
    article_id = c.lastrowid
    conn.close()
    return {"id": article_id, "msg": "ok"}

def delete_article(article_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM articles WHERE id=?', (article_id,))
    conn.commit()
    conn.close()
    return {"deleted": c.rowcount}

def update_article(article_id, title, content, author):
    conn = get_conn()
    c = conn.cursor()
    fields = []
    values = []
    if title is not None:
        fields.append("title=?")
        values.append(title)
    if content is not None:
        fields.append("content=?")
        values.append(content)
    if author is not None:
        fields.append("author=?")
        values.append(author)
    if not fields:
        return {"error": "无更新内容"}
    fields.append("updated_at=?")
    values.append(datetime.now())
    values.append(article_id)
    sql = f'UPDATE articles SET {", ".join(fields)} WHERE id=?'
    c.execute(sql, values)
    conn.commit()
    conn.close()
    return {"updated": c.rowcount}

def get_article(article_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, title, content, author, created_at, updated_at FROM articles WHERE id=?', (article_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(zip(["id", "title", "content", "author", "created_at", "updated_at"], row))
    return {"error": "未找到"}

def get_articles(skip=0, limit=20):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, title, content, author, created_at, updated_at FROM articles ORDER BY created_at DESC LIMIT ? OFFSET ?', (limit, skip))
    rows = c.fetchall()
    conn.close()
    return [dict(zip(["id", "title", "content", "author", "created_at", "updated_at"], row)) for row in rows] 