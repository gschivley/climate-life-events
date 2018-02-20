# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import os
from random import randint

fn = 'https://raw.githubusercontent.com/gschivley/climate-life-events/master/iamc_db.csv'
df = pd.read_csv(fn)
df['climate'] = df['Scenario'].str.split('-').str[-1]
climates = df['climate'].unique()
years = pd.to_datetime(df.columns[6:-1], yearfirst=True)

fn = 'https://raw.githubusercontent.com/gschivley/climate-life-events/master/GISS_temps.csv'
hist = pd.read_csv(fn)
hist['datetime'] = pd.to_datetime(hist['datetime'], yearfirst=True)

# Adjust SSP temps to match GISS in 2010 so they share the same baseline
year_2010 = pd.to_datetime('2010-01-01', yearfirst=True)
GISS_2010 = hist.loc[hist['datetime'] == year_2010, 'temp'].values[0]
diff_2010 = df.loc[:, '2010'].values[0] - GISS_2010
df.loc[:, '2005':'2100'] -= diff_2010

# Colors from tab10 palette
# colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
colors = ['#d62728', '#ff7f0e', '#1f77b4']

scenario_map = {
    'Baseline': 'High',
    '60': 'High',
    '45': 'Mid',
    '34': 'Mid',
    '26': 'Low'
}

df['name'] = df['climate'].map(scenario_map)

data = []
trace = {
    'x': hist.loc[hist['datetime'].dt.year <=2010, 'datetime'],
    'y': hist.loc[hist['datetime'].dt.year <=2010, 'temp'],
    'type': 'scatter',
    'mode': 'lines',
    'name': 'Historical record',
    'line': {'color': 'rgb(33, 33, 33)'}
}
data.append(trace)

# for idx, climate in enumerate(climates):
for idx, climate in enumerate(['High', 'Mid', 'Low']):
    # dfs[climate] = df.loc[df['climate'] == climate, '2010':'2100']
    trace = {
        'x': years,
        # 'y': df.loc[df['climate'] == climate, '2010':'2100'].mean(),
        'y': df.loc[df['name'] == climate, '2010':'2100'].mean(),

        # 'fill': 'tonexty',
        'showlegend': False,
        'type': 'scatter',
        'mode': 'lines',
        'name': climate,
        'line': {'color': 'rgb(33, 33, 33)'}
    }
    data.append(trace)

# for idx, climate in enumerate(climates):
for idx, climate in enumerate(['High', 'Mid', 'Low']):
    trace = {
        'x': years,
        # 'y': df.loc[df['climate'] == climate, '2010':'2100'].min(),
        'y': df.loc[df['name'] == climate, '2010':'2100'].min(),
        # 'fill': 'tonexty',
        'showlegend': False,
        'type': 'scatter',
        'mode': 'lines',
        'name': 'min {}'.format(climate),
        'line': {'color': colors[idx],
                 'width': 0.5}
    }
    data.append(trace)

    trace = {
        'x': years,
        # 'y': df.loc[df['climate'] == climate, '2010':'2100'].max(),
        'y': df.loc[df['name'] == climate, '2010':'2100'].max(),
        'type': 'scatter',
        'fill': 'tonexty',
        # 'showlegend': False,
        'mode': 'lines',
        # 'name': 'max {}'.format(climate),
        'name': climate,
        'line': {'color': colors[idx],
                 'width': 0.5}
    }
    data.append(trace)



app = dash.Dash(csrf_protect=False)
server = app.server
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))

app.layout = html.Div(children=[
    html.H1(children='Climate change and life events'),

    html.P([
        html.Label('Year your mother was born'),
        # dcc.Input(id='mother_birth', value=1952, type='number'),
        dcc.Dropdown(
            id='mother_birth',
            options=[{'label': i, 'value':i} for i in range(1900, 2018)],
            value=1950
        )
    ],
    style={'width': '250px'}),

    html.P([
        html.Label('Year you were born'),
        # dcc.Input(id='self_birth',value=1982, type='number'),
        dcc.Dropdown(
            id='self_birth',
            options=[{'label': i, 'value':i} for i in range(1900, 2018)],
            value=1980
        )
    ],
    style={'width': '250px'}),

    html.P([
        html.Label('Year your child was born'),
        # dcc.Input(id='child_birth', value=0, type='number'),
        dcc.Dropdown(
            id='child_birth',
            options=[{'label': i, 'value':i} for i in range(1900, 2018)],
            value=2010
        )
    ],
    style={'width': '250px'}),

    html.Div([
        dcc.Graph(
            id='example-graph',
            # figure={
            #     'data': data,
            #     'layout': {
            #         'title': 'Dash Data Visualization',
            #         'annotations': annotation
            #     }
            # }
        )
        ],
        style={'width': '90%', 'margin-right': 'auto', 'margin-left': 'auto'}),


        # dcc.Markdown('''
        # Data from:
        #
        # [SSP Public Database (Version 1.1)](https://tntcat.iiasa.ac.at/SspDb)
        # '''),
        dcc.Markdown('Inspired by [Sophie Lewis](https://twitter.com/aviandelights/status/870485031973658624), who created the figure below.'),
        html.Img(src='https://pbs.twimg.com/media/DBSVdWFVwAAxaMy.jpg',
                 style={'width': '50%', 'margin-right': 'auto', 'margin-left': 'auto'})
])

@app.callback(
    dash.dependencies.Output('example-graph', 'figure'),
    [dash.dependencies.Input('mother_birth', 'value'),
    dash.dependencies.Input('self_birth', 'value'),
    dash.dependencies.Input('child_birth', 'value')])
def update_figure(mother_year, self_year, child_year):
    # y_value = {}
    # for key, year in zip(['mother', 'self', 'child'],
    #                      [mother_year, self_year, child_year]):
    #     if year < 2010:
    #         y_value[key] =

    annotation = [
            {
                "yanchor": "bottom",
                "xref": "x",
                "xanchor": "center",
                "yref": "y",
                "text": "My mother was born",
                "y": 0.75,
                "x": '{}-01-01'.format(mother_year),
                "showarrow": True
            },
            {
                "yanchor": "bottom",
                "xref": "x",
                "xanchor": "center",
                "yref": "y",
                "text": "I was born",
                "y": 1,
                "x": '{}-01-01'.format(self_year),
                "showarrow": True
            },
            {
                "yanchor": "bottom",
                "xref": "x",
                "xanchor": "center",
                "yref": "y",
                "text": "My child was born",
                "y": 1.75,
                "x": '{}-01-01'.format(child_year),
                "showarrow": True
            },
            {
                "yanchor": "bottom",
                "xref": "x",
                "xanchor": "center",
                "yref": "y",
                "text": "My child finishes high school",
                "y": 2.25,
                "x": '{}-01-01'.format(child_year+18),
                "showarrow": True
            },
            {
                "yanchor": "bottom",
                "xref": "x",
                "xanchor": "center",
                "yref": "y",
                "text": "My first grandchild born",
                "y": 3.5,
                "x": '{}-01-01'.format(child_year+18+15),
                "showarrow": True
            }
            ]

    if child_year < self_year:
        annotation = annotation[:-3]
    figure={
        'data': data,
        'layout': {
            # 'title': 'Dash Data Visualization',
            'annotations': annotation,
            'hovermode': 'closest',
            'yaxis': {
                'ticksuffix': '°C',
                'title': 'Observed & Forecast Temperature Anomaly',
                'showgrid': False,
            },
            "font": {
                "family": "Roboto",
                "size": 14
            }
        }
    }

    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
