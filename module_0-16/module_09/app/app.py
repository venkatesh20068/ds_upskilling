"""Module 9 mini application: a single agent built with LangGraph over
a local llama3.1 model via Ollama.

Models the agent loop (Perceive -> Think -> Act -> Observe) as an
explicit graph, instead of a fixed chain (Module 8) or a hidden loop
inside a library's AgentExecutor:

    [agent] --tool call requested?--> yes --> [tools] --> back to [agent]
                                    --> no  --> END

The number of loop iterations is decided by the model at runtime, not
fixed in code - unlike Module 8's always-exactly-two-steps chain. This
is the actual distinguishing feature of an "agent" versus a "chain,"
and is why the two example questions below take a different number of
steps to answer.

Run:
    python app.py
"""

import sys

from langchain_ollama import ChatOllama
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from calculator_tool import calculate

sys.stdout.reconfigure(encoding="utf-8")  # llama3.1 output may include Unicode the console codepage can't render

TOOLS = [calculate]

llm = ChatOllama(model="llama3.1", temperature=0.3).bind_tools(TOOLS)


def call_model(state: MessagesState) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}


def build_agent():
    graph = StateGraph(MessagesState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


QUESTIONS = [
    "What is 847 times 293?",
    "What is the capital of France?",
]


def ask(agent, question: str) -> None:
    print(f"\n{'=' * 70}\nQ: {question}")

    result = agent.invoke({"messages": [("user", question)]})
    steps = result["messages"][1:]  # everything after the initial human message

    for message in steps:
        if type(message).__name__ == "AIMessage" and message.tool_calls:
            for call in message.tool_calls:
                print(f"  [agent] -> tool call: {call['name']}({call['args']})")
        elif type(message).__name__ == "ToolMessage":
            print(f"  [tools] -> result: {message.content}")
        else:
            print(f"  [agent] -> final answer: {message.content}")

    print(f"({len(steps)} step{'s' if len(steps) != 1 else ''} in the loop)")


def main() -> None:
    agent = build_agent()
    for question in QUESTIONS:
        ask(agent, question)


if __name__ == "__main__":
    main()
