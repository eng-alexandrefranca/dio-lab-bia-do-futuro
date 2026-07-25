# Base de Conhecimento — BankOn

> [!TIP]
> **Prompt usado para esta etapa:**
> 
> Organize a base de conhecimento do assistente virtual "BankOn" utilizando os arquivos contidos na pasta `data/`. Explique a finalidade de cada fonte de dados e exemplifique como o contexto é buscado e injetado no LLM via mecanismo RAG para suporte a onboarding e anti-alucinação.

---

## Dados Utilizados

| Arquivo | Formato | Para que serve no BankOn? |
|---------|---------|---------------------------|
| `conceitos_bancarios.json` | JSON | Fornecer definições oficiais e exemplos didáticos sobre termos do mercado financeiro e produtos básicos (ex: CDB, Tesouro Selic, Reserva de Emergência). |
| `produtos_essenciais.csv` | CSV | Detalhar fichas técnicas dos produtos do banco, incluindo público-alvo, regras de rentabilidade, prazos e políticas de resgate. |
| `compliance_seguranca.csv` | CSV | Mapear regras internas de compliance, protocolos de autenticação (como 2FA) e diretrizes de segurança da informação (ex: atualização cadastral, tratamento de indisponibilidade no app). |

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

Os dados originais de atendimentos genéricos e extratos de clientes foram adaptados para compor um **guia formal de onboarding e nivelamento de colaboradores**. Foram consolidados conceitos fundamentais de renda fixa, regras rígidas de segurança digital para o atendimento ao cliente e diretrizes de compliance bancário, garantindo alinhamento estrito às exigências do setor financeiro.

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como o agente acessa a base de conhecimento.

Os dados são lidos diretamente pelo script `rag_engine.py`, que carrega os arquivos da pasta `data/` em memória e realiza uma busca por palavras-chave/relevância com base na dúvida digitada pelo colaborador.

Exemplo de carregamento via código Python:

```python
import json
import pandas as pd

def carregar_base_conhecimento():
    conceitos = json.load(open('./data/conceitos_bancarios.json', encoding='utf-8'))
    produtos = pd.read_csv('./data/produtos_essenciais.csv', encoding='utf-8')
    compliance = pd.read_csv('./data/compliance_seguranca.csv', encoding='utf-8')
    return conceitos, produtos, compliance
```

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

Os dados são consultados dinamicamente via RAG local. Apenas os trechos de conhecimento relevantes para a pergunta do funcionário são extraídos da pasta `data/` e injetados na janela de contexto junto ao System Prompt e ao histórico da conversa.

```text
=================== CONTEXTO DA BASE DE CONHECIMENTO ===================
CONCEITOS BANCÁRIOS (data/conceitos_bancarios.json):
[
  {
    "termo": "CDB",
    "definicao": "Certificado de Depósito Bancário. Título privado emitido por instituições financeiras para captação de recursos...",
    "exemplo": "Rentabilidade de 100% do CDI com liquidez diária ou no vencimento."
  }
]

PRODUTOS ESSENCIAIS (data/produtos_essenciais.csv):
produto,tipo,rentabilidade_prazos,publico_alvo,resgate
CDB,Renda Fixa Privada,Definida na contratação (atrelada ao CDI ou prefixada),Novos investidores e conservadores,Conforme contrato (diário ou no vencimento)

COMPLIANCE E SEGURANÇA (data/compliance_seguranca.csv):
tema,regra_compliance,procedimento_seguranca
Atualizacao Cadastral,Manter dados do cliente sempre atualizados e validados,Apenas o titular pode alterar e-mail ou telefone mediante validação por duplo fator (2FA) e confirmação de identidade.
========================================================================
```

## Exemplo de Contexto Montado

> Um exemplo de como os dados são formatados para o agente.

O exemplo de contexto montado abaixo, se baiseia nos dados originais da base de conhecimento, mas os sintetiza deixando apenas as informações mais relevantes, otimizando assim o consumo de tokens. Entretanto, vale lembrar que mais importante do que economizar tokens, é ter todas as informações relevantes disponíveis em seu contexto.

Quando o novo colaborador digita "Como funciona o CDB e qual o procedimento para alteração de e-mail do cliente?", o `rag_engine.py` consolida o seguinte bloco de contexto:

```
[CONTEXTO RECUPERADO PARA O BANKON]

--- CONCEITO E PRODUTO ---
- Termo: CDB (Certificado de Depósito Bancário)
- Tipo: Renda Fixa Privada
- Público-Alvo: Novos investidores e perfis conservadores
- Resgate: Conforme contrato (diário ou vencimento)
- Definição: Título emitido pelo banco para captação de recursos com taxa pre ou pós-fixada.

--- REGRA DE COMPLIANCE ---
- Tema: Atualização Cadastral
- Regra: Manter dados do cliente sempre validados.
- Procedimento: Alteração de e-mail/telefone exige confirmação de identidade e validação por segundo fator (2FA). Proibido realizar sem a devida autenticação do titular.
```