import numpy as np
import pandas as pd
import dash
import dash_table
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

# Transforma coluna Year de float para int
df['Year'] = df['Year'].astype('int64')

# Remove asteriscos dos nomes dos jogadores
df['Player'] = df['Player'].str.replace('*','')

# Cria coluna dos links para as fotos
def build_photo_link(name):
    name_parts = name.split(' ')
    first = name_parts[0]
    last = name_parts[1]
    photo_link = 'https://nba-players.herokuapp.com/players/' + last + '/' + first
    return photo_link

df['Photo'] = df['Player'].apply(build_photo_link)

# Cria lista dos nomes de jogadores
players = df['Player'].sort_values().unique()
print('Jogadores:', len(players))

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='NBA Players since 1950'),
    dcc.Dropdown(
        id='player-select',
        options=[{'label': p, 'value': p} for p in players],
        multi=False
    ),
    dcc.Graph(id='graph-pts', figure={'data': []}),
    dcc.Graph(id='graph-efg', figure={'data': []}),
    html.Img(id='photo', src='', alt='Photo not available'),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=[]
    )
])

@app.callback([
    dash.dependencies.Output('photo', 'src'),
    dash.dependencies.Output('graph-pts', 'figure'),
    dash.dependencies.Output('graph-efg', 'figure'),
    dash.dependencies.Output('table', 'data')],
    [dash.dependencies.Input('player-select', 'value')])
def update_dashboard(player_name):
    if (player_name is not None):
        player = df[df['Player'] == player_name]
        photo = player['Photo'].to_list()[0]
        pts = {'data': [{'x': player['Year'], 'y': player['PTS'], 'type': 'line', 'name': player_name}]}
        efg = {'data': [{'x': player['Year'], 'y': player['eFG%'], 'type': 'line', 'name': player_name}]}
        table_data = player.to_dict('records')
    else:
        photo = ''
        pts = {'data':[]}
        efg = {'data':[]}
        table_data = []
    return photo, pts, efg, table_data

if __name__ == '__main__':
    app.run_server(debug=True)
