import folium
import pandas as pd

def gerar_mapa_status(df_final):
    """
    df_final deve conter: ['Município_Join', 'latitude', 'longitude', 'recebeu_valor']
    'recebeu_valor' deve ser booleano (True/False)
    """
    print("🗺️ Gerando mapa de status de recebimento 2025...")
    
    # Centralizado no estado de SP
    mapa = folium.Map(location=[-23.55, -46.63], zoom_start=7, tiles='cartodbpositron')

    for _, linha in df_final.iterrows():
        # Define a cor baseada no status
        cor = 'green' if linha['recebeu_valor'] else 'red'
        status_texto = "Recebeu Repasse" if linha['recebeu_valor'] else "Inabilitado (Não recebeu)"
        
        folium.CircleMarker(
            location=[linha['latitude'], linha['longitude']],
            radius=5,
            color=cor,
            fill=True,
            fill_color=cor,
            fill_opacity=0.7,
            popup=f"<b>Cidade:</b> {linha['Município_Join']}<br><b>Status:</b> {status_texto}",
        ).add_to(mapa)

    mapa.save('output/mapa_status_2025.html')
    print("✅ Mapa salvo em 'output/mapa_status_2025.html'")