import pandas as pd
import numpy as np

def processar_sp():
    print("⚙️ Iniciando processamento dos dados 2025 com índices DIPAM...")
    
   # 1. Carregamento dos arquivos com tratamento de encoding
    print("📂 Carregando arquivos brutos...")
    
    # Arquivos gerados pelo seu pipeline costumam ser UTF-8
    df_rec = pd.read_csv('data/processed/receitas_br.csv', encoding='utf-8')
    df_ina = pd.read_csv('data/processed/inabilitados_br.csv', encoding='utf-8-sig')
    df_coords = pd.read_csv('data/raw/municipios_sp_coords.csv', encoding='utf-8')
    
    
    
    
    try:
       
        df_dipam = pd.read_csv(
            'data/raw/indices_dipam_2024.csv', 
            sep=None, 
            engine='python', 
            encoding='utf-8-sig' # O 'utf-8-sig' ignora o marcador de ordem de byte que o Excel coloca
        )
        
        # Limpeza de colunas (para remover espaços e garantir que o Python ache os nomes)
        df_dipam.columns = [c.strip() for c in df_dipam.columns]
        
        print("✅ CSV da DIPAM (UTF-8) carregado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo salvo: {e}")
    # Funções de limpeza
    def limpar_valor_pdf(valor):
        if pd.isna(valor) or str(valor).strip() in ['-', '']:
            return 0.0
        valor_limpo = str(valor).replace(' ', '').strip()
        try:
            if ',' in valor_limpo:
                valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
            return float(valor_limpo)
        except ValueError:
            return 0.0

    def limpar_valor_dipam(valor):
        # A DIPAM usa pontos para milhar e vírgula para decimal (ex: 1.216.515,00)
        if pd.isna(valor): return 0.0
        return float(str(valor).replace('.', '').replace(',', '.'))

    # 2. Filtrar SP e preparar Receitas VAAR
    sp_receitas = df_rec[df_rec.iloc[:, 0].astype(str).str.contains('SP', na=False)].copy()
    
    # Limpeza robusta do Código IBGE do PDF:
    
    sp_receitas['IBGE_6'] = sp_receitas.iloc[:, 1].astype(str).str.replace('.0', '', regex=False).str.strip().str[:6]
    
    col_vaar_nome = sp_receitas.columns[6]
    sp_receitas['valor_vaar_2025'] = sp_receitas[col_vaar_nome].apply(limpar_valor_pdf)
    
    # 3. Preparar dados da DIPAM (Índices e População)
    # Força a limpeza de espaços em branco nos nomes das colunas
    df_dipam.columns = [str(c).strip() for c in df_dipam.columns]
    print(f"📊 Colunas reais encontradas na DIPAM: {list(df_dipam.columns)}")

    # Busca automatizada para evitar erros de acentuação (acha 'Município', 'Municipio' ou 'MUNICÍPIO')
    colunas_municipio = [c for c in df_dipam.columns if 'MUNICI' in c.upper()]
    if not colunas_municipio:
        raise KeyError("Não foi possível encontrar uma coluna de Município no arquivo da DIPAM.")
    col_municipio_real = colunas_municipio[0]

    # Identifica as outras colunas cruciais
    col_populacao_real = [c for c in df_dipam.columns if 'POPULA' in c.upper()][0]
    col_cota_real = [c for c in df_dipam.columns if 'COTA' in c.upper() or 'EDUCA' in c.upper()][0]

    # Padroniza os dados usando as colunas dinâmicas encontradas
    df_dipam['Município_Join'] = df_dipam[col_municipio_real].astype(str).str.upper().str.strip()
    df_dipam['populacao'] = df_dipam[col_populacao_real].apply(limpar_valor_dipam)
    df_dipam['iqem_indice'] = df_dipam[col_cota_real].apply(limpar_valor_dipam)

    print(f"🎯 Mapeamento DIPAM concluído usando a coluna: '{col_municipio_real}'")
    # 4. Preparar Inabilitados
    coluna_motivo = df_ina.columns[-1]
    df_ina_sp = df_ina[df_ina.iloc[:, 0].astype(str).str.contains('SP', na=False)].copy()
    df_ina_sp['Município_Join'] = df_ina_sp.iloc[:, 1].astype(str).str.upper().str.strip()

    # 5. Cruzamento Principal (Base Geográfica + Receitas via Código IBGE)
    # Garante que a base do geobr também está estritamente com 6 dígitos em formato string
    df_coords['IBGE_6'] = df_coords['IBGE_6'].astype(str).str.strip().str[:6]
    
    # Remove duplicados do PDF se houver, para não inflar o merge
    sp_receitas_clean = sp_receitas.drop_duplicates(subset=['IBGE_6'])
    
    # Realiza o cruzamento das coordenadas com o valor do PDF
    df_final = pd.merge(df_coords, sp_receitas_clean[['IBGE_6', 'valor_vaar_2025']], on='IBGE_6', how='left')

    # 6. Cruzamento com dados DIPAM (via Nome do Município)
    df_final = pd.merge(
        df_final, 
        df_dipam[['Município_Join', 'populacao', 'iqem_indice']], 
        on='Município_Join', 
        how='left'
    )

    # 7. Cruzamento com Inabilitados (via Nome)
    df_final = pd.merge(
        df_final, 
        df_ina_sp[['Município_Join', coluna_motivo]], 
        on='Município_Join', 
        how='left'
    )
    df_final = df_final.rename(columns={coluna_motivo: 'Motivo'})

    # 8. Definição de Status e preenchimento de nulos
    df_final['recebeu_valor'] = (df_final['valor_vaar_2025'] > 0) & (df_final['Motivo'].isna())
    df_final['valor_vaar_2025'] = df_final['valor_vaar_2025'].fillna(0)
    df_final['iqem_indice'] = df_final['iqem_indice'].fillna(0)
    df_final['populacao'] = df_final['populacao'].fillna(0)

    # Salva o resultado consolidado
    df_final.to_csv('data/processed/dados_finais_sp.csv', index=False)
    
    print(f"✅ Processamento concluído!")
    print(f"📊 Municípios com repasse VAAR 2025: {df_final[df_final['recebeu_valor'] == True].shape[0]}")
    
    return df_final

if __name__ == "__main__":
    processar_sp()