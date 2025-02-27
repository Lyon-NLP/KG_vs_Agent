from service import KGRAG

import streamlit as st

kg_rag = KGRAG()

prompt = st.chat_input("Posez votre question")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    res = kg_rag.run(prompt)
    with st.chat_message("assistant"):
        st.write(res["answer"])
    print(f"\n\n### QUESTION ###\n{prompt}")
    print(f"\n\n### QUERY ###\n{res['llm_query']}")
    print(f"\n\n### EXTRACTED CONTEXT ###\n{res['context']}")
    print(f"\n\n### ANSWER ###\n{res['answer']}")
    print(
        f"\n\n### ENVIRONMENTAL IMPACT###\n{res['env_impacts'][0]['name']}: {res['env_impacts'][0]['value']} {res['env_impacts'][0]['unit']}\n{res['env_impacts'][1]['name']}: {res['env_impacts'][1]['value']} {res['env_impacts'][1]['unit']}"
    )
