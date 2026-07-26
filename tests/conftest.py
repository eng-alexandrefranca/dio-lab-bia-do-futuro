import time
import pytest

@pytest.fixture(autouse=True)
def pausar_entre_testes():
    """Garante um intervalo entre as chamadas para não estourar o limite de 429 da API."""
    yield
    # Pausa 2.5 segundos após a execução de cada teste
    time.sleep(2.5)