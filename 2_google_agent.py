from dotenv import load_dotenv
load_dotenv()

from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver


model = ChatGroq(model="openai/gpt-oss-20b")
search = GoogleSerperAPIWrapper()
memory = MemorySaver()

agent = create_agent(
    model=model,
    tools=[search.run],
    checkpointer=memory,
    system_prompt="You are a helpful assistant that can answer questions using Google Search.")


while True:
    query = input("user: ")
    if query.lower() == "exit":
        print("Goodbye!")
        break
    
    response = agent.invoke({"messages": [{"role": "user", "content": query}]},
                            {"configurable": {"thread_id": "1"}},
                            )
    
    print("Ai: ", response["messages"][-1].content) 