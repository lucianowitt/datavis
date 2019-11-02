
from IPython import get_ipython
import chart_studio.plotly as py
#import plotly.chart_studio.plotly as py
import plotly.graph_objs as go
import plotly.offline as offline

offline.init_notebook_mode(connected=True)


from datetime import datetime
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like

#import pandas_datareader.data as web


ds = pd.read_csv('C:\\PUCRS\\VD\\seasons_stats_player_pts_accum.csv', index_col =['player','num_season'])

top_player_pts = list(pd.DataFrame(ds.groupby(['player']).agg({'tot_pts':'sum'}).sort_values('tot_pts', ascending=False)[:5]).index)

#type(top_player_pts)

#ds[(ds['player'] == 'Kareem Abdul-Jabbar*')]

ds_top_player = ds.loc[top_player_pts]


ds_top_player['tot_pts_acum'] = ds_top_player.groupby(['player'])['tot_pts'].cumsum()
ds_top_player['num_season_col'] = ds_top_player.index.get_level_values('num_season') 

#ds_top_player.loc['Kareem Abdul-Jabbar*'].num_season_col

ds_top_player.head()

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


trace = []
nome_title = 'Top Jogadores da NBA'

fig = go.Figure()

for i,nome_jogador in enumerate(top_player_pts):
    print(top_player_pts[i],plotly_color[i])
    fig.add_trace(go.Scatter(x=ds_top_player.loc[top_player_pts[i]].num_season_col,
                            y=ds_top_player.loc[top_player_pts[i]].tot_pts_acum,
                            name = nome_jogador,
                            line = dict(color = plotly_color[i])
                            )
                )

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
            y0=0.05,
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
            y0=0.05,
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




fig.update_traces(
    hoverinfo="name+x+text",
    line={"width": 2.0},
    marker={"size": 8},
    mode="lines+markers",
    showlegend=True
)

# Update layout
fig.update_layout(
    dragmode="zoom",
    hovermode="x",
    legend=dict(traceorder="reversed"),
    height=800,
    template="plotly_white",
    margin=dict(
        t=100,
        b=100
    ),
)

#offline.iplot(fig)
fig.show()




# ### Range slider
# We can add a range slider to an axis to allow the range of data displayed to be restricted
'''
layout = dict(title = nome_title,              
              xaxis = dict(rangeslider=dict(),
                           type='date')
             )
'''
layout = dict(title = nome_title,              
              rangeslider=dict(visible=True)
             )

fig = dict(data=data, 
           layout=layout)

offline.iplot(fig)

#%% [markdown]
# #### Range Selector
# In addition to range sliders, we can include rangeselector buttons where we can quickly restrict the plotted range:
# * <b>step</b> is a time interval to set the range. Can be year, month, day, hour, minute, second and all
# * <b>stepmode</b> value can be 'todate' or 'backward'. 
#  * A value of 'todate' with a step of 'month' means that the left of the range slider will move to the start of the month (and the right will remain where it is)
#  * A value of 'backward' will keep the right slider where it is, and shift the left slider back by the value of count. In our example, the left slider will move back 6 months from the position of the right slider

#%%
layout = dict(
    
    title = 'Amazon Stock Price Data ',
    
    xaxis = dict(rangeselector = dict(buttons = list([dict(count = 1,
                                                           label = '1m',
                                                           step = 'month',
                                                           stepmode = 'todate'),
                                                  
                                                      dict(count = 6,
                                                           label = '6m',
                                                           step = 'month',
                                                           stepmode = 'backward'),
                                                  
                                                      dict(step = 'all')])
                                     ),
                 
                 rangeslider=dict(),
                 type='date'
    )
)


#%%
fig = dict(data=data, 
           layout=layout)

offline.iplot(fig)


#%%



