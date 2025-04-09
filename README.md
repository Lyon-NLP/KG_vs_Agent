# KG_vs_Agent

![image](https://github.com/user-attachments/assets/afd52df9-bb61-4e27-9086-45a458764740)


Talk Lyon Data Science on comparing a Knowledge Graph approach to a Web Agent one. Replay of the talk can be found on [YouTube](https://youtu.be/dnf0Ex-x6Ck), the talk is in French.

## KG-RAG

Initialise the project: 

```
git clone https://github.com/Lyon-NLP/KG_vs_Agent.git
cd KG_vs_Agent
cd kg_rag
python3 -m venv kg_env
source kg_env/bin/active
pip install -r requirements.txt
```

Start the conversational interface on Streamlit: 
```
streamlit run main.py
```

Specify an `.env` file with :
- the LLM model name
- the LLM API key
- the Neo4j graph URL
- the Neo4j graph user
- the Neo4j graph password
- the Neo4j graph database name

## Web Agent

Please check the REDAME in the web_agent folder.
