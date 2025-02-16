import os
import yaml

# Construct the path to setup.yml dynamically
config_path = os.path.join(os.path.dirname(__file__), "setup.yml")

# Load the configuration from the YAML file
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# Extract prompts
SUPERVISOR_LLM_PROMPT = config.get("SUPERVISOR_LLM_PROMPT", "Default Supervisor Prompt")
ANALYST_SYS_PROMPT = config.get("ANALYST_SYS_PROMPT", "Default Analyst Prompt")
EDUCATE_SYS_PROMPT = config.get("EDUCATE_SYS_PROMPT", "Default Educate Prompt")
ADVISOR_SYS_PROMPT = config.get("ADVISOR_SYS_PROMPT", "Default Advisor Prompt")

# Extract database credentials
DATABASE_URI = config.get("DATABASE_URI", "")

print("Configuration loaded successfully!")