import sys
import os
import pandas as pd

# Ajusta o caminho para encontrar a pasta scripts
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from scripts.calculator import calcular_repasse_icms
from scripts.coords_sp import criar_base_coordenadas
from scripts.parser_pdf import extrair_dados
from scripts.transform import processar_sp
from scripts.heatmap import gerar_mapa_status # Alterado para o novo mapa de status

if __name__ == "__main__":
    try:
        print("\n--- 🚀 Iniciando Pipeline ICMS Educacional SP 2025 ---")

        # Passo 0: Coordenadas Geográficas
        print("\nPasso 0: Configurando base de coordenadas...")
        criar_base_coordenadas()

        # Passo 1: Extração do PDF (Verifique se o PDF de 2025 está na pasta data/raw)
        print("\nPasso 1: Extraindo dados do PDF de 2025...")
        extrair_dados()

        # Passo 2: Processamento e Cruzamento
        # Agora salvamos o retorno do processamento em uma variável
        print("\nPasso 2: Processando e cruzando dados dos municípios...")
        df_processado = processar_sp()

        # Passo 3: Calculadora
        # Simulando um valor total de repasse (Ex: 100 Milhões)
        # O df_processado deve conter colunas de população e IQEM para o cálculo real
        print("\nPasso 3: Calculando estimativas de repasse...")
        VALOR_TOTAL_ESTADO = 100000000  # Exemplo de orçamento
        df_com_calculos = calcular_repasse_icms(VALOR_TOTAL_ESTADO, df_processado)
        
        # Salva o resultado da calculadora em CSV
        os.makedirs('output', exist_ok=True)
        df_com_calculos.to_csv('output/estimativa_repasse_2025.csv', index=False)

        # Passo 4: Visualização (Mapa de Status)
        print("\nPasso 4: Gerando mapa de identificação (Recebeu vs Inabilitado)...")
        gerar_mapa_status(df_com_calculos)

        print("\n--- ✅ Tudo pronto! Verifique a pasta 'output' ---")
        print("Arquivos gerados: mapa_status_2025.html e estimativa_repasse_2025.csv")

    except Exception as e:
        print(f"\n❌ Erro no Pipeline: {e}")