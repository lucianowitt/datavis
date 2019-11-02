import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly as py
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# dataset baixado de "https://www.kaggle.com/drgilermo/nba-players-stats/download" para a pasta "data"
# dicionário de dados no arquio "dicionario_dados.txt"

df = pd.read_csv('data/Seasons_Stats.csv', index_col=0)
print(df.shape)
df.head()

# Remove linhas em que o ano é nulo (na verdade nessas linhas todas coluans são nulas)
df = df[pd.notnull(df['Year'])]
print(df.shape)
df.head()

# Confere o número de valores nulos para cada coluna
nulos = pd.DataFrame(df.isna().sum(), columns=['Nulos']).transpose()
nulos

df['Year'] = df['Year'].astype('int64')
df.head()

players = df['Player'].sort_values().unique()
print('Jogadores:', len(players))

app = dash.Dash(__name__)

player_name = 'James Young'
player = df[df['Player'] == player_name]

player

app.layout = html.Div(children=[
    html.H1(children='NBA Players since 1950'),
    dcc.Graph(
        id='example-graph-2',
        figure={
            'data': [
                {'x': player['Year'], 'y': player['PTS'], 'type': 'bar', 'name': player_name}
            ]
        }
    )
])
if __name__ == '__main__':
    app.run_server(debug=True)
