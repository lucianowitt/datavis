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

# teams
teams = pd.read_csv('data/teams.csv')
teams.head()

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

player = None

def get_figure(title='Graph', data=[], x=None, y=None, xtitle=None, ytitle=None, text=None):
    if (len(data) > 0):
        if (xtitle is None):
            xtitle = x
        if (ytitle is None):
            ytitle = y
        if (text is not None):
            text = data[text].to_list()
        figure = {
            'data': [go.Scatter(x=data[x], y=data[y], text=text)],
            'layout': {
                'title': title,
                'hovermode': 'closest',
                'xaxis': {'title':x, 'nticks': len(data[x])},
                'yaxis': {'title':y, 'nticks': len(data[y])}
            }
        }
    else:
        figure = {'data':[]}
    return figure

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='NBA Players since 1950'),
    html.Div(id='header', style={'width':'50%'}, children=[
        html.B(children='Select a player'),
        dcc.Dropdown(id='player-select', options=[{'label': p, 'value': p} for p in players], multi=False)
    ]),
    html.Div(style={'width':'50%'}),
    html.Div(
        id='photo_area',
        style={'float':'left', 'width':'20%', 'textAlign':'center', 'marginTop': '50px'},
        children=[
            html.Img(id='photo', src='', width=240, height=200, alt='Photo'),
            html.Br(),
            html.Img(id='team_logo', src='', width=150, height=150, alt='Team Logo'),
        ]
    ),
    html.Div(id='graph1_area', style={'float':'left', 'width':'40%'}, children=[
        dcc.Graph(id='graph-pts', figure=get_figure(title='Number of Points'))
    ]),
    html.Div(id='graph2_area', style={'float':'left', 'width':'40%'}, children=[ 
        dcc.Graph(id='graph-efg', figure=get_figure(title='Effective Field Goal %'))
    ])
])

@app.callback([
    dash.dependencies.Output('photo', 'src'),
    dash.dependencies.Output('team_logo', 'src'),
    dash.dependencies.Output('team_logo', 'alt'),
    dash.dependencies.Output('graph-pts', 'figure'),
    dash.dependencies.Output('graph-efg', 'figure')],
    [dash.dependencies.Input('player-select', 'value')])
def update_dashboard(player_name):
    if (player_name is not None):
        player = df[df['Player'] == player_name]
        photo = player['Photo'].to_list()[0]
        team_abbr = player['Tm'].to_list()[0]
        team = teams[teams['Abbr'] == team_abbr]
        logo_path = team['Logo'].to_list()[0]
        logo_alt = str(team['Team'].to_list()[0])
        if (logo_alt == 'nan'):
            logo_alt = team_abbr
        pts = get_figure(title='Number of Points', data=player, x='Year', y='PTS', text='Tm')
        efg = get_figure(title='Effective Field Goal %', data=player, x='Year', y='eFG%', text='Tm')
    else:
        photo = ''
        logo_path = ''
        logo_alt = 'Team Logo'
        pts = get_figure(title='Number of Points')
        efg = get_figure(title='Effective Field Goal %')
    return photo, logo_path, logo_alt, pts, efg

if __name__ == '__main__':
    app.run_server(debug=True)
