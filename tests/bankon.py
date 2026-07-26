import time
from google.api_core.exceptions import ResourceExhausted

def responder_pergunta(pergunta: str) -> str:
    tentativas = 3
    tempo_espera = 4  # segundos
    
    for tentativa in range(tentativas):
        try:
            # Sua chamada de geração de conteúdo do Gemini aqui
            response = model.generate_content(pergunta)
            return response.text
        except ResourceExhausted as e:
            if tentativa < tentativas - 1:
                print(f"\n[429] Limite atingido. Aguardando {tempo_espera}s antes de tentar novamente...")
                time.sleep(tempo_espera)
                tempo_espera *= 2  # Dobra o tempo a cada erro (4s, 8s...)
            else:
                raise e