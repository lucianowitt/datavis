import numpy as np
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly as py
import plotly.graph_objects as go

# ----------------------------------------------------------------------------------------------------------------------------------
# TRATAMENTO DOS DADOS
# ----------------------------------------------------------------------------------------------------------------------------------

# dataset baixado de "https://www.kaggle.com/drgilermo/nba-players-stats/download" para a pasta "data"
# dicionário de dados no arquivo "dicionario_dados.txt"

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

# Remove totalizadores, que só aparecem quando o jogador
# jogou em mais de um time no mesmo ano
df = df[df['Tm'] != 'TOT']

# ----------------------------------------------------------------------------------------------------------------------------------
# PLAYER STATS 
# ----------------------------------------------------------------------------------------------------------------------------------

# teams
teams = pd.read_csv('teams.csv')
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

# ----------------------------------------------------------------------------------------------------------------------------------
# TOP 5 PLAYERS
# ----------------------------------------------------------------------------------------------------------------------------------

ds_player = pd.DataFrame(df.groupby(['Player','Year']).agg({'Year':'min','PTS':'sum'}))[['PTS']]
ds_player.reset_index(level='Year',inplace=True) 
ds_player['Year_Ini'] = ds_player.groupby(['Player'])[['Year']].min().astype(int)
ds_player['Qtd'] = 1
ds_player['num_season_col'] = ds_player.groupby(['Player'])['Qtd'].cumsum().astype(int)
ds_player['tot_pts_acum'] = ds_player.groupby(['Player'])['PTS'].cumsum().astype(int)

top_player_pts = list(pd.DataFrame(ds_player.groupby(['Player']).agg({'PTS':'sum'}).sort_values('PTS', ascending=False)[:50]).index)

ds_top_player = ds_player.loc[top_player_pts]

top_5_traces_1 = []
for i, nome_jogador in enumerate(top_player_pts[0:5]):
    print(nome_jogador, i)
    top_5_traces_1.append(
        go.Scatter(
            x = ds_top_player.loc[nome_jogador].num_season_col.astype(int),
            y = ds_top_player.loc[nome_jogador].tot_pts_acum.astype(int),
            name = nome_jogador,
            text = ds_top_player.loc[nome_jogador].Year.astype(int)
        )
    )

top_5_layout_1 = {
    'hoverinfo': "name+x+text",
    'line': {"width": 2.0},
    'marker': {"size": 8},
    'mode': "lines+markers",
    'showlegend': True,
    'dragmode': "zoom",
    'hovermode': "x",
    'legend': dict(traceorder="reversed"),
    'height': 1200,
    'template': "plotly_white",
    'margin': dict(t=100, b=100),
    'shapes': [
        go.layout.Shape(
            fillcolor="rgba(63, 81, 181, 0.2)",
            line={"width": 0}, type="rect",
            x0=0, x1=7, xref="x", y0=0.02, y1=0.95, yref="paper"
        ),
        go.layout.Shape(
            fillcolor="rgba(76, 175, 80, 0.1)",
            line={"width": 0}, type="rect",
            x0=7, x1=14, xref="x", y0=0.02, y1=0.95, yref="paper"
        )
    ],
    'xaxis': go.layout.XAxis(
        autorange=True, range=[0, 20],
        rangeslider=dict(autorange=True, range=[0, 20]),
        type="linear", title_text='Number of Seasons', tick0=1, dtick=1
    ),
    'yaxis': go.layout.YAxis(title_text='Pontos', tick0=2000, dtick=2000
    ),
    'annotations': [
        go.layout.Annotation(
            x=7, y=0,
            arrowcolor="rgba(63, 81, 181, 0.2)", arrowsize=0.3,
            ax=0, ay=30,
            text="First 7 seasons",
            xref="x", yanchor="bottom", yref="y"
        ),
        go.layout.Annotation(
            x=14, y=0,
            arrowcolor="rgba(76, 175, 80, 0.1)", arrowsize=0.3,
            ax=0, ay=30,
            text="First 14 seasons",
            xref="x", yanchor="bottom", yref="y"
        )
    ]
}

