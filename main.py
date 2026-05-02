from langchain.messages import HumanMessage,AIMessage
import streamlit as st
import time
from util.agent import agent


import time

def stream_response(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.05)

def convert_history(messages: list) -> list:
    """Converte st.session_state.messages para mensagens LangChain."""
    history = []
    for msg in messages[:-1]:  # exclui a última (é o prompt atual)
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history.append(AIMessage(content=msg["content"]))
    return history

st.set_page_config(
    page_title="FarmaChat – Legislação Farmacêutica",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

  /* ── Global ── */
  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* ── Background ── */
  .stApp {
    background: linear-gradient(135deg, #f0f9f4 0%, #e8f5f0 40%, #f5f9ff 100%);
    min-height: 100vh;
  }

  /* ── Header block ── */
  .hero-block {
    background: linear-gradient(135deg, #0d6e4a 0%, #0a8a5c 50%, #0d6e4a 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem 2rem;
    margin-bottom: 1.8rem;
    box-shadow: 0 8px 32px rgba(13,110,74,0.25);
    position: relative;
    overflow: hidden;
  }
  .hero-block::before {
    content: "💊";
    position: absolute;
    right: -10px; top: -20px;
    font-size: 9rem;
    opacity: 0.08;
  }
  .hero-block h1 {
    font-family: 'DM Serif Display', serif;
    color: #ffffff;
    font-size: 2rem;
    margin: 0 0 0.4rem;
    line-height: 1.2;
  }
  .hero-block p {
    color: #a8f0d0;
    font-size: 1rem;
    font-weight: 300;
    margin: 0;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: #0d6e4a !important;
  }
  section[data-testid="stSidebar"] * {
    color: #e8f5f0 !important;
  }
  .sidebar-card {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1rem;
  }
  .sidebar-card h3 {
    font-family: 'DM Serif Display', serif;
    color: #ffffff !important;
    margin: 0 0 0.6rem;
    font-size: 1.05rem;
  }
  .sidebar-card p, .sidebar-card a {
    font-size: 0.85rem;
    line-height: 1.6;
  }
  .sidebar-card a {
    color: #a8f0d0 !important;
    text-decoration: underline;
  }
  .badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border-radius: 99px;
    padding: 2px 10px;
    font-size: 0.75rem;
    margin-top: 0.5rem;
    color: #a8f0d0 !important;
  }

  /* ── Chat messages ── */
  [data-testid="stChatMessage"] {
    border-radius: 14px;
    margin-bottom: 0.5rem;
    border: none;
  }
  /* user bubble */
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #e1f5ec;
  }
  /* assistant bubble */
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(13,110,74,0.08);
  }

  /* ── Input ── */
  [data-testid="stChatInput"] textarea {
    border: 2px solid #0d6e4a !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  [data-testid="stChatInput"] textarea:focus {
    box-shadow: 0 0 0 3px rgba(13,110,74,0.15) !important;
  }

  /* ── Disclaimer banner ── */
  .disclaimer {
    background: #fff8e1;
    border-left: 4px solid #f59e0b;
    border-radius: 0 10px 10px 0;
    padding: 0.8rem 1rem;
    font-size: 0.82rem;
    color: #7c5a00;
    margin-bottom: 1.2rem;
  }

  [data-testid="stChatMessage"] p,
  [data-testid="stChatMessage"] li,
  [data-testid="stChatMessage"] span {
    color: #000000 !important;
  }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
      <span style="font-size:3rem;">⚕️</span>
      <h2 style="font-family:'DM Serif Display',serif; color:#fff; margin:0.3rem 0 0;">FarmaChat</h2>
      <p style="color:#a8f0d0; font-size:0.8rem; margin:0;">v1.0 – Projeto Experimental</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div class="sidebar-card">
      <h3>Sobre o Projeto</h3>
      <p>
        Como farmacêutico, entendo a correria do dia a dia na drogaria e a necessidade urgente de tirar dúvidas sobre legislação farmacêutica rapidamente.<br><br>
        O <strong>FarmaChat</strong> é um agente experimental cujas respostas são baseadas em legislações farmacêuticas brasileiras. Espero que ajude meus colegas a obterem respostas rápidas sobre farmácia! 🤝
      </p>
      <span class="badge">📄 Base: Guia de Legislação CFF 2025</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card">
      <h3>📚 Legislações</h3>
      <p>
        As respostas deste agente são fundamentadas no <em>Guia de Legislação para Farmácias e Drogarias</em> (CFF, 2025), que reúne normas federais, resoluções da ANVISA, portarias do CFF e legislações estaduais.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card">
      <h3>👤 Contato</h3>
      <p>
        Dúvidas, sugestões ou colaborações?<br>
        Me encontre no LinkedIn:Romario Gomes</br>
        <a href="https://www.linkedin.com/in/romario-gomes/" target="_blank">🔗 linkedin.com/in/seu-perfil</a>
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding: 1rem 0; font-size:0.75rem; color:#a8f0d0;">
      ⚠️ Projeto experimental – não substitui consulta profissional ou jurídica
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="hero-block">
  <h1>💬 Fale com a Legislação Farmacêutica</h1>
  <p>Uma forma rápida de tirar dúvidas sobre a legislação farmacêutica</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer">
  ⚠️ <strong>Aviso:</strong> Este é um projeto experimental. As respostas são baseadas no
  <em>Guia de Legislação para Farmácias e Drogarias (CFF, 2025)</em> e em legislações farmacêuticas
  disponíveis. Consulte sempre o texto original das normas e, se necessário, um especialista jurídico.
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "💊"):
        st.markdown(msg["content"])

if not st.session_state.messages:
    st.markdown("**💡 Perguntas frequentes para começar:**")
    cols = st.columns(2)
    suggestions = [
        "Quais medicamentos precisam de receita retida?",
        "O que diz a RDC 44/2009 sobre boas práticas?",
        "Posso vacinar em drogaria? Quais requisitos?",
        "O farmacêutico precisa estar presente o tempo todo?",
    ]
    for i, s in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(s, use_container_width=True, key=f"sug_{i}"):
                st.session_state.messages.append({"role": "user", "content": s})
                st.rerun()

prompt = st.chat_input("Digite sua dúvida sobre legislação farmacêutica...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="💊"):

        history = convert_history(st.session_state.messages)

        response = agent.invoke({
            "messages": history + [HumanMessage(content=prompt)]
            })

        st.write_stream(stream_response(response['messages'][-1].content))
        
        
        st.session_state.messages.append({"role": "assistant", "content": response['messages'][-1].content})

# ─── Footer ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; font-size:0.78rem; color:#6b7280;'>"
    "FarmaChat © 2025 · Projeto experimental · "
    "Respostas baseadas no Guia de Legislação CFF 2025 · "
    "Não substitui orientação jurídica profissional"
    "</p>",
    unsafe_allow_html=True,
)
