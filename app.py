import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Calculadora ICMS Educacional SP", layout="centered")

st.title("🧮 Calculadora Interativa - ICMS Educacional SP 2025")
st.write("Consulte as estimativas de repasse e o status de habilitação dos 645 municípios de São Paulo.")

# 1. Carregar a base de dados que seu pipeline gerou
@st.cache_data
def carregar_dados():
    # Carrega o arquivo final gerado pelo seu transform/calculator
    df = pd.read_csv('data/processed/dados_finais_sp.csv')
    # Garante que os nomes estão em maiúsculo para facilitar a busca
    df['Município_Join'] = df['Município_Join'].str.upper().str.strip()
    return df

try:
    df_sp = carregar_dados()

    # 2. Entrada do usuário: Definição do Orçamento Total do Estado
    st.sidebar.header("⚙️ Configurações do Orçamento")
    orcamento_total = st.sidebar.number_input(
        "Orçamento Total para Distribuição (R$):",
        min_value=1000000,
        max_value=100000000000,
        value=100000000, # 100 Milhões padrão
        step=1000000,
        format="%d"
    )

    # 3. Entrada do usuário: Busca pelo Município
    st.subheader("🔍 Pesquisar Município")
    lista_municipios = sorted(df_sp['Município_Join'].unique())
    municipio_selecionado = st.selectbox("Selecione ou digite o nome da cidade:", lista_municipios)

    # 4. Filtrar e Calcular o resultado da cidade escolhida
    if municipio_selecionado:
        dados_cidade = df_sp[df_sp['Município_Join'] == municipio_selecionado].iloc[0]
        
        # Recupera as informações da base
        indice_cota = float(dados_cidade['iqem_indice'])
        status_recebimento = dados_cidade['recebeu_valor']
        populacao = dados_cidade['populacao']
        motivo_inabilitado = dados_cidade.get('Motivo', 'Não especificado')

        st.markdown("---")
        st.header(f"🏙️ {municipio_selecionado}")
        
        # Métrica de População e Índice
        col1, col2 = st.columns(2)
        col1.metric("População Estimada", f"{int(populacao):,}".replace(",", "."))
        col2.metric("Cota Parte Educação (Índice)", f"{indice_cota:.7f}")

        # --- CÁLCULO E VALIDAÇÃO (Dentro do escopo do município selecionado) ---
        # 1. Inicializa a variável para evitar avisos do linter
        valor_calculado = 0.0
        
        # 2. Realiza o cálculo matemático da regra de negócio
        if pd.notna(indice_cota):
            valor_calculado = orcamento_total * indice_cota

        # 3. Padroniza o status para validação
        status_validado = str(status_recebimento).strip().lower() if pd.notna(status_recebimento) else "false"

        # 4. Verificação do Status de Repasse
        if status_validado in ["true", "1", "sim"]:
            
            # SE RECEBEU, MAS O ÍNDICE OU O VALOR DEU ZERO (Trata o problema dos dados sumidos)
            if valor_calculado == 0 or pd.isna(valor_calculado):
                st.success("✔️ **Habilitado para o Repasse**")
                st.warning("⚠️ **Atenção:** Este município está habilitado, mas o Índice da Cota-Parte Educação está zerado ou não foi preenchido.")
                st.markdown("### 💰 Valor Estimado a Receber: **R$ 0,00**")
            
            # SE RECEBEU E TEM VALOR VÁLIDO (Fluxo normal de sucesso)
            else:
                st.success("✔️ **Habilitado para o Repasse**")
                # Formatação para o padrão brasileiro (R$ 1.234,56)
                valor_formatado = f"{valor_calculado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                st.markdown(f"### 💰 Valor Estimado a Receber: **R$ {valor_formatado}**")
                st.caption("Este valor é calculado multiplicando o orçamento total inserido pelo índice oficial da cota-parte do município.")

        else:
            # FLUXO DE INABILITADO
            st.error("❌ **Inabilitado / Não recebeu o repasse**")
            
            if pd.notna(motivo_inabilitado) and str(motivo_inabilitado).strip() != "":
                st.warning(f"**Motivo registrado:** {motivo_inabilitado}")
            else:
                st.info("**Motivo:** O município não atingiu o valor mínimo do VAAR ou não constava como elegível no relatório de receitas.")
                
            st.markdown("### 💰 Valor Estimado a Receber: **R$ 0,00**")

# Captura de exceções estruturais (totalmente encostados na esquerda)
except FileNotFoundError:
    st.error("📂 Arquivo 'data/processed/dados_finais_sp.csv' não encontrado. Por favor, execute o `main.py` primeiro para gerar a base.")
except Exception as e:
    st.error(f"❌ Ocorreu um erro no aplicativo: {e}")