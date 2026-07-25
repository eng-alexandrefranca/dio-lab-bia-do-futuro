import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from rag_engine import buscar_contexto_relevante
from prompts import carregar_system_prompt, formatar_prompt_final

# 1. Carregar variáveis de ambiente
load_dotenv()

# Configuração da página Streamlit
st.set_page_config(
    page_title="BankOn - Onboarding Bancário", 
    page_icon="🏦", 
    layout="centered"
)

st.title("🏦 BankOn")
st.caption("Assistente Virtual de Onboarding e Nivelamento de Novos Colaboradores")

# 2. Configurar API Key do Gemini
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")

if not API_KEY:
    st.warning("⚠️ Variável GEMINI_API_KEY não encontrada no arquivo .env.")

genai.configure(api_key=API_KEY)

# Configuração de Geração: Temperature = 0.0 garante respostas estritas à base (Anti-Alucinação)
GENERATION_CONFIG = genai.GenerationConfig(
    temperature=0.0
)

def obter_modelo_gemini():
    """Retorna o modelo Gemini instanciado utilizando APENAS versões da camada gratuita."""
    # Lista priorizada apenas com modelos com suporte no Free Tier
    modelos_gratuitos = [
        'gemini-2.5-flash',
        'gemini-2.5-flash-lite',
        'gemini-1.5-flash'
    ]
    
    for nome_modelo in modelos_gratuitos:
        try:
            return genai.GenerativeModel(
                model_name=nome_modelo,
                generation_config=GENERATION_CONFIG
            )
        except Exception:
            continue
            
    # Fallback seguro padrão para a camada gratuita
    return genai.GenerativeModel('gemini-2.5-flash', generation_config=GENERATION_CONFIG)

# 3. Inicializar Histórico do Chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Olá! Seja bem-vindo ao banco! Sou o **BankOn**, seu assistente virtual de onboarding. "
                       "Estou aqui para tirar suas dúvidas sobre produtos bancários, conceitos financeiros, compliance e segurança.\n\n"
                       "Como posso te ajudar no seu nivelamento hoje?"
        }
    ]

# Carregar System Prompt oficial com as diretrizes e regras rígidas
system_prompt = carregar_system_prompt()

# 4. Exibir histórico de mensagens anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 5. Captura de entrada do usuário por texto
text_input = st.chat_input("Digite sua dúvida sobre produtos, conceitos ou compliance...")

if text_input:
    # Registra e exibe a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": text_input})
    with st.chat_message("user"):
        st.write(text_input)

    # A. Recuperar contexto dos arquivos da pasta /data (RAG)
    contexto = buscar_contexto_relevante(text_input)

    # B. Formatar histórico recente para manter o fio da conversa
    historico_texto = ""
    for msg in st.session_state.messages[-6:]:
        historico_texto += f"{msg['role']}: {msg['content']}\n"

    # C. Montar o prompt completo (System Prompt + Contexto Local + Histórico + Pergunta)
    prompt_completo = formatar_prompt_final(system_prompt, contexto, historico_texto, text_input)

    # D. Processar resposta via Gemini API
    with st.chat_message("assistant"):
        with st.spinner("Consultando guia de nivelamento..."):
            try:
                model = obter_modelo_gemini()
                response = model.generate_content(prompt_completo)

                bot_reply = response.text
                st.write(bot_reply)

                # Salva a resposta no histórico da sessão
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": bot_reply
                })

            except Exception as e:
                st.error("Erro ao comunicar com o BankOn. Verifique sua chave de API ou conexão.")
                st.caption(f"Detalhes técnicos do erro: {e}")
