import os
import ssl
import json
import urllib3
import requests
import dotenv
import streamlit as st

from rag_engine import buscar_contexto_relevante
from prompts import carregar_system_prompt, formatar_prompt_final

# ==============================================================================
# 1. CONFIGURAÇÕES ANTI-BLOQUEIO SSL & PROXY (Ambiente Corporativo/Dev)
# ==============================================================================
os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Carrega variáveis do .env
dotenv.load_dotenv()

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="BankOn - Onboarding Bancário", 
    page_icon="🏦", 
    layout="centered"
)

st.title("🏦 BankOn")
st.caption("Assistente Virtual de Onboarding e Nivelamento de Novos Colaboradores")

# Validação da Chave de API
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")

if not API_KEY:
    st.warning("⚠️ Variável GEMINI_API_KEY não encontrada no arquivo .env.")

# ==============================================================================
# 3. FUNÇÃO DE CHAMADA REST DIRETA (Com Fallback de Modelos e Bypass SSL)
# ==============================================================================
def chamar_gemini_rest(prompt_completo: str) -> str:
    """
    Envia o prompt para a API REST do Gemini testando modelos ativos na camada gratuita.
    Supera travamentos de gRPC, erros de SSL e erros 404 de modelos descontinuados.
    """
    # Lista de modelos ativos ordenados por prioridade
    modelos_para_testar = [
        "gemini-flash-latest",
        "gemini-3.5-flash",
        "gemini-3.5-lite",
        "gemini-3.1-flash",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
    ]
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt_completo}]
        }],
        "generationConfig": {
            "temperature": 0.0  # Respostas estritas e anti-alucinação
        }
    }
    
    ultimo_erro = None

    for modelo in modelos_para_testar:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={API_KEY}"
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                json=payload, 
                verify=False, 
                timeout=30
            )
            
            if response.status_code == 200:
                dados = response.json()
                return dados["candidates"][0]["content"]["parts"][0]["text"]
            
            # Se a API retornar erro (ex: 404), guarda e tenta o próximo modelo
            ultimo_erro = f"HTTP {response.status_code}: {response.text}"
            
        except Exception as err:
            ultimo_erro = str(err)
            continue

    # Caso nenhum modelo responda com sucesso
    raise Exception(f"Não foi possível conectar aos modelos da API. Último erro: {ultimo_erro}")

# ==============================================================================
# 4. ESTADO DA SESSÃO E INICIALIZAÇÃO
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Olá! Seja bem-vindo ao banco! Sou o **BankOn**, seu assistente virtual de onboarding. "
                       "Estou aqui para tirar suas dúvidas sobre produtos bancários, conceitos financeiros, compliance e segurança.\n\n"
                       "Como posso te ajudar no seu nivelamento hoje?"
        }
    ]

# Carrega System Prompt oficial
system_prompt = carregar_system_prompt()

# Exibe histórico de mensagens do chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ==============================================================================
# 5. PROCESSAMENTO DE ENTRADA DO USUÁRIO
# ==============================================================================
text_input = st.chat_input("Digite sua dúvida sobre produtos, conceitos ou compliance...")

if text_input:
    # Registra e exibe a mensagem enviada pelo usuário
    st.session_state.messages.append({"role": "user", "content": text_input})
    with st.chat_message("user"):
        st.write(text_input)

    # A. Busca contexto relevante na pasta /data (RAG)
    contexto = buscar_contexto_relevante(text_input)

    # B. Formata o histórico recente
    historico_texto = ""
    for msg in st.session_state.messages[-6:]:
        historico_texto += f"{msg['role']}: {msg['content']}\n"

    # C. Monta o prompt consolidado (System Prompt + Contexto RAG + Histórico + Pergunta)
    prompt_completo = formatar_prompt_final(system_prompt, contexto, historico_texto, text_input)

    # D. Gera e exibe a resposta via API REST
    with st.chat_message("assistant"):
        with st.spinner("Consultando guia de nivelamento..."):
            try:
                bot_reply = chamar_gemini_rest(prompt_completo)
                st.write(bot_reply)

                # Salva a resposta no histórico da sessão
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": bot_reply
                })

            except Exception as e:
                st.error("Erro ao comunicar com o BankOn. Verifique sua chave de API ou conexão.")
                st.caption(f"Detalhes técnicos: {e}")