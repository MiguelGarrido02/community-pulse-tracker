import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

# load environment variables from .env file
load_dotenv()

# streamlit app title and description
st.set_page_config(page_title="Community Pulse AI", page_icon="🤖")
st.title("🤖 Track Open Source Community Issues and Sentiment")
st.markdown("Ask whatever you want about open source community issues and sentiment data stored in Snowflake!")

# Snowflake connection
user = os.getenv("SNOWFLAKE_CHATBOT_USER")
password = os.getenv("SNOWFLAKE_CHATBOT_PASSWORD")
account = os.getenv("SNOWFLAKE_ACCOUNT")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
database = os.getenv("SNOWFLAKE_DATABASE")
schema = os.getenv("SNOWFLAKE_CHATBOT_SCHEMA")
role = os.getenv("SNOWFLAKE_CHATBOT_ROLE")

# connection url string
snowflake_url = f"snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role={role}"


# init langchain agent with Snowflake
@st.cache_resource # this will cache the agent between interactions
def get_agent():
    try:
        # connect to snowflake's db
        db = SQLDatabase.from_uri(snowflake_url)
        
        # define LLM model
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # create SQL agent
        agent_executor = create_sql_agent(
            llm=llm,
            db=db,
            agent_type="openai-tools",
            verbose=True #check logs for debugging
        )
        return agent_executor
    except Exception as e:
        st.error(f"Error while connecting to Snowflake: {e}")
        return None

agent = get_agent()

# chat interface with message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# show chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



def get_conversation_string():
    conversation_string = ""
    # get last 4 messages for context
    for message in st.session_state.messages[-4:]:
        role = message["role"]
        content = message["content"]
        conversation_string += f"{role}: {content}\n"
    return conversation_string

# get user input and process
if prompt := st.chat_input("Ej: Which open source projects...?"):
    
    # save and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. build the question with context from history
    history_text = get_conversation_string()

    # build final prompt with conversation history    
    final_prompt = (
        f"I need you to answer the user's QUESTION based on the following CONVERSATION_HISTORY.\n\n"
        f"CONVERSATION_HISTORY:\n{history_text}\n\n"
        f"QUESTION: {prompt}\n\n"
        f"Important: If the question refers to previous data (like 'show me this in days'), "
        f"use the logic from the previous query but modify it."
    )

    # ai response
    with st.chat_message("assistant"):
        if agent:
            with st.spinner("Let me think..."):
                try:
                    # send final prompt but show only the user prompt in history
                    response = agent.invoke(final_prompt)
                    output_text = response["output"]
                    st.markdown(output_text)
                    
                    # save ai response to session state
                    st.session_state.messages.append({"role": "assistant", "content": output_text})
                except Exception as e:
                    st.error(f"Whoops something went wrong: {e}")