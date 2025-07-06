import streamlit as st
from agent.agent_runner import get_agent, run_agent_with_tools
from providers.bedrock import get_llm
from providers.vectorstore import reset_vector_db
from providers.websearch import clear_search_cache
from dotenv import load_dotenv
load_dotenv()

# --- Streamlit UI ---
st.set_page_config(page_title="Annet - HR Policy Research Assistant")

# Main area header
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px; margin-bottom: 30px;">
    <h1 style="color: #2c3e50; margin: 0; font-size: 28px;">⚡ Annet: Your HR Policy & Insurance Research Assistant</h1>
    <p style="color: #34495e; margin: 10px 0 0 0; font-size: 16px;">Ask me anything about HR policies, insurance queries, or industry trends!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Header with styling
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0; font-size: 24px;">⚡ Annet</h2>
        <p style="color: white; margin: 5px 0; font-size: 14px; opacity: 0.9;">Your AI HR Research Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    # Capabilities section with better styling
    st.markdown("""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; border-left: 4px solid #667eea; margin-bottom: 20px;">
        <h4 style="margin: 0 0 15px 0; color: #333; font-size: 18px;">✨ What I Can Do</h4>
        <div style="line-height: 1.8;">
            <div style="margin-bottom: 8px;">🔍 HR Policy Q&A (internal PDFs)</div>
            <div style="margin-bottom: 8px;">🏥 Insurance Queries (Google Docs)</div>
            <div style="margin-bottom: 8px;">🌐 Web Search (public info)</div>
            <div style="margin-bottom: 8px;">🎯 Smart Tool Selection</div>
            <div style="margin-bottom: 8px;">📚 Citations & References</div>
            <div style="margin-bottom: 8px;">⚡ Rate Limiting Protection</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Clear chat button with better styling
    if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.rerun()

# --- Chat UI ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "db_reset" not in st.session_state:
    st.session_state.db_reset = True
    reset_vector_db()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about HR policies..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.pending_prompt = prompt
    st.rerun()

if "pending_prompt" in st.session_state:
    prompt = st.session_state.pending_prompt
    agent, tools = get_agent(get_llm())
    with st.chat_message("assistant"):
        with st.spinner("Annet is thinking..."):
            answer = run_agent_with_tools(agent, prompt, tools)
            if answer:
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
    del st.session_state.pending_prompt
