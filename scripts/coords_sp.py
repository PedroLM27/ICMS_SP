import geobr
import pandas as pd
import os

def criar_base_coordenadas():
    print("🌍 Buscando coordenadas e códigos oficiais do IBGE")
    os.makedirs('data/raw', exist_ok=True)
    
    # Baixa os dados de SP
    df_sp = geobr.read_municipality(code_muni="SP", year=2022)
    
    # Extrai latitude e longitude do centroide
    df_sp['latitude'] = df_sp.geometry.centroid.y
    df_sp['longitude'] = df_sp.geometry.centroid.x
    
    # Mantém o Código IBGE (7 dígitos) para um cruzamento perfeito
    # O geobr traz o código completo, garantimos que seja string para o merge
    df_sp['IBGE_7'] = df_sp['code_muni'].astype(str)
    # Criamos também uma versão de 6 dígitos, pois alguns PDFs do governo usam apenas 6
    df_sp['IBGE_6'] = df_sp['IBGE_7'].str[:6]
    
    df_sp['Município_Join'] = df_sp['name_muni'].str.upper().str.strip()
    
    df_coords = df_sp[['IBGE_6', 'IBGE_7', 'Município_Join', 'latitude', 'longitude']]
    df_coords.to_csv('data/raw/municipios_sp_coords.csv', index=False)
    print(f"✅ Base gerada com sucesso: {len(df_coords)} municípios carregados.")

if __name__ == "__main__":
    criar_base_coordenadas()