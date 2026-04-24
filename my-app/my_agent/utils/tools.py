import os
from typing import Optional, Tuple
from langchain.tools import tool

# 意图分类关键词
HUMAN_KEYWORDS = ["转人工", "人工", "找人工"]
CHAT_KEYWORDS = ["你好", "您好", "嗨", "早上好", "下午好", "晚上好", "谢谢", "感谢", "再见", "拜拜"]

# 用户手册目录
DATABASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "docs",
    "database"
)
MANUAL_DIR = os.path.join(DATABASE_DIR, "RS-100")


@tool
def classify_intent_keywords(query: str) -> str:
    """
    第一层：关键词快速匹配意图。
    返回 intent 字符串，如 "human", "chat", "technical question"。
    """
    query_lower = query.lower()

    for keyword in HUMAN_KEYWORDS:
        if keyword in query:
            return "human"

    for keyword in CHAT_KEYWORDS:
        if keyword in query_lower:
            return "chat"

    return "technical question"


@tool
def get_manual_toc() -> str:
    """
    获取 用户手册的目录。

    返回:
        目录.md 的完整内容
    """
    toc_path = os.path.join(MANUAL_DIR, "目录.md")
    if not os.path.exists(toc_path):
        return ""
    try:
        with open(toc_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


@tool
def get_chapter_content(chapter_name: str) -> str:
    """
    获取 RS-100 用户手册指定章节的内容。

    参数:
        chapter_name: 章节文件名，如 "常见问题解答"

    返回:
        章节的 Markdown 内容
    """
    # Add .md extension if not present
    if not chapter_name.endswith('.md'):
        chapter_name = chapter_name + '.md'
    chapter_path = os.path.join(MANUAL_DIR, chapter_name)
    if not os.path.exists(chapter_path):
        return ""
    try:
        with open(chapter_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""




@tool
def get_human_fallback_message() -> str:
    """获取人工客服提示信息。"""
    return "已为你转接人工客服，请稍候..."