top_5_traces_2 = []
for i, nome_jogador in enumerate(top_player_pts[0:5]):
    print(nome_jogador, i)
    top_5_traces_2.append(
        go.Bar(
            x=ds_top_player.loc[nome_jogador].num_season_col.astype(int),
            y=ds_top_player.loc[nome_jogador].tot_pts_acum.astype(int),
            name=nome_jogador,
            text=ds_top_player.loc[nome_jogador].Year.astype(int),
            textposition='auto'
        )
    )

top_5_layout_2 = {
    'title': 'Total Points per Season',
    'xaxis_tickfont_size': 16,
    'yaxis': dict(title='Points', titlefont_size=16, tickfont_size=14),
    'legend': dict(x=0, y=1.0, bgcolor='rgba(255, 255, 255, 0)', bordercolor='rgba(255, 255, 255, 0)'),
    'barmode': 'group',
    'bargap': 0.5, # gap between bars of adjacent location coordinates.
    'bargroupgap': 0.05, # gap between bars of the same location coordinate.
    'xaxis': go.layout.XAxis(
        autorange=True,
        range=[0, 20],
        rangeslider=dict(autorange=True, range=[0, 20]),
        type="linear",
        tick0=1, dtick=1
    ),
    'marker_line_color': 'rgb(8,48,107)',
    'marker_line_width': 1.0,
    'opacity': 0.95
}

# ----------------------------------------------------------------------------------------------------------------------------------
# PLAYER COMPARISON
# ----------------------------------------------------------------------------------------------------------------------------------

df_pivotado = pd.pivot_table(df,index=["Player"],values=['PF'],aggfunc='sum')

# ----------------------------------------------------------------------------------------------------------------------------------
# LAYOUT
# ----------------------------------------------------------------------------------------------------------------------------------

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.Div(id='header', style={'width':'100%', 'height':'80px', 'background-color':'white'}, children=[
        html.Img(id='nba_logo', src='http://content.sportslogos.net/leagues/thumbs/6.gif', height=80, style={'float':'left'}),
        html.P(style={'color':'#1b326f', 'font-size':'40px', 'font-weight':'bold', 'padding-left': '140px', 'padding-top':'10px'}, children='NBA Players since 1950')
    ]),
    html.Br(),
    dcc.Tabs(id='tabs', children=[
        dcc.Tab(label='Player Stats', children=[
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
                dcc.Graph(id='graph-pts', figure=get_bar_chart(title='Points per Year'))
            ])
        ]),
        dcc.Tab(label='Top Players', children=[
            dcc.Graph(
                id='graph-top-5-1',
                figure={
                    'data': top_5_traces_1,
                    'layout': top_5_layout_1
                }
            ),
            dcc.Graph(
                id='graph-top-5-2',
                figure={
                    'data': top_5_traces_2,
                    'layout': top_5_layout_2
                }
            )
        ]),
        dcc.Tab(label='Player Comparison', children=[
            html.B(children='Select players'),
            dcc.Dropdown(id='player-comparison-select', options=[{'label': p, 'value': p} for p in players], multi=True),
            html.Div(id='player-comparison-graph-area', style={'float':'left', 'width':'100%'}, children=[
                dcc.Graph(id='player-comparison-graph', figure={'data': [], 'layout': {'title': 'Points per Player'}})
            ])
        ])
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
        pts = get_bar_chart(title='Points per Year', data=player, x='Year', y='PTS', name='Tm')
    else:
        photo = ''
        team_logos = []
        pts = get_bar_chart(title='Points per Year')
    return photo, team_logos, pts

@app.callback(
    dash.dependencies.Output('player-comparison-graph', 'figure'),
    [dash.dependencies.Input('player-comparison-select', 'value')])
def update_figure(selected_player):
    if isinstance(selected_player,list):
        filtered_df = df_pivotado[df_pivotado.index.isin(selected_player)]
    else:
        filtered_df = df_pivotado[df_pivotado.index == selected_player]
    return {
        'data': [{'x': filtered_df.index, 'y': filtered_df.PF, 'type': 'bar', 'name': 'PF'}],
        'layout': {'title': 'Points per Player'}
    }

if __name__ == '__main__':
    app.run_server(debug=True)
