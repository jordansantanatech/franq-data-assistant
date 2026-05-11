import streamlit as st
from app.agent import run_agent
from app.visualizer import render_chart

st.set_page_config(
    page_title="Assistente de Dados FRANQ",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Assistente Virtual de Dados")
st.caption("Faça perguntas sobre os dados em linguagem natural.")

# Exemplos de perguntas
with st.expander("💡 Exemplos de perguntas"):
    st.markdown("""
    - Liste os 5 estados com maior número de clientes que compraram via app em maio.
    - Quantos clientes interagiram com campanhas de WhatsApp em 2024?
    - Quais categorias de produto tiveram o maior número de compras em média por cliente?
    - Qual o número de reclamações não resolvidas por canal?
    - Qual a tendência de reclamações por canal no último ano?
    """)

# Histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "df" in msg and msg["df"] is not None:
            if msg["chart_type"] == "tabela":
                st.dataframe(msg["df"], use_container_width=True)
            else:
                st.plotly_chart(msg["fig"], use_container_width=True)
        if "steps" in msg:
            with st.expander("🔍 Ver raciocínio do agente"):
                for step in msg["steps"]:
                    st.markdown(f"**{step['role']}**")
                    st.code(step["content"], language="sql" if step["role"] == "SQL" else "markdown")

# Input do usuário
question = st.chat_input("Digite sua pergunta...")

if question:
    # Mostra pergunta do usuário
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # Processa e mostra resposta
    with st.chat_message("assistant"):
        with st.spinner("Analisando os dados..."):
            result = run_agent(question)

        if not result["success"]:
            st.error(f"Não foi possível responder: {result['error']}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Erro: {result['error']}",
            })
        else:
            df = result["df"]
            fig, chart_type = render_chart(question, df)

            # Resumo textual
            st.markdown(f"**{len(df)} registro(s) encontrado(s).**")

            # Visualização
            if chart_type == "tabela" or fig is None:
                st.dataframe(df, use_container_width=True)
            else:
                st.plotly_chart(fig, use_container_width=True)

            # Raciocínio
            with st.expander("🔍 Ver raciocínio do agente"):
                for step in result["steps"]:
                    st.markdown(f"**{step['role']}**")
                    st.code(step["content"], language="sql" if step["role"] == "SQL" else "markdown")

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**{len(df)} registro(s) encontrado(s).**",
                "df": df,
                "fig": fig,
                "chart_type": chart_type,
                "steps": result["steps"],
            })