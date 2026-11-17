"""Graphe LangGraph de l'agent de cadrage.

        ┌──────────┐   appel d'outil ?   ┌─────────┐
START ─►│  agent   │ ──────── oui ─────► │  tools  │
        │  (LLM)   │ ◄────────────────── │         │
        └──────────┘                     └─────────┘
              │ non (réponse à l'utilisateur)
              ▼
             END

L'état contient l'historique des messages. Un checkpointer garde la mémoire de
chaque conversation (identifiée par un thread_id) entre deux messages.
"""

from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from .prompts import SYSTEM_PROMPT
from .tools import TOOLS

MAX_STEPS = 25  # garde-fou contre les boucles infinies d'appels d'outils


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def build_graph(llm: BaseChatModel | None = None, checkpointer=None):
    if llm is None:
        from .config import get_llm

        llm = get_llm()
    llm_with_tools = llm.bind_tools(TOOLS)

    def agent(state: State) -> dict:
        response = llm_with_tools.invoke([SystemMessage(SYSTEM_PROMPT), *state["messages"]])
        return {"messages": [response]}

    builder = StateGraph(State)
    builder.add_node("agent", agent)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")
    return builder.compile(checkpointer=checkpointer or InMemorySaver())


def run_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}, "recursion_limit": MAX_STEPS}
