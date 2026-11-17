"""Discuter avec l'agent de cadrage dans le terminal.

Usage : python -m agent
"""

from __future__ import annotations

import uuid

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from .config import ConfigError, provider_name
from .graph import build_graph, run_config
from .prompts import WELCOME_MESSAGE


def main() -> None:
    try:
        graph = build_graph()
    except ConfigError as err:
        print(f"⚠️  {err}")
        return

    config = run_config(str(uuid.uuid4()))
    print(f"\n🧭 Agent de cadrage – fournisseur : {provider_name()}  (tapez « quitter » pour sortir)\n")
    print(WELCOME_MESSAGE.replace("**", "").replace("*", ""), "\n")

    while True:
        try:
            user_input = input("Vous > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in {"quitter", "exit", "quit"}:
            break
        if not user_input:
            continue

        for update in graph.stream({"messages": [HumanMessage(user_input)]}, config, stream_mode="updates"):
            for node, payload in update.items():
                for msg in payload.get("messages", []):
                    if isinstance(msg, AIMessage) and msg.tool_calls:
                        for call in msg.tool_calls:
                            print(f"   🔧 {call['name']}")
                    elif isinstance(msg, ToolMessage):
                        print(f"   ↳ {str(msg.content).splitlines()[0][:100]}")
                    elif isinstance(msg, AIMessage) and node == "agent":
                        print(f"\nAgent > {msg.content}\n")
    print("À bientôt 👋")


if __name__ == "__main__":
    main()
