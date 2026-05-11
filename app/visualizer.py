import pandas as pd
import plotly.express as px
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0,
)

VIZ_PROMPT = """Você decide como visualizar dados retornados de uma query SQL.
Responda com APENAS uma dessas palavras, sem explicação:
- tabela → para listas, contagens simples, dados detalhados
- barra → para comparações entre categorias
- linha → para tendências ao longo do tempo
- pizza → para proporções/percentuais

Pergunta do usuário: {question}
Colunas disponíveis: {columns}
"""


def decide_chart_type(question: str, df: pd.DataFrame) -> str:
    columns = list(df.columns)
    response = llm.invoke([
        HumanMessage(content=VIZ_PROMPT.format(
            question=question,
            columns=columns
        ))
    ])
    chart = response.content.strip().lower()
    valid = ["tabela", "barra", "linha", "pizza"]
    return chart if chart in valid else "tabela"


def render_chart(question: str, df: pd.DataFrame):
    if df is None or df.empty:
        return None, "tabela"

    chart_type = decide_chart_type(question, df)
    cols = list(df.columns)

    # Identifica colunas numéricas e categóricas
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    text_cols = df.select_dtypes(exclude="number").columns.tolist()

    if chart_type == "barra" and len(numeric_cols) >= 1 and len(text_cols) >= 1:
        fig = px.bar(
            df,
            x=text_cols[0],
            y=numeric_cols[0],
            title="Resultado",
            color=text_cols[0],
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        return fig, chart_type

    elif chart_type == "linha" and len(numeric_cols) >= 1:
        x_col = text_cols[0] if text_cols else cols[0]
        y_col = numeric_cols[0]
        color_col = text_cols[1] if len(text_cols) > 1 else None
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title="Tendência",
            markers=True
        )
        return fig, chart_type

    elif chart_type == "pizza" and len(numeric_cols) >= 1 and len(text_cols) >= 1:
        fig = px.pie(
            df,
            names=text_cols[0],
            values=numeric_cols[0],
            title="Distribuição"
        )
        return fig, chart_type

    return None, "tabela"