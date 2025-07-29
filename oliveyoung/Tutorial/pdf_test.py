import os
from typing import TypedDict, Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
load_dotenv()

os.environ["TAVILY_API_KEY"] = "1gp11HnQdTjyvK2w8ZbQEQoGZnYh1ErX"

# 1. 상태(State) 정의
# Agent가 실행되는 동안 관리할 데이터의 구조를 정의합니다.
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. 도구(Tool) 및 모델(LLM) 정의
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

# 모델을 도구에 바인딩
llm_with_tools = llm.bind_tools(tools)

# 3. 노드(Node) 함수 정의

# (1) Agent: LLM을 호출하여 어떤 도구를 사용할지 결정하는 노드
def agent_node(state: State):
    print("---AGENT 노드 실행---")
    # PDB 디버깅 지점을 여기에 추가합니다! ############################
    # import pdb; pdb.set_trace()
    ################################################################
    breakpoint()
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# (2) Tool: 실제로 도구를 실행하는 노드
# LangGraph에서 미리 만들어 둔 ToolNode를 사용합니다.
tool_node = ToolNode(tools=[tool])

# 4. 엣지(Edge) 로직 정의
# Agent 노드 실행 후, LLM의 응답에 tool_calls가 있는지 확인하여 다음 단계를 결정합니다.
def should_continue(state: State) -> str:
    print("---엣지 로직 실행 (should_continue)---")
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        # LLM이 도구 사용을 결정했다면 tool_node로 이동
        return "tools"
    # 도구 사용이 필요 없으면 종료
    return "end"

# 5. 그래프(Graph) 생성
graph = StateGraph(State)

graph.add_node("agent", agent_node) # Agent 노드 추가
graph.add_node("tools", tool_node) # Tool 노드 추가

graph.set_entry_point("agent") # 시작점을 agent로 설정

# 조건부 엣지 추가
graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": "__end__"
    }
)

# Tool 노드 실행 후에는 다시 agent 노드로 돌아가도록 설정
graph.add_edge("tools", "agent")

# 6. 그래프 컴파일 및 실행
app = graph.compile()

# "What's the weather in SF?" 라는 질문으로 그래프 실행
inputs = {"messages": [("user", "What's the weather in SF?")]}
for event in app.stream(inputs, stream_mode="values"):
    event["messages"][-1].pretty_print()