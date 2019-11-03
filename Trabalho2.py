import numpy as np
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly as py
import plotly.graph_objects as go

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

# Remove totalizadores, que só aparecem quando o jogador jogou em mais de um time no ano
df = df[df['Tm'] != 'TOT']

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


def get_team_data(team_abbr):
    team = teams[teams['Abbr'] == team_abbr]
    team_name = str(team['Team'].to_list()[0])
    if (team_name == 'nan'):
        team_name = team_abbr
        team_logo = ''
    else:
        team_logo = team['Logo'].to_list()[0]
    return team_name, team_logo

def get_bar_chart(title='Graph', data=[], x=None, y=None, xtitle=None, ytitle=None, name=None):
    if (len(data) > 0):
        if (xtitle is None):
            xtitle = x
        if (ytitle is None):
            ytitle = y
        traces = []
        if (name is not None):
            for t, trace in data.groupby(name):
                team_name, _ = get_team_data(t)
                traces.append(go.Bar(x=trace[x], y=trace[y], name=team_name, text=team_name))
        else:
            traces.append(go.Bar(x=data[x], y=data[y]))
        figure = {
            'data': traces,
            'layout': {
                'title': title,
                'hovermode': 'closest',
                'barmode' : 'stack',
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
    html.Div(id='header', style={'width':'100%', 'background-color':'#1b326f'}, children=[
        html.Img(id='nba_logo', src='http://content.sportslogos.net/leagues/thumbs/6.gif', height=80, style={'float':'left'}),
        html.P(style={'color':'white', 'font-size':'50px', 'font-weight':'bold', 'padding-left': '140px'}, children='NBA Players since 1950')
    ]),
    html.Br(),
    html.Div(id='filtros', style={'width':'50%'}, children=[
        html.B(children='Select a player'),
        dcc.Dropdown(id='player-select', options=[{'label': p, 'value': p} for p in players], multi=False)
    ]),
    html.Div(style={'width':'50%'}),
    html.Div(
        id='photo_area',
        style={'float':'left', 'width':'100%', 'textAlign':'center', 'marginTop': '50px'},
        children=[
            html.Img(id='photo', src='', width=200, height=150, alt='Photo', style={'float':'left', 'border':'1px solid gray'}),
            html.Div(id='teams', style={'float':'left', 'width':'80%', 'overflow-x':'auto'}, children=[])
        ]
    ),
    html.Br(),
    html.Div(id='graph1_area', style={'float':'left', 'width':'100%'}, children=[
        dcc.Graph(id='graph-pts', figure=get_bar_chart(title='Number of Points'))
    ])
])

@app.callback([
    dash.dependencies.Output('photo', 'src'),
    dash.dependencies.Output('teams', 'children'),
    dash.dependencies.Output('graph-pts', 'figure')],
    [dash.dependencies.Input('player-select', 'value')])
def update_dashboard(player_name):
    if (player_name is not None):
        player = df[df['Player'] == player_name]
        photo = player['Photo'].to_list()[0]
        team_abbrs = player['Tm'].unique()
        team_logos = []
        for team_abbr in team_abbrs:
            logo_alt, logo_path = get_team_data(team_abbr)
            if (logo_path == ''):
                team_logos.append(html.Img(src='', width=150, height=150, alt=team_abbr, style={'float':'left', 'border':'1px solid gray', 'margin-left':'10px' }))
            else:
                team_logos.append(html.Img(src=logo_path, width=150, height=150, alt=logo_alt, style={'float':'left', 'border':'1px solid gray', 'margin-left':'10px' }))
        pts = get_bar_chart(title='Number of Points', data=player, x='Year', y='PTS', name='Tm')
    else:
        photo = ''
        team_logos = []
        pts = get_bar_chart(title='Number of Points')
    return photo, team_logos, pts

if __name__ == '__main__':
    app.run_server(debug=True)
