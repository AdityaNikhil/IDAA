from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import os
import yaml

def create_default_setup():
    """Create a default setup.yml file with empty values."""
    default_config = {
        "environment": {
            "LANGSMITH_TRACING_V2": "true",
            "LANGCHAIN_ENDPOINT": "https://api.smith.langchain.com",
            "LANGSMITH_API_KEY": "",
            "TAVILY_API_KEY": "",
            "GROQ_API_KEY": "",
            "OPENAI_API_KEY": "",
            "DATABASE_URI": "postgresql://postgres:postgres@localhost:5432/postgres"
        }
    }
    
    try:
        with open('setup.yml', 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)
        print("\nCreated setup.yml with default configuration.")
        print("Please update the following API keys in setup.yml:")
        print("- LANGSMITH_API_KEY")
        print("- TAVILY_API_KEY")
        print("- GROQ_API_KEY")
        print("- OPENAI_API_KEY")
        print("\nYou can get these API keys from their respective platforms:")
        print("- LangSmith: https://smith.langchain.com/")
        print("- Tavily: https://tavily.com/")
        print("- Groq: https://console.groq.com/")
        print("- OpenAI: https://platform.openai.com/")
        return True
    except Exception as e:
        print(f"Error creating setup.yml: {str(e)}")
        return False

def validate_environment_vars(config):
    """Validate environment variables and prompt for missing values."""
    missing_vars = []
    for key, value in config['environment'].items():
        if not value and key != "LANGCHAIN_ENDPOINT" and key != "DATABASE_URI":
            missing_vars.append(key)
    
    if missing_vars:
        print("\nMissing required API keys in setup.yml:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease update these values in setup.yml before continuing.")
        return False
    return True

def load_config():
    """Load configuration from setup.yml and validate environment variables."""
    # First check if setup.yml exists
    if not os.path.exists('setup.yml'):
        if not create_default_setup():
            raise FileNotFoundError("Failed to create setup.yml")
        raise ValueError("Please configure your API keys in setup.yml before continuing.")

    # Load the configuration
    try:
        with open('setup.yml', 'r') as file:
            config = yaml.safe_load(file)
    except Exception as e:
        raise Exception(f"Error reading setup.yml: {str(e)}")

    # Validate environment variables
    if not validate_environment_vars(config):
        raise ValueError("Missing required API keys in setup.yml")

    # Set environment variables
    for key, value in config['environment'].items():
        os.environ[key] = str(value)

    return config

# Load configuration when module is imported
config = load_config()

# LLM Configuration
llm = ChatOpenAI(model='gpt-4o-mini')

# Load prompts
with open("prompts/prompts.yml", "r") as file:
    prompts = yaml.safe_load(file)

# Access the prompts
ANALYST_SYS_PROMPT = prompts["system_prompts"]["analyst_llm"]["description"]
SUPERVISOR_LLM_PROMPT = prompts["system_prompts"]["supervisor_llm"]["description"]
ADVISOR_LLM_PROMPT = prompts["system_prompts"]["advisor_llm"]["description"]
