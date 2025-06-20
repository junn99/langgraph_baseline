"""
해당 서버 각각에 대해
클라이언트를 명시적으로 작성하지 않아도
여러 MCP 서버에 쉽게 연결하는 데 사용 가능
"""

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_retries=2,  # 최대 2번 재시도
)


async def main():
    print("hello langcahin mcp")
    # -------------------Legacy code-------------------
    # async with MultiServerMCPClient(
    #     {
    #         "math": {
    #             "command": "python",
    #             "args": [
    #                 "C:\\cursor\\DealMakers\\langgraph_baseline\\notebook\\server\\math_server.py"
    #             ],
    #         },
    #         "weather": {
    #             "url" : "http://localhost:8000/sse",
    #             "transport" : "sse",
    #         },
    #     }
    # ) as client:
        
    #     agent = create_react_agent(llm, client.get_tools())
    #     result = await agent.ainvoke({"messages": "What is 54 + 2 * 3?"})
    #     print(result["messages"][-1].content)
    # -------------------Legacy code-------------------


    # client = MultiServerMCPClient(
    #     {
    #         "math": {
    #             "command": "python",
    #             "args": [
    #                 "C:\\cursor\\DealMakers\\langgraph_baseline\\notebook\\server\\math_server.py"
    #             ],
    #             "transport" : "stdio",
    #         },
    #         "weather": {
    #             "url" : "http://localhost:8000/sse",
    #             "transport" : "sse",
    #         },
    #     }
    # )
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": [
                    "C:\\cursor\\DealMakers\\langgraph_baseline\\notebook\\server\\math_server.py"
                ],
                "transport" : "stdio",
            },
            "weather": {
                "url" : "http://localhost:8005/sse",
                "transport" : "sse",
            },
        }
    )
    
    tools = await client.get_tools()
    agent = create_react_agent(llm, tools)
    # result = await agent.ainvoke({"messages": "What is 54 + 2 * 3?"})
    # result = await agent.ainvoke({"messages": "What is the weather in Tokyo?"})
    result = await agent.ainvoke({"messages": "retrieve 도구를 활용해서 Fine-tuning based learning에 대해 알려줘"})
    print(result["messages"][-1].content)



if __name__ == "__main__":
    asyncio.run(main())
