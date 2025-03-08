from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import os
import yaml
import streamlit as st

with open('setup.yml', 'r') as file:
    config = yaml.safe_load(file)

for key, value in config['environment'].items():
    os.environ[key] = value

# LLM Configuration
def get_llm_model():
    # Default model if nothing is selected
    selected_model = st.session_state.get("selected_model", "gpt-4o-mini")
    
    if selected_model == "gpt-4o-mini":
        return ChatOpenAI(model='gpt-4o-mini')
    return ChatGroq(model='llama3-70b-8192')  # Fallback

llm = get_llm_model()

# Load prompts
with open("prompts/prompts.yml", "r") as file:
    prompts = yaml.safe_load(file)

# Access the prompts
ANALYST_SYS_PROMPT = prompts["system_prompts"]["analyst_llm"]["description"]
SUPERVISOR_LLM_PROMPT = prompts["system_prompts"]["supervisor_llm"]["description"]
