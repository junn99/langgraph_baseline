import asyncio
from dotenv import load_dotenv
import os

from mcp import ClientSession, StdioServerParameters

# ClientSession : 프로그램이 mcp 클라이언트 역할을 할 수 있는 프레임워크 제공
# mcp 서버에 연결, 메시지 교환, 사용자 정의, 콜백 등을 통해 서버 요청 및 알람에 반응
# 서버와 클라이언트는 1:1 연결 -> 그래서? 클라이언트를 초기화할 때 데이터를 읽고 쓰는 방법을 알려줘야 함.
# StdioServerParameters : mcp 서버를 실행하는 방법을 나타내는 명령 및 args 필드가 있는 클래스
from mcp.client.stdio import stdio_client

# 입출력의 전송을 통해 mcp 서버와 통신하는 객체
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.tools import load_mcp_tools

# mcp 서버를 통해 노출되고 mcp 객체인 도구를 랭체인 도구로 변환해줌
from langgraph.prebuilt import create_react_agent

# 사전 구축된 에이전트 구현체
# 도구를 올바르게 불러오게하는 오케스터라고 생각하면 됨
from langchain_core.messages import HumanMessage


load_dotenv()

# LLM Instantiation
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite-preview-06-17",
    temperature=0,
    max_retries=2,  # 최대 2번 재시도
    api_key=os.getenv("GOOGLE_API_KEY"),
)


stdio_server_params = StdioServerParameters(
    command="python",
    args=[
        "C:\\cursor\\DealMakers\\langgraph_baseline\\notebook\\server\\math_server.py"
    ],  # 웹 서버 파일의 절대 경로
)


async def main():
    print("Starting MCP server...")
    async with stdio_client(stdio_server_params) as (read, write):
        # 모든 클라이언트가 세션을 통해 서버에 연결하기 때문에 클라이언트 세션 작성
        async with ClientSession(read_stream=read, write_stream=write) as session:
            # 이 mcp 클라이언트 세션이 객체는 클라이언트 서버와 통신을 담당 -> 그닥 알 필욘 없음
            await session.initialize()
            print("session initialized")

            # 확인용(테스트)
            # 클라이언트가 보유한 모든 도구 나열
            # tools = await session.list_tools()
            # print(tools)

            tools = await load_mcp_tools(session)
            print(tools)

            # Host 생성
            agent = create_react_agent(llm, tools)

            # result = await agent.ainvoke({"messages": "What is 2 + 2?"})
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content="What is 54 + 2 * 3?")]}
            )
            # 딱히 차이가 없는데?
            print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
