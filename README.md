# Setup

The following files need to be setup before building our docker file.

### 1. `.env`
```python
DATABASE_URI=<PATH_TO_YOUR_POSTGRES_DB>
```

### 2. `setup.yml`
```python
environment:
  LANGSMITH_TRACING_V2: "true"
  LANGCHAIN_ENDPOINT: "https://api.smith.langchain.com"
  LANGSMITH_ENDPOINT: "https://api.smith.langchain.com"
  LANGSMITH_API_KEY: "YOUR_API_KEY"
  LANGSMITH_PROJECT: "PROJECT-NAME"
  GROQ_API_KEY: "YOUR_API_KEY"
  DATABASE_URI: "DATABASE_URI"
```


# Docker building

Now that the files have been setup. Simply run, 

```python
docker compose up --build
```

You will find your streamlit app running at: 
```python
localhost:8501
```

And also you can find the agent's fast API endpoints at:
```python 
localhost:8000/docs
```
