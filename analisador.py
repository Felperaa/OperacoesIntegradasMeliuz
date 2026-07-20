import pandas as pd
import os
import argparse
from datetime import datetime

def limpar_moeda(valor):
    """Limpa formato 'R$ 10.273' ou 'R$ 10.273,50' para float nativo."""
    if pd.isna(valor): return 0.0
    valor_str = str(valor).replace('R$', '').strip()
    # Se tem ponto e vírgula (ex: 1.000,50)
    if '.' in valor_str and ',' in valor_str:
        valor_str = valor_str.replace('.', '').replace(',', '.')
    # Se só tem ponto (ex: 10.273 - assumindo que é milhar no padrão BR dos datasets)
    elif '.' in valor_str:
        partes = valor_str.split('.')
        if len(partes[-1]) == 3:  # É separador de milhar
            valor_str = valor_str.replace('.', '')
    return float(valor_str)

def analisar_teste(caminho_csv, arquivo_planilha="acompanhamento_testes.csv"):
    print(f"Analisando dataset: {caminho_csv}...")
    
    try:
        df = pd.read_csv(caminho_csv)
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")
        return

    # Limpeza de dados robusta
    colunas_monetarias = ['comissão', 'cashback', 'vendas totais']
    for col in colunas_monetarias:
        df[col] = df[col].apply(limpar_moeda)
    
    df['compradores'] = pd.to_numeric(df['compradores'], errors='coerce').fillna(0)

    # Agrupamento e cálculo de métricas A/B
    resumo = df.groupby('Grupos de usuários').agg(
        total_compradores=('compradores', 'sum'),
        total_comissao=('comissão', 'sum'),
        total_cashback=('cashback', 'sum'),
        total_gmv=('vendas totais', 'sum')
    ).reset_index()

    # Visão de Growth / Negócio Méliuz
    # Receita Líquida Méliuz = Comissão recebida - Cashback pago
    resumo['receita_liquida_meliuz'] = resumo['total_comissao'] - resumo['total_cashback']
    resumo['ticket_medio'] = resumo['total_gmv'] / resumo['total_compradores']
    resumo['roi_meliuz'] = (resumo['receita_liquida_meliuz'] / resumo['total_cashback']).round(2)

    # Tomada de decisão: A variante vencedora maximiza a Receita Líquida do Méliuz
    vencedor = resumo.loc[resumo['receita_liquida_meliuz'].idxmax()]
    parceiro = df['Parceiro'].iloc[0]
    nome_teste = f"Teste A/B - {parceiro}"

    # 1. Gerar Relatório
    relatorio_md = f"""# Relatório de Teste A/B: {parceiro}
*Data da análise: {datetime.now().strftime('%Y-%m-%d')}*

## Resumo dos Resultados
"""
    for _, row in resumo.iterrows():
        relatorio_md += f"""
### {row['Grupos de usuários']}
- **Usuários Compradores:** {row['total_compradores']:,.0f}
- **Vendas Totais (GMV):** R$ {row['total_gmv']:,.2f}
- **Ticket Médio:** R$ {row['ticket_medio']:,.2f}
- **Comissão Gerada:** R$ {row['total_comissao']:,.2f}
- **Cashback Distribuído:** R$ {row['total_cashback']:,.2f}
- **Receita Líquida Méliuz:** R$ {row['receita_liquida_meliuz']:,.2f}
"""

    relatorio_md += f"""
## Decisão Acionável
**Variante recomendada para escalar para 100% do tráfego:** `{vencedor['Grupos de usuários']}`.

**Justificativa Analítica:**
O grupo `{vencedor['Grupos de usuários']}` gerou a maior Receita Líquida para o Méliuz (R$ {vencedor['receita_liquida_meliuz']:,.2f}), que é o indicador de rentabilidade final da operação (Comissão - Cashback). Escalar esta variante maximiza a margem da empresa.
"""

    nome_arquivo_relatorio = f"relatorio_{parceiro.replace(' ', '_')}.md"
    with open(nome_arquivo_relatorio, "w", encoding="utf-8") as f:
        f.write(relatorio_md)
    print(f" Relatório gerado: {nome_arquivo_relatorio}")

    # 2. Registrar na Planilha de Acompanhamento (Append CSV)
    novo_registro = pd.DataFrame([{
        "Data_Analise": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "Nome_Teste": nome_teste,
        "Parceiro": parceiro,
        "Variante_Vencedora": vencedor['Grupos de usuários'],
        "Receita_Liquida_Vencedora": f"R$ {vencedor['receita_liquida_meliuz']:.2f}",
        "Decisao": f"Escalar {vencedor['Grupos de usuários']} (Maior margem líquida)"
    }])

    if not os.path.isfile(arquivo_planilha):
        novo_registro.to_csv(arquivo_planilha, index=False, encoding='utf-8')
    else:
        novo_registro.to_csv(arquivo_planilha, mode='a', header=False, index=False, encoding='utf-8')
    print(f" Teste registrado na planilha: {arquivo_planilha}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Méliuz A/B Test Analyzer")
    parser.add_argument("dataset", help="Caminho para o arquivo CSV do dataset")
    args = parser.parse_args()
    analisar_teste(args.dataset)