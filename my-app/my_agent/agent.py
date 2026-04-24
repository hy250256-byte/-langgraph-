from langgraph.graph import END, START, StateGraph

from my_agent.utils.state import CustomerServiceState
from my_agent.utils.nodes import (
    intent_classifier_node,
    chat_node,
    doc_search_node,
    human_node,
    draft_reply_node,
    send_reply_node,
)



def route_intent(state: CustomerServiceState) -> str:
    """根据意图路由到对应节点。"""
    intent = state.get("intent", "technical question")
    return intent


# 构建图
graph_builder = StateGraph(CustomerServiceState)

# 添加节点
graph_builder.add_node("intent_classifier", intent_classifier_node)
graph_builder.add_node("chat", chat_node)
graph_builder.add_node("doc_search", doc_search_node)
graph_builder.add_node("human", human_node)
graph_builder.add_node("draft_reply", draft_reply_node)
graph_builder.add_node("send_reply", send_reply_node)

# 添加边
graph_builder.add_edge(START, "intent_classifier")

# 条件边：根据意图路由
graph_builder.add_conditional_edges(
    "intent_classifier",
    route_intent,
    {
        "chat": "chat",
        "technical question": "doc_search",
        "human": "human",
    },
)

# 三个分支汇聚到 draft_reply
graph_builder.add_edge("chat", "draft_reply")
graph_builder.add_edge("doc_search", "draft_reply")
graph_builder.add_edge("human", "draft_reply")

# 后续流程
graph_builder.add_edge("draft_reply", "send_reply")
graph_builder.add_edge("send_reply", END)

# langgraph.json 里引用的导出对象
agent = graph_builder.compile()
