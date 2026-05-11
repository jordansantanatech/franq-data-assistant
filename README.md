# 🤖 Assistente Virtual de Dados — FRANQ

Assistente inteligente capaz de responder perguntas de negócio em linguagem natural, consultando um banco de dados SQLite e apresentando os resultados visualmente de forma automática.

---

## 🏗️ Arquitetura

```
Usuário (linguagem natural)
        ↓
  Streamlit (interface)
        ↓
   Agent (LangChain)
        ↓
  LLM Groq LLaMA 3.3 70b
        ↓
  Geração de SQL
        ↓
  Execução no SQLite
        ↓ (erro?)
  Auto-correção (até 3 tentativas)
        ↓
  Visualizer (tabela / barra / linha / pizza)
        ↓
  Resposta + Raciocínio exibidos
```

### Componentes

| Arquivo | Responsabilidade |
|---|---|
| `app/database.py` | Conexão com SQLite, leitura de schema, execução de queries |
| `app/agent.py` | Agente LangChain, geração e auto-correção de SQL |
| `app/visualizer.py` | Decisão e renderização do tipo de gráfico |
| `streamlit_app.py` | Interface de chat com histórico e painel de raciocínio |

---

## ⚙️ Como executar

### Pré-requisitos
- Python 3.11+
- Chave de API do [Groq](https://console.groq.com) (gratuita)

### Instalação

```bash
git clone https://github.com/jordansantanatech/franq-data-assistant
cd franq-data-assistant
pip install -r requirements.txt
```

### Configuração

```bash
cp .env.example .env
# Edite o .env e adicione sua chave:
# GROQ_API_KEY=sua_chave_aqui
```

### Execução

```bash
streamlit run streamlit_app.py
```

---

## 🧠 Fluxo do Agente

1. **Descoberta dinâmica do schema** — o agente lê as tabelas e colunas do banco automaticamente, sem queries hardcoded
2. **Geração de SQL** — o LLM recebe o schema e a pergunta do usuário e gera a query adequada
3. **Execução com auto-correção** — se a query falhar, o erro é enviado de volta ao LLM que tenta corrigir (até 3 tentativas)
4. **Decisão de visualização** — um segundo prompt decide se o resultado deve ser exibido como tabela, gráfico de barras, linha ou pizza
5. **Transparência** — todas as queries e passos intermediários ficam disponíveis no painel "Ver raciocínio do agente"

---

## 💬 Exemplos de consultas testadas

| Pergunta | Resultado | Visualização |
|---|---|---|
| Liste os 5 estados com maior número de clientes que compraram via app em maio | SP, SC, PR, MG, ES | Tabela |
| Quantos clientes interagiram com campanhas de WhatsApp em 2024? | 17 clientes | Tabela |
| Quais categorias de produto tiveram o maior número de compras em média por cliente? | 6 categorias ordenadas | Gráfico de barras |
| Qual o número de reclamações não resolvidas por canal? | Chat, E-mail, Telefone | Gráfico de barras |
| Qual a tendência de reclamações por canal no último ano? | Jul/2024 a Jul/2025 | Gráfico de linha |

---

## 🚀 Sugestões de melhorias

- **Memória de conversa** — manter contexto entre perguntas para perguntas de follow-up
- **Cache de queries** — armazenar resultados de perguntas frequentes para reduzir latência
- **Autenticação** — controle de acesso para ambientes corporativos
- **Suporte a múltiplos bancos** — PostgreSQL, BigQuery, etc.
- **Exportação de resultados** — download dos dados em CSV ou PDF
- **Feedback do usuário** — botão de "resposta útil" para fine-tuning futuro

---

## 🛠️ Stack

- [Python 3.11](https://python.org)
- [LangChain](https://langchain.com)
- [Groq LLaMA 3.3 70b](https://groq.com)
- [SQLite](https://sqlite.org)
- [Streamlit](https://streamlit.io)
- [Plotly](https://plotly.com)
