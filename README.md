#OperacoesIntegradasMeliuz

# Analisador Automatizado de Testes A/B - Méliuz

Esta solução foi desenvolvida para automatizar a análise de testes A/B de cashback do Méliuz, reduzindo o tempo de análise de horas para segundos, eliminando vieses e erros humanos no cálculo.

## Arquitetura da Solução
A solução utiliza uma abordagem híbrida ideal para integrações com IAs (Cursor, Claude Code, etc.):
1. **Script Python (`analisador.py`)**: Garante precisão absoluta nos cálculos, tratamento de dados "sujos" (conversão de moedas BR) e padronização dos outputs.
2. **Prompt de Agente (`instrucoes_agente.md`)**: Contexto em linguagem natural para que qualquer pessoa do time peça à IA para rodar a análise usando o script.

## Como Rodar

### Opção 1: Via Linha de Comando (Tradicional)
Certifique-se de ter o `pandas` instalado (`pip install pandas`). No terminal, rode:

python analisador.py dataset\\\_01\\\_parceiroA.csv

ou

Opção 2: Via Ferramenta de IA (Cursor / Claude Code / ChatGPT Interpreter)

Basta abrir o chat da ferramenta e digitar:

"Analise os 3 testes A/B que estão nos datasets CSV desta pasta."

A IA usará as diretrizes do arquivo instrucoes_agente.md para rodar o script e devolver a resposta.

