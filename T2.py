
from IPython import get_ipython
import chart_studio.plotly as py
#import plotly.chart_studio.plotly as py
import plotly.graph_objs as go
import plotly.offline as offline
import plotly.express as px

offline.init_notebook_mode(connected=True)


from datetime import datetime
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like


ds = pd.read_csv('C:\\PUCRS\\VD\\Seasons_Stats.csv',sep=";")

ds.drop(['Unnamed: 0'], axis=1, inplace=True)

ds_player = pd.DataFrame(ds.groupby(['Player','Year']).agg({'Year':'min','PTS':'sum'}))[['PTS']]

ds_player.reset_index(level='Year',inplace=True) 

ds_player['Year_Ini'] = ds_player.groupby(['Player'])[['Year']].min().astype(int)
ds_player['Qtd'] = 1
#ds_player['num_season_col'] = 1 + ds_player['Year'].astype(int) - ds_player['Year_Ini']
ds_player['num_season_col'] = ds_player.groupby(['Player'])['Qtd'].cumsum().astype(int)
ds_player['tot_pts_acum'] = ds_player.groupby(['Player'])['PTS'].cumsum().astype(int)

top_player_pts = list(pd.DataFrame(ds_player.groupby(['Player']).agg({'PTS':'sum'}).sort_values('PTS', ascending=False)[:50]).index)


ds_top_player = ds_player.loc[top_player_pts]

#ds_top_player['tot_pts_acum'] = ds_top_player.groupby(['player'])['tot_pts'].cumsum()
#ds_top_player['num_season_col'] = ds_top_player.index.get_level_values('num_season') 

#ds_top_player.loc['Michael Jordan*']

#ds_top_player.head()

plotly_color = ['#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
#    '#8c564b',  # chestnut brown
#    '#e377c2',  # raspberry yogurt pink
#    '#7f7f7f',  # middle gray
#    '#bcbd22',  # curry yellow-green
#    '#17becf'   # blue-teal
]

# #### Plot a graph of high price vs date
# This will produce a time series

nome_title = 'Top Jogadores da NBA'

fig = go.Figure()

for i,nome_jogador in enumerate(top_player_pts[0:5]):
    print(nome_jogador,i)
    fig.add_trace(go.Scatter(x=ds_top_player.loc[nome_jogador].num_season_col.astype(int),
                             y=ds_top_player.loc[nome_jogador].tot_pts_acum.astype(int),
                             name = nome_jogador,
                             text=ds_top_player.loc[nome_jogador].Year.astype(int)
                             #line = dict(color = plotly_color[i])
                            )
                )

#fig.show()

# Add annotations
fig.update_layout(
    annotations=[
        go.layout.Annotation(
            x=7,
            y=0,
            arrowcolor="rgba(63, 81, 181, 0.2)",
            arrowsize=0.3,
            ax=0,
            ay=30,
            text="Primeiras 7 temporadas",
            xref="x",
            yanchor="bottom",
            yref="y"
        ),
        go.layout.Annotation(
            x=14,
            y=0,
            arrowcolor="rgba(76, 175, 80, 0.1)",
            arrowsize=0.3,
            ax=0,
            ay=30,
            text="Primeiras 14 temporadas",
            xref="x",
            yanchor="bottom",
            yref="y"
        )
    ],
)

fig.update_traces(
    hoverinfo="name+x+text",
    line={"width": 2.0},
    marker={"size": 8},
    mode="lines+markers",
    showlegend=True
)


# Add shapes
fig.update_layout(
    shapes=[
        go.layout.Shape(
            fillcolor="rgba(63, 81, 181, 0.2)",
            line={"width": 0},
            type="rect",
            x0=0,
            x1=7,
            xref="x",
            y0=0.02,
            y1=0.95,
            yref="paper"
        ),
        go.layout.Shape(
            fillcolor="rgba(76, 175, 80, 0.1)",
            line={"width": 0},
            type="rect",
            x0=7,
            x1=14,
            xref="x",
            y0=0.02,
            y1=0.95,
            yref="paper"
        )
    ]
)

# Update axes
fig.update_layout(
    xaxis=go.layout.XAxis(
        autorange=True,
        range=[0, 20],
        rangeslider=dict(
            autorange=True,
            range=[0, 20]
        ),
        type="linear"
    )
)


fig.update_xaxes(title_text='Quantidade de Temporadas',tick0=1, dtick=1)
fig.update_yaxes(title_text='Pontos',tick0=2000, dtick=2000)


# Update layout
fig.update_layout(
    dragmode="zoom",
    hovermode="x",
    legend=dict(traceorder="reversed"),
    height=1200,
    template="plotly_white",
    margin=dict(
        t=100,
        b=100
    ),
)


num_jogador_extra = 40
top_player_pts[num_jogador_extra]
fig.add_trace(go.Scatter(x=ds_top_player.loc[top_player_pts[num_jogador_extra]].num_season_col.astype(int),
                         y=ds_top_player.loc[top_player_pts[num_jogador_extra]].tot_pts_acum.astype(int),
                         name = top_player_pts[num_jogador_extra],
                         text=ds_top_player.loc[top_player_pts[num_jogador_extra]].Year.astype(int),
                        )
                )


#offline.iplot(fig)
fig.show()

#ds_top_player[0:5]




fig = go.Figure()

for i,nome_jogador in enumerate(top_player_pts[0:5]):
    print(nome_jogador,i)
    fig.add_trace(go.Bar(name=nome_jogador, 
                        x=ds_top_player.loc[nome_jogador].num_season_col.astype(int), 
                        y=ds_top_player.loc[nome_jogador].PTS.astype(int),
                        text=ds_top_player.loc[nome_jogador].PTS.astype(int),
                        textposition='auto',
                        )
                        )


fig.update_traces(marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.0, opacity=0.95)

# Change the bar mode
fig.update_layout(
    title='Total de Pontos por Temporada',
    xaxis_tickfont_size=16,
    yaxis=dict(
        title='Pontos',
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    barmode='group',
    bargap=0.5, # gap between bars of adjacent location coordinates.
    bargroupgap=0.05 # gap between bars of the same location coordinate.
)

fig.update_layout(
    xaxis=go.layout.XAxis(
        autorange=True,
        range=[0, 20],
        rangeslider=dict(
            autorange=True,
            range=[0, 20]
        ),
        type="linear"
    )
)

fig.update_xaxes(tick0=1, dtick=1)


fig.show()


