import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly as py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os


# Tratamento dos dados
seasons = pd.read_csv('datavis/data/Seasons_Stats.csv')
stats = seasons[['Year','Player','Tm','FG','FG%','FT','FT%','AST','STL','BLK','TOV','PF']]
nulos = pd.DataFrame(stats.isna().sum(), columns=['Nulos']).transpose()
stats = stats.dropna(axis=0)
stats.index = np.arange(1, len(stats) + 1)
stats['Year'] = stats['Year'].astype('int64')
players = stats['Player'].sort_values().unique()
df = stats.copy()
df_pivotado = pd.pivot_table(df,index=["Player"],values=['PF'],aggfunc='sum')

# Css para deixar bonitinho
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Instancia do app e onde colocamos os objetos e as divs
app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
app.layout = html.Div(children=[
                                html.H1(children='Estatísticas NBA'),
                                html.Div(children='''Estatísticas dos jogadores da NBA desde 1978.'''),                                
                                dcc.Dropdown(
                                                id='my-dropdown',
                                                options=[
                                                         {'label': i, 'value': i} for i in df_pivotado.index
                                                ],
                                                multi=True,    
                                                value='James Young'
                                ),
                                dcc.Graph(id='example-graph'),
                                html.Img(id='photo')
                    ])

# Callbacks 

@app.callback(
    dash.dependencies.Output('photo', 'src'),
    [dash.dependencies.Input('my-dropdown', 'value')])
def update_image(selected_player):
    if isinstance(selected_player,list):
        if len(selected_player)==0:
            return ""
        else:
            player = selected_player[0]
    else:
        player = selected_player
    player = player.replace('*','')
    player = player.split(' ')
    lastname = player[-1]
    firstname = player[0]
    return "https://nba-players.herokuapp.com/players/{}/{}".format(lastname,firstname)


@app.callback(
    dash.dependencies.Output('example-graph', 'figure'),
    [dash.dependencies.Input('my-dropdown', 'value')])
def update_figure(selected_player):
    if isinstance(selected_player,list):
        filtered_df = df_pivotado[df_pivotado.index.isin(selected_player)]
    else:
        filtered_df = df_pivotado[df_pivotado.index == selected_player]
    return {
            'data': [
                    {'x': filtered_df.index, 'y': filtered_df.PF, 'type': 'bar', 'name': 'PF'}
            ],
            'layout': {
                'title': 'Pontos por jogador'
            }
    }

if __name__ == '__main__':
    app.run_server(debug=True)