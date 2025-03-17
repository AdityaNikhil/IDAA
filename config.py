from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import os
import yaml

with open('setup.yml', 'r') as file:
    config = yaml.safe_load(file)

for key, value in config['environment'].items():
    os.environ[key] = value

# LLM Configuration
llm = ChatOpenAI(model='gpt-4o-mini')

# Load prompts
with open("prompts/prompts.yml", "r") as file:
    prompts = yaml.safe_load(file)

# Access the prompts
ANALYST_SYS_PROMPT = prompts["system_prompts"]["analyst_llm"]["description"]
SUPERVISOR_LLM_PROMPT = prompts["system_prompts"]["supervisor_llm"]["description"]
ADVISOR_LLM_PROMPT = prompts["system_prompts"]["advisor_llm"]["description"]
