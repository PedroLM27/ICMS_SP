import pandas as pd

def calcular_repasse_icms(valor_total_disponivel, df_municipios):
    print(f"🧮 Calculando repasses baseados no montante de R$ {valor_total_disponivel:,.2f}...")
    
    # Garante que o índice é float puro
    df_municipios['iqem_indice'] = df_municipios['iqem_indice'].astype(float)
    
    # Cálculo base: Total * Índice da Cota Parte
    df_municipios['valor_estimado'] = valor_total_disponivel * df_municipios['iqem_indice']
    
    # REGRA DE NEGÓCIO: Se a cidade NÃO recebeu o valor (está inabilitada), o repasse estimado DEVE ser zero!
    df_municipios.loc[df_municipios['recebeu_valor'] == False, 'valor_estimado'] = 0.0
    
    # Ordena do maior para o menor repasse real
    df_municipios = df_municipios.sort_values(by='valor_estimado', ascending=False)
    
    return df_municipios

# Exemplo de teste isolado
if __name__ == "__main__":
    # Simulando os dados que viriam do seu novo transform.py
    dados_exemplo = {
        'Município_Join': ['ADAMANTINA', 'ADOLFO', 'AGUAI'],
        'iqem_indice': [0.0007679, 0.0001282, 0.0008075], # Valores da sua imagem
        'populacao': [34687, 4351, 32072]
    }
    df_teste = pd.DataFrame(dados_exemplo)
    
    # Supondo um repasse total de 1 bilhão de reais para o estado
    resultado = calcular_repasse_icms(1000000000, df_teste)
    
    print("\n--- Resultado da Simulação (Top 3) ---")
    print(resultado[['Município_Join', 'valor_estimado']])