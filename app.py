import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Monitoramento Climático", layout="wide")

# Função para adicionar estilo customizado (imagem de fundo e transparência)
def add_background_image(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        .block-container {{
            background-color: rgba(0, 0, 0, 0.7);
            padding: 20px;
            border-radius: 10px;
        }}
        </style>
        """, unsafe_allow_html=True
    )

# Chamada da função para aplicar o fundo
add_background_image("https://images.pexels.com/photos/209831/pexels-photo-209831.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1")

# Função para buscar os dados climáticos da API com cache a cada 12 horas
@st.cache_data(ttl=86400)  # 24 horas de cache (86400 segundos)
def buscar_dados_climaticos(cidade):
    api_key = "1a82951ed748dbe31ed153645d97c9fd"  # Substitua pela sua chave da API
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={api_key}&lang=pt_br&units=metric"
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        return resposta.json()
    else:
        return None

# Função para processar os dados retornados da API
def processar_dados(dados_climaticos):
    # Extrair os dados principais
    df = pd.json_normalize(dados_climaticos['list'], sep='_')

    # Extraindo a descrição do clima corretamente
    weather_descriptions = [item['weather'][0]['description'] for item in dados_climaticos['list']]
    df['weather_description'] = weather_descriptions

    # Se a chave 'rain' estiver presente, extrair o valor. Se não, definir como 0 (sem chuva)
    df['rain_3h'] = df.get('rain.3h', 0)

    # Selecionando as colunas relevantes para o projeto
    df = df[['dt_txt', 'main_temp', 'weather_description', 'wind_speed', 'main_humidity', 'rain_3h']]
    df.rename(columns={
        'dt_txt': 'Data e Hora',
        'main_temp': 'Temperatura (°C)',
        'weather_description': 'Condição do Tempo',
        'wind_speed': 'Velocidade do Vento (m/s)',
        'main_humidity': 'Umidade (%)',
        'rain_3h': 'Precipitação (mm)'
    }, inplace=True)
    
    return df

# Layout da aplicação
st.title("Monitoramento Climático")

# Lista de cidades da região de Limeira até São Paulo (capital)
cidades = [
    "Limeira", "Americana", "Piracicaba", "Campinas", "Santa Bárbara D'Oeste",
    "Sumaré", "Hortolândia", "Jundiaí", "Valinhos", "Vinhedo", "Itupeva", 
    "Itatiba", "Indaiatuba", "São Paulo"
]

# Campo para selecionar a cidade
cidade = st.selectbox("Selecione a cidade:", cidades)

# Se o usuário selecionar a cidade, buscar os dados
if cidade:
    st.subheader(f"Previsão do tempo para {cidade}")
    
    # Buscar dados da API
    dados_climaticos = buscar_dados_climaticos(cidade)
    
    if dados_climaticos:
        # Processar os dados
        df = processar_dados(dados_climaticos)
        
        # Exibir os dados na interface, ajustando a largura das colunas
        st.dataframe(df, use_container_width=True)
        
        # Gráfico de Temperatura ao longo do tempo
        st.subheader("Previsão da Variação da Temperatura")
        fig_temp = px.line(df, x='Data e Hora', y='Temperatura (°C)', title='Temperatura (°C) ao Longo do Tempo')
        st.plotly_chart(fig_temp, use_container_width=True)

        # Gráfico de Umidade ao longo do tempo
        st.subheader("Previsão da Variação da Umidade")
        fig_humidity = px.line(df, x='Data e Hora', y='Umidade (%)', title='Umidade (%) ao Longo do Tempo')
        st.plotly_chart(fig_humidity, use_container_width=True)

    else:
        st.error("Cidade não encontrada ou erro na API.")
