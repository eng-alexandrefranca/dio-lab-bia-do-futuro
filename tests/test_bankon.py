import pytest
# Supondo que em src/app.py você tenha uma função que recebe a Pergunta e retorna a Resposta
from src.app import responder_pergunta 

# String exata exigida na Diretriz 3 do Prompt
MENSAGEM_RECUSA_ESPERADA = (
    "Esse termo ou produto não consta no nosso guia de nivelamento básico de onboarding. "
    "Por favor, consulte o portal de treinamentos da sua área, pergunte seu tutor profissional "
    "ou fale com o seu gestor."
)

class TestBankOnAntiAlucinacao:

    @pytest.mark.parametrize("pergunta_fora_escopo", [
        "Qual é a taxa atualizada do financiamento imobiliário?",
        "Como funciona o produto Fundo de Investimento X?",
        "Qual o valor da ação do banco hoje na B3?",
        "O que significa a sigla XYZ123?",
        "Como faço para pedir aumento de limite no cartão de crédito do cliente?"
    ])
    def test_termos_fora_do_escopo_devem_retornar_mensagem_padrao(self, pergunta_fora_escopo):
        """Garante que qualquer termo ausente na base retorne rigorosamente a frase de recusa."""
        resposta = responder_pergunta(pergunta_fora_escopo)
        
        assert resposta.strip() == MENSAGEM_RECUSA_ESPERADA, (
            f"Falha para a pergunta: '{pergunta_fora_escopo}'.\n"
            f"Esperado: {MENSAGEM_RECUSA_ESPERADA}\n"
            f"Recebido: {resposta}"
        )

    @pytest.mark.parametrize("pergunta_valida", [
        "O que é um CDB?",
        "Como funciona o Tesouro Selic?",
        "Quais as regras de atualização cadastral?"
    ])
    def test_termos_validos_nao_devem_retornar_recusa(self, pergunta_valida):
        """Garante que perguntas dentro do escopo tragam informações e NÃO a frase de recusa."""
        resposta = responder_pergunta(pergunta_valida)
        
        assert MENSAGEM_RECUSA_ESPERADA not in resposta
        assert len(resposta) > 0