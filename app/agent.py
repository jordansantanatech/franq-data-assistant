import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.database import get_schema, run_query
import pandas as pd
import re

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0,
)

SYSTEM_PROMPT = """Você é um assistente especialista em análise de dados SQL.
Você tem acesso a um banco de dados SQLite com as seguintes tabelas:

{schema}

INFORMAÇÕES IMPORTANTES SOBRE OS DADOS:
- Datas disponíveis em compras: de 2024-07-22 até 2025-07-22
- Canais de compras: 'App', 'Site', 'Loja Física' (exatamente assim, com maiúscula)
- Canais de marketing: 'WhatsApp', 'E-mail', 'SMS'
- Canais de suporte: 'Chat', 'E-mail', 'Telefone'
- Categorias de produto: 'Serviços', 'Viagens', 'Eletrônicos', 'Livros', 'Roupas', 'Alimentos'
- Formato de datas no banco: YYYY-MM-DD (ex: 2024-07-22)
- Para filtrar mês use: strftime('%m', data_compra) = '05'
- Para filtrar ano use: strftime('%Y', data_compra) = '2024'
- O "último ano" refere-se ao período de 2024-07-22 até 2025-07-22

REGRAS:
- Responda SEMPRE com um bloco SQL válido entre ```sql e ```
- Nunca limite resultados com LIMIT a menos que o usuário peça explicitamente um número
- Se o usuário pedir top 5, use LIMIT 5
- Use apenas tabelas e colunas existentes no schema
- Sempre use GROUP BY quando usar funções de agregação com outras colunas
- Para tendências por canal ao longo do tempo, agrupe por canal E por mês
- Após o bloco SQL, explique brevemente o que a query faz em português
"""

def extract_sql(text: str) -> str | None:
    pattern = r"```sql\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def run_agent(question: str) -> dict:
    schema = get_schema()
    steps = []

    # Passo 1: gerar SQL
    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(schema=schema)),
        HumanMessage(content=question),
    ]

    response = llm.invoke(messages)
    steps.append({"role": "LLM", "content": response.content})

    sql = extract_sql(response.content)

    if not sql:
        return {
            "success": False,
            "error": "Não foi possível gerar uma query SQL.",
            "steps": steps,
            "df": None,
        }

    # Passo 2: executar SQL (com auto-correção)
    max_attempts = 3
    df = None
    last_error = None

    for attempt in range(max_attempts):
        try:
            df = run_query(sql)
            steps.append({"role": "SQL", "content": sql})
            break
        except Exception as e:
            last_error = str(e)
            steps.append({"role": "Erro", "content": f"Tentativa {attempt+1}: {last_error}"})

            # Pede pro LLM corrigir
            fix_messages = messages + [
                {"role": "assistant", "content": response.content},
                HumanMessage(content=f"A query gerou o erro: {last_error}. Corrija o SQL."),
            ]
            response = llm.invoke(fix_messages)
            sql = extract_sql(response.content)
            steps.append({"role": "LLM (correção)", "content": response.content})

            if not sql:
                break

    if df is None:
        return {
            "success": False,
            "error": last_error,
            "steps": steps,
            "df": None,
        }

    return {
        "success": True,
        "df": df,
        "sql": sql,
        "steps": steps,
        "llm_explanation": response.content,
    }