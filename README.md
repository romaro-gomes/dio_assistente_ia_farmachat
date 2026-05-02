# 💊 FarmaChat — Assistente de Legislação Farmacêutica

> Projeto de conclusão do **Bootcamp de IA – DIO + Afya**  
> Desenvolvido por Romario | Farmacêutico & Entusiasta de IA

---

## 📖 Sobre o Projeto

O **FarmaChat** nasceu de uma necessidade real: farmacêuticos que atuam em drogarias frequentemente precisam tirar dúvidas rápidas sobre legislação farmacêutica no meio da correria do dia a dia — e nem sempre há tempo para consultar manualmente portarias, RDCs e leis.

Este projeto é a minha **entrega final do Bootcamp de Assistentes de IA da Afya**, onde apliquei os conhecimentos adquiridos durante as aulas para construir um assistente de IA com finalidade prática real.

O objetivo é simples: **dar respostas rápidas e confiáveis sobre legislação farmacêutica** para farmacêuticos que trabalham em drogarias, com base em documentos oficiais reais.

> 💬 *"Como farmacêutico, sei o quanto é difícil lembrar de tudo na correria da drogaria. Espero que essa ferramenta ajude meus colegas."*

---

## 🏗️ Arquitetura

```
📂 farma_chat/
├── main.py                  # Interface Streamlit (Frontend)
├── util/
│   ├── agent.py             # Agente LangChain com ferramentas de RAG
│   └── use_retriever.py     # Pipeline de ingestão e carregamento dos retrievers
├── data/                    # Documentos de legislação farmacêutica (PDFs)
├── chroma_db/               # Banco vetorial persistido (gerado localmente)
├── bm25_index/              # Índice BM25 persistido (gerado localmente)
└── .env                     # Variáveis de ambiente (não versionado)
```

---

## 🤖 Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| **LLM** | [Ollama](https://ollama.com/) – API gratuita na nuvem (`gemma4:31b-cloud`) |
| **Agente** | [LangChain](https://www.langchain.com/) – `create_react_agent` |
| **Embeddings** | `intfloat/multilingual-e5-large` via HuggingFace |
| **Reranker** | `BAAI/bge-reranker-base` via HuggingFace CrossEncoder |
| **Busca vetorial** | [ChromaDB](https://www.trychroma.com/) |
| **Busca léxica** | BM25 (rank_bm25) |
| **RAG** | Hybrid RAG: ChromaDB + BM25 |
| **Ingestão de documentos** | [Docling](https://github.com/DS4SD/docling) |
| **Frontend** | [Streamlit](https://streamlit.io/) |

---

## 📚 Base de Conhecimento (RAG)

O assistente responde com base em legislações farmacêuticas brasileiras oficiais, incluindo:

- **Guia de Legislação para Farmácias e Drogarias** – CFF, 2025
- Leis federais (Lei 5.991/1973, Lei 6.360/1976, Lei 9.787/1999, entre outras)
- Resoluções da ANVISA (RDCs e Instruções Normativas)
- Resoluções do Conselho Federal de Farmácia (CFF)
- Legislações estaduais de 16 estados brasileiros

---

## 🔍 Como Funciona o Hybrid RAG

O agente utiliza três ferramentas encadeadas para garantir respostas mais precisas:

1. **`retrieve_context`** — busca inicial combinando ChromaDB (busca semântica) + BM25 (busca léxica)
2. **`recreate_query`** — o LLM gera um documento fictício baseado na pergunta e no contexto, técnica conhecida como *HyDE (Hypothetical Document Embedding)*
3. **`final_retriver`** — usa o documento fictício para uma segunda busca mais refinada nos índices

Essa abordagem melhora significativamente a qualidade da recuperação comparada ao RAG simples.

---

## 🚀 Como Rodar Localmente

### Pré-requisitos
- Python 3.12+
- GPU com VRAM suficiente **ou** rodar tudo na CPU (configurado por padrão)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/farma-chat.git
cd farma-chat

# Crie o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt
```

### Indexar os documentos (primeira vez)

Coloque os PDFs das legislações na pasta `data/` e rode:

```bash
python util/use_retriever.py
```

### Rodar a aplicação

```bash
streamlit run main.py
```

---

## ⚙️ Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Adicione aqui suas chaves se necessário
OLLAMA_API_KEY=sua_chave_aqui
```

---

## 📌 Limitações e Próximos Passos

- [ ] Adicionar mais legislações estaduais
- [ ] Melhorar o reranking com o `hf` CrossEncoder já configurado
- [ ] Adicionar citação automática da fonte legislativa na resposta
- [ ] Testes automatizados para as ferramentas do agente

---

## 🙏 Agradecimentos

- **DIO + Afya Bootcamp** — pelo conteúdo e pela oportunidade
- **Documentação do LangChain** — fundamental para o Hybrid RAG
- **Claude (Anthropic)** — me ajudou com o frontend em Streamlit *(frontend não é meu forte!)*
- Tutoriais, blogs e outros chats que me ajudaram ao longo do caminho

---

## 👨‍⚕️ Autor

Feito com 💚 por um farmacêutico que acredita que IA pode tornar o trabalho na drogaria mais seguro e eficiente.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Conecte--se-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/romario-gomes/)

---

> ⚠️ **Aviso:** Este é um projeto experimental acadêmico. As respostas são baseadas nos documentos indexados e não substituem consulta a um especialista jurídico ou à legislação original.
