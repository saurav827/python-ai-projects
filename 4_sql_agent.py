from dotenv import load_dotenv
load_dotenv()

### Db, llm, tools, system prompt, create agent
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver 
from langchain.agents import create_agent
import streamlit as st 


db = SQLDatabase.from_uri("sqlite:///my_task.db")

db.run("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed')) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

## llm, tools, memory, system prompt
model=ChatGroq(model="openai/gpt-oss-20b")
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()



system_prompt = """
You are a task management assistant that interacts with a SQL database containing a 'tasks' table.
    
TASK RULES:
1. Limit SELECT queries to 10 results maximum with ODER BY created_at DESC.
2. After CREATED/UPDATE/DELETE, confrim with SELECT query.
3. If the user requests a list of task, present the output in a strutured table fromat to ensure a clean organized display in th brower."

CRUD OPRATIONS:
   CREATE: INSERT INTO tasks(title, discription, status) 
   READ: SELECT * FROM tasks WHERE ... LIMIT 10
   UPDATE: UPDATE tasks SET status=? WHERE id=? OR title=?
   DELETE: DELETE FROM tasks WHERE id=? OR title=?
   
Table schema: id, title, discription, status(pending/in_progress/completed)l, created_at.
"""  

@st.cache_resource
def get_agent():
    agent = create_agent(
        model=model,
        tools=tools,
        checkpointer=InMemorySaver(),
        system_prompt=system_prompt
    )
    return agent

agent = get_agent()
     
st.subheader("📓 TaskBot - Manage Your Tasks")

if "messages" not in st.session_state:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])
    
prompt = st.chat_input("Ask me to manage your tasks ?")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role":"user", "content":prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("processing..."):
            response = agent.invoke(
            {"messages":[{"role":"user", "content":prompt}]},
            {"configurable":{"thread_id":"1"}}
            )
    
    result = response["messages"][-1].content 
    st.markdown(result)
    st.session_state.messages.append({"role":"assistant", "content":result})