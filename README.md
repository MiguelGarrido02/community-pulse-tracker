# Open Source Communities Sentiment Tracking

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![Snowflake](https://img.shields.io/badge/Snowflake-Data_Cloud-29B5E8?logo=snowflake&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-Transform-FF694B?logo=dbt&logoColor=white)
![LangChain](https://img.shields.io/badge/AI-LangChain-1C3C3C?logo=langchain&logoColor=white)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit&logoColor=white)

An End-to-End Data Engineering Project that analyzes the "health" and sentiment of Open Source communities (like Pandas, dbt, Prefect) by processing thousands of GitHub Issues using **Snowflake Cortex (AI)** and serving insights via a **Power BI Dashboard** and an **AI-powered Chatbot**.

**Core Value Proposition:**
This project democratizes data access. By syncing a powerful Data Warehouse with an LLM, **users don't need technical skills or SQL knowledge**. They can query complex datasets using natural language, effectively using the AI as an on-demand Data Analyst.

#### For demonstration, all the issues from the repositories *dbt-core, pandas, prefect, and streamlit* that had been created or updated on the year 2025 have been extracted.
---

## Architecture

```mermaid
graph LR
    A[GitHub API] -->|"Extract Python Async"| B(Snowflake RAW)
    B -->|"Transform & Clean"| C{dbt Core}
    C -->|"Sentiment Analysis"| D[Snowflake Cortex LLM]
    D -->|"Data Marts"| E(FCT_ISSUES_SENTIMENT)
    
    E -->|Viz| F[Power BI Dashboard]
    E -->|"RAG / Chat"| G[Streamlit + LangChain AI]
```
---
##  Key Features

* **Highly Modular & Decoupled:** The architecture separates Extraction, Storage, and Logic. You can swap the data source (GitHub) for any other API without breaking the downstream transformation or AI layers.
* **Universal Sentiment Engine:** The Snowflake Cortex implementation is **source-agnostic**. It works equally well for analyzing **Customer Reviews**, Support Tickets, or Social Media posts.
* **Extraction:** Asynchronous Python script hitting GitHub API with rate-limit handling.
* **Storage:** Scalable storage in **Snowflake** (Raw & Analytics layers).
* **Transformation:** Modular data modeling with **dbt** (Data Build Tool).
* **Interactive Chatbot:** A "Chat with your Data" app built with **Streamlit** and **LangChain**, featuring memory context and SQL generation.
* **Security:** Role-Based Access Control (RBAC) implementation for the chatbot user.
---
## Screenshots
### 1. The AI Analyst (Chat with Data)
<img width="1907" height="852" alt="imggithub1" src="https://github.com/user-attachments/assets/c2815b08-7061-4053-951e-a15ad84e4e4d" />
<img width="1896" height="880" alt="imggithub2" src="https://github.com/user-attachments/assets/d2a92de2-a31b-4203-9048-bfaf9463b181" />
<img width="1133" height="502" alt="githubimg3" src="https://github.com/user-attachments/assets/ad2698f8-c44a-4083-a3ca-a89799d614f0" />

### 2. Community Health Dashboard
<img width="291" height="189" alt="image" src="https://github.com/user-attachments/assets/0f267637-f654-4a7b-b5a4-74d4581ecf7f" />
<img width="293" height="185" alt="image" src="https://github.com/user-attachments/assets/874aced3-e1bc-4372-b90c-846178abc64a" />
<img width="788" height="403" alt="image" src="https://github.com/user-attachments/assets/b7ccfe96-1899-411d-8e6f-8ba17c94ba1c" />
<img width="1014" height="415" alt="image" src="https://github.com/user-attachments/assets/d1129d53-953d-4f43-a7ca-4e9bf92ad91b" />

---
## Tech Stack
* Ingestion: Python (requests)
* Warehouse: Snowflake (Data Cloud)
* Transformation: dbt Core
* AI/ML: Snowflake Cortex (Sentiment), OpenAI GPT-4o (Reasoning Agent)
* Orchestration: LangChain (SQLDatabaseChain)
* Frontend: Streamlit
---
## How to Run Locally
**1. Clone repo**
``` bash
git clone https://github.com/MiguelGarrido02/community-pulse-tracker.git
cd community_pulse_tracker
```
**2. Install dependencies**
``` bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
**3. Set up environment variables.** 
Create .env file with your credentials (see .env.example for the complete list of env variables)
``` Ini, TOML
SNOWFLAKE_USER=...
OPENAI_API_KEY=...
GITHUB_TOKEN=...
```
**4. Run the Ingestion Pipeline (Extract & Load)**
Fetch raw data from the GitHub API and load it into Snowflake (Raw Layer).
```bash
# Adjust the path to your main extraction script
python extraction/main.py 
```
**5. Run Transformations (dbt)**
Transform raw data, apply Sentiment Analysis (Cortex), and build Data Marts.
```bash
cd transformation  # Go to your dbt project folder
dbt deps           # Install dbt dependencies
dbt build          # Run seeds, models, snapshots, and tests
cd ..              # Go back to root
```
**6. Run the Chatbot**
Launch the Streamlit app to interact with the processed data.
```bash
streamlit run chatbot.py
```
