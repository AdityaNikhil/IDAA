from langchain_groq import ChatGroq
import os
import yaml

with open('setup.yml', 'r') as file:
    config = yaml.safe_load(file)

for key, value in config['environment'].items():
    os.environ[key] = value

# LLM Configuration
llm = ChatGroq(model_name="llama3-70b-8192")

# Load prompts
with open("prompts/prompts.yml", "r") as file:
    prompts = yaml.safe_load(file)

# Access the prompts
EDUCATE_SYS_PROMPT = prompts["system_prompts"]["educate_llm"]["description"]
ANALYST_SYS_PROMPT = prompts["system_prompts"]["analyst_llm"]["description"]
SUPERVISOR_LLM_PROMPT = prompts["system_prompts"]["supervisor_llm"]["description"]
