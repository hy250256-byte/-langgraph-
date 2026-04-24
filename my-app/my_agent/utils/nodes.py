import os
from langchain_openai import ChatOpenAI

from my_agent.utils.state import CustomerServiceState
from my_agent.utils.tools import (
    classify_intent_keywords,
    get_manual_toc,
    get_human_fallback_message,
    get_chapter_content,
)

DEFAULT_DOUBAO_MODEL = "doubao-seed-2-0-mini-260215"
DEFAULT_ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"


def _build_llm() -> ChatOpenAI | None:
    """按环境变量构建豆包模型客户端。"""
    api_key = os.getenv("ARK_API_KEY", "").strip()
    if not api_key:
        return None

    return ChatOpenAI(
        model=os.getenv("DOUBAO_MODEL", DEFAULT_DOUBAO_MODEL),
        api_key=api_key,
        base_url=os.getenv("ARK_BASE_URL", DEFAULT_ARK_BASE_URL),
        temperature=0.7,
    )


def intent_classifier_node(state: CustomerServiceState) -> CustomerServiceState:
    """意图分类节点：判断用户意图。"""
    # 优先从 messages 读取最新的用户输入
    query = ""
    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        # 获取 content
        if isinstance(last_msg, dict):
            content = last_msg.get("content", "")
        elif hasattr(last_msg, "content"):
            content = last_msg.content
        else:
            content = ""

        query = _extract_text(content).strip()

    # 如果 messages 中没有，才从 user_query 读取
    if not query:
        query = state.get("user_query", "")
        query = _extract_text(query).strip()

    if not query:
        return {"intent": "chat", "user_query": ""}

    intent = classify_intent_keywords.invoke({"query": query})
    return {"intent": intent, "user_query": query}


def _extract_text(content) -> str:
    """从 str | list[str | dict] 格式中提取纯文本"""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict) and "text" in item:
                texts.append(item["text"])
            elif isinstance(item, dict) and "type" in item and item["type"] == "text":
                texts.append(item.get("text", ""))
        return "".join(texts)

    return str(content)


def chat_node(state: CustomerServiceState) -> CustomerServiceState:
    """闲聊节点：直接调用大模型。"""
    query = state.get("user_query", "").strip()

    llm = _build_llm()
    if llm is None:
        return {"draft_response": "你好！我们可以聊聊天。"}

    system_prompt = "你是一个友好的客服助手，用自然、亲切的语气与用户聊天。"
    try:
        result = llm.invoke(
            [
                ("system", system_prompt),
                ("human", query),
            ]
        )
        return {"draft_response": result.content}
    except Exception:
        return {"draft_response": "你好！很高兴为你服务。"}


def doc_search_node(state: CustomerServiceState) -> CustomerServiceState:
    query = state.get("user_query", "").strip()
    
    # 1. 获取目录
    toc = get_manual_toc.invoke({})
    
    # 2. 将目录 + state传给 LLM，让 LLM 选择章节
    prompt_text = f"""
    你是一个智能文档检索助手。

    用户的问题是：
    "{query}"
    
    请参考以下文档目录（TOC），找出最能解决用户问题的章节的一级标题，如用户提问“挂衣片怎么挂”，则返回“常见问题解答”：
    {toc}
    
    要求：
    1. 只返回一级标题名称，不要包含“章节：”等前缀，也不要包含句号。
    2. 如果目录中没有相关章节，请返回 "常见问题解答"。
    3. 必须完全匹配目录中的文字。
    """
    
    llm = _build_llm()
    if llm is None:
        return {"draft_response": "无法调用模型。"}
    
    try:
        result = llm.invoke(
            [
                ("system", prompt_text),
                ("human", query),
            ]
        )
        chapter_name = result.content.strip()
    except Exception:
        chapter_name = "常见问题解答"
    
    # 3. 读取章节内容
    content = get_chapter_content.invoke({"chapter_name": chapter_name})
    if not content:
        return {"retrieved_docs": "未找到相关手册。"}
    return {"retrieved_docs": content}


def human_node(_state: CustomerServiceState) -> CustomerServiceState:
    """人工客服节点：返回转接提示。"""
    message = get_human_fallback_message.invoke({})
    return {"draft_response": message}


def draft_reply_node(state: CustomerServiceState) -> CustomerServiceState:
    """起草回复节点：根据不同意图生成最终回复。"""
    intent = state.get("intent", "technical question")
    query = state.get("user_query", "").strip()
    retrieved_docs = state.get("retrieved_docs", "")

    if intent == "chat":
        return state

    if intent == "human":
        return state

    if intent == "technical question":
        if retrieved_docs:
            llm = _build_llm()
            if llm:
                system_prompt = (
                    "你是一个吊挂系统软件客服助手。根据以下用户手册内容回答用户问题。"
                    "回答要简洁、礼貌、可执行。\n\n"
                    "回复例子：用户：一打开软件就提示 TCP/IP 错误，登不进去。\n"
                    "客服助手：\n"
                    "这是数据库连接异常，请按以下排查：\n"
                    "1.检查电脑与服务器网络是否通，能否 ping 通服务器 IP。\n"
                    "2.确认SQL Server Browser 服务已设为自动启动。\n"
                    "3.检查服务器是否CPU 过高、磁盘满。\n"
                    "4.确认配置文件里服务器 IP、端口、账号密码正确。\n"
                    "需要我帮您核对配置文件吗？\n\n"
                    f"用户手册内容：\n{retrieved_docs}"
                )
                try:
                    result = llm.invoke([
                        ("system", system_prompt),
                        ("human", query),
                    ])
                    return {"draft_response": result.content}
                except Exception:
                    pass
            return {"draft_response": "根据用户手册，" + retrieved_docs[:200]}
        else:
            llm = _build_llm()
            if llm:
                system_prompt = (
                    "你是一个吊挂系统软件客服助手。回答要简洁、礼貌、可执行。"
                    "若信息不足，先向用户追问必要信息（如系统型号、具体生产环节等）。"
                )
                try:
                    result = llm.invoke([
                        ("system", system_prompt),
                        ("human", query),
                    ])
                    return {"draft_response": result.content}
                except Exception:
                    pass
            return {"draft_response": "你好，请描述一下你遇到的吊挂系统问题。"}

    return {"draft_response": "你好，请描述一下你的问题。"}


def send_reply_node(state: CustomerServiceState) -> CustomerServiceState:
    """发送回复节点：返回最终结果。"""
    from langchain_core.messages import AIMessage

    draft_response = state.get("draft_response", "")
    return {
        "messages": [AIMessage(content=draft_response)],
        "response": draft_response
    }
