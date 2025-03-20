# Intelligent Digital Assets Assistant (IDAA)

[![pages-build-deployment](https://github.com/adityanikhil/IDAA/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/adityanikhil/IDAA/actions/workflows/pages/pages-build-deployment)

<p align="center">
    <img src="assets/architecture.png" width="700" alt="Thumbnail">
</p>
<p align="center">
    <a href="playground.ipynb"><em>Demo Notebook</em></a> |
    <a href="https://youtu.be/fR2ar-ChBDY"><em>React Demo</em></a> |
    <a href="https://www.youtube.com/watch?v=77j7a_dnGb4&ab_channel=AdityaNikhil"><em>Streamlit Demo</em></a>
</p>

> [!NOTE]
> 🚧 **This repository features a React frontend. If you need a Streamlit frontend, visit the [Streamlit version](https://github.com/AdityaNikhil/IDAA-Streamlit-App).**

---
## Table of Contents
1. [Overview](#overview)
2. [Approach](#approach)
3. [Setup](#setup)
4. [Getting Started](#getting-started)
5. [License](#license)
6. [Contributors](#contributors)

---
## Overview
The **Intelligent Digital Asset Advisor (IDAA)** is an AI-powered financial advisory system integrating three core functions:
- **Professor:** Provides educational insights on digital assets.
- **Analyst:** Processes market and on-chain data for analytics.
- **Advisor:** Offers strategic financial guidance.

Built using **GPT-4, LLAMA 3.3, and RAG**, IDAA delivers real-time, informed, and personalized digital asset recommendations. The system orchestrates these components seamlessly, ensuring accurate and timely financial insights.

---
## Approach

<p align="center">
  <img src="assets/mermaid.png" width="500" alt="System Workflow">
</p>

### System Workflow
1. **User Query Handling**: Queries are routed to the appropriate agent via the **supervisor node**.
2. **Analyst Agent**: Queries PostgreSQL for historical market data.
3. **Advisor Agent**: Uses Pinecone vector DB for trading insights.
4. **Professor Agent**: Gathers real-time educational content.
5. **Query Processing**:
    - Analyst queries PostgreSQL and generates insights.
    - Advisor applies **RAG operations** for recommendations.
    - Professor fetches relevant educational materials.

This modular approach ensures a well-rounded financial advisory experience.

---
## Setup

> [!IMPORTANT]
> **Ensure the ETL pipeline is configured and PostgreSQL data is loaded before proceeding.**
> Refer to the [ETL setup](etl/) for more details.

### Prerequisites
- **PostgreSQL Database**: Ensure historical data is loaded.
- **API Keys**: Obtain keys from **Langsmith, Groq, OpenAI, TavilySearch**.

### Installation
Clone the repository:
```sh
git clone https://github.com/adityanikhil/idaa
cd idaa
```

### Configure Environment Variables
Create `setup.yml` and add your API keys:
```yaml
environment:
  LANGSMITH_TRACING_V2: "true"
  LANGCHAIN_ENDPOINT: "https://api.smith.langchain.com"
  LANGSMITH_API_KEY: "YOUR_API_KEY"
  TAVILY_API_KEY: "YOUR_API_KEY"
  GROQ_API_KEY: "YOUR_API_KEY"
  OPENAI_API_KEY: "YOUR_API_KEY"
  DATABASE_URI: "postgresql://postgres:postgres@localhost:5432/postgres"
```

---
## Getting Started
### Deploying the FastAPI Backend
#### 1. Build the API Service
```sh
docker build -f Dockerfile.api -t api-service .
```
#### 2. Run the API Service
```sh
docker run -p 8000:8000 api-service
```
#### 3. Access the API
```sh
http://localhost:8000/docs
```

### Running the React Frontend
1. Clone the [frontend repo](https://github.com/yolandawu/IDAA-FN):
    ```sh
    git clone https://github.com/yolandawu/IDAA-FN
    cd IDAA-FN
    ```
2. Install dependencies:
    ```sh
    npm install
    ```
3. Configure API endpoint in `.env`:
    ```sh
    REACT_APP_BACKEND_URL=http://localhost:8000
    ```
4. Start the React server:
    ```sh
    npm run dev
    ```
5. Open your browser at [http://localhost:3000](http://localhost:3000).

For additional frontend setup options, check [this guide](https://github.com/yolandawu/IDAA-FN?tab=readme-ov-file#deployment).

> [!NOTE]
> 🚧 **Need a Streamlit frontend?** Visit the [Streamlit version](https://github.com/AdityaNikhil/IDAA-Streamlit-App).

---
## License
This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---
## Contributors
- **[Aditya Nikhil Digala](https://linkedin.com/in/aditya-nikhil)**
- **[Yang Wu](https://www.linkedin.com/in/yangywu/)**
- **[Vaeshnavi Vella](https://www.linkedin.com/in/vaeshnavi-vella/)**
