from typing import List, Optional
from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator

class CustomerServiceState(TypedDict, total=False):
    """客服图状态：完整状态定义。"""

    intent: str              # 识别出的意图："chat" | "technical question" | "human"
    retrieved_docs: str      # 从用户手册检索到的文档内容
    messages: Annotated[list[AnyMessage], operator.add]  # 对话历史记录
    llm_calls: int             # 调用模型的次数计数
    draft_response: str      # 起草的回复
    user_query: str          # 用户查询
