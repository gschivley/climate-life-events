# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
# import os
# from random import randint
from bisect import bisect_left
from datetime import datetime

currentYear = datetime.now().year

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
colors = ['#d62728', '#ff7f0e', '#1f77b4'][::-1]

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
    'x': hist.loc[(hist['datetime'].dt.year <= 2010) &
                  (hist['datetime'].dt.year > 1899), 'datetime'],
    'y': hist.loc[(hist['datetime'].dt.year <= 2010) &
                  (hist['datetime'].dt.year > 1899), 'temp'],
    'type': 'scatter',
    'mode': 'lines',
    'name': 'Historical record',
    'line': {'color': 'rgb(33, 33, 33)'}
}
data.append(trace)

# for idx, climate in enumerate(climates):
for idx, climate in enumerate(['Low', 'Mid', 'High']):
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
for idx, climate in enumerate(['Low', 'Mid', 'High']):
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
        'name': climate,
        'line': {'color': colors[idx],
                 'width': 0.5}
    }
    data.append(trace)



app = dash.Dash(csrf_protect=False)
# app.config.supress_callback_exceptions=True
app.css.append_css({'external_url':
                    'https://cdn.rawgit.com/gschivley/8040fc3c7e11d2a4e7f0589ffc829a02/raw/8daf84050707365c5e266591d65232607f802a43/dash.css'
                    # 'https://rawgit.com/gschivley/8040fc3c7e11d2a4e7f0589ffc829a02/raw/8daf84050707365c5e266591d65232607f802a43/dash.css'

                    })
server = app.server
# server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))

app.layout = html.Div(children=[
    html.H1(
        children='Climate change and life events',
        style={'text-align': 'center'}
    ),

    html.P([
        html.Label('Year your mother was born'),
        # dcc.Input(id='mother_birth', value=1952, type='number'),
        dcc.Dropdown(
            id='mother_birth',
            options=[{'label': i, 'value':i} for i in range(1900, 2018)],
            value=1950
        )
    ],
    style={'width': '250px', 'margin-right': 'auto',
           'margin-left': 'auto', 'text-align': 'center'}),
    # 'margin-left': '40px', 'text-align': 'center'}),

    html.P([
        html.Label('Year you were born'),
        # dcc.Input(id='self_birth',value=1982, type='number'),
        dcc.Dropdown(
            id='self_birth',
            options=[{'label': i, 'value':i} for i in range(1920, 2018)],
            value=1980
        )
    ],
    style={'width': '250px', 'margin-right': 'auto',
           'margin-left': 'auto', 'text-align': 'center'}),

    html.P([
        html.Label('Year your child was born'),
        # dcc.Input(id='child_birth', value=0, type='number'),
        dcc.Dropdown(
            id='child_birth',
            options=[{'label': i, 'value':i}
                     for i in range(1940, currentYear+1)],
            value=2010
        )
    ],
    style={'width': '250px', 'margin-right': 'auto',
           'margin-left': 'auto', 'text-align': 'center'}),
    html.Div(
    [
        dcc.Graph(
            id='example-graph',
            config={
                'modeBarButtonsToRemove': ['autoScale2d', 'select2d', 'zoom2d',
                                           'pan2d', 'toggleSpikelines',
                                           'hoverCompareCartesian',
                                           'zoomOut2d', 'zoomIn2d',
                                           'hoverClosestCartesian',
                                           # 'sendDataToCloud',
                                           'resetScale2d']
            }
        )
        ],
        # style={'width': '75%', 'margin-right': 'auto', 'margin-left': 'auto'}
        ),

        dcc.Markdown('Created by [Greg Schivley](https://twitter.com/gschivley) with help from [Ben Noll](https://twitter.com/BenNollWeather)'),
        dcc.Markdown('Inspired by [Sophie Lewis](https://twitter.com/aviandelights/status/870485031973658624)'),
        dcc.Markdown('Find out more about the data, get the code, or help improve this figure on [GitHub](https://github.com/gschivley/climate-life-events)')
        # html.Img(src='https://pbs.twimg.com/media/DBSVdWFVwAAxaMy.jpg',
        #          style={'width': '50%', 'margin-right': 'auto', 'margin-left': 'auto'})
],
className='container'
# style={'width': '600px', 'margin-right': 'auto', 'margin-left': 'auto'}
)

def takeClosest(myList, myNumber):
    """
    From https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value

    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    return after
    # if after - myNumber < myNumber - before:
    #    return after
    # else:
    #    return before

def annotation_height(year):
    """
    Get the height for an annotation.
    Historical is easy - we have data for every year.
    After 2010 is harder - need to find the closest year to SSP values
    """
    if year < 2010:
        temp = hist.loc[hist['datetime'].dt.year == year, 'temp'].values[0]
    else:
        close_year = str(takeClosest(years.year, year))

        temp = df.loc[:, close_year].max()

    return temp + 0.5

@app.callback(
    dash.dependencies.Output('example-graph', 'figure'),
    [dash.dependencies.Input('mother_birth', 'value'),
    dash.dependencies.Input('self_birth', 'value'),
    dash.dependencies.Input('child_birth', 'value')])
def update_figure(mother_year, self_year, child_year):

    annotation = [
            {
                "yanchor": "bottom",
                "xref": "x",
                "xanchor": "center",
                "yref": "y",
                "text": "My mother<br>was born",
                "y": annotation_height(mother_year), #0.75,
                "x": '{}-01-01'.format(mother_year),
                "ay": -40,
                "ax": 0,
                "showarrow": True,
                'arrowhead': 2,
            },
            {
                "yanchor": "bottom",
                "xref": "x",
                "xanchor": "center",
                "yref": "y",
                "text": "I was born",
                "y": annotation_height(self_year), #1,
                "x": '{}-01-01'.format(self_year),
                "ay": -40,
                "ax": 0,
                "showarrow": True,
                'arrowhead': 2,
            },
            {
                "yanchor": "bottom",
                "xref": "x",
                "xanchor": "center",
                "yref": "y",
                "text": "My child<br>was born",
                "y": annotation_height(child_year), #1.75,
                "x": '{}-01-01'.format(child_year),
                "ay": -40,
                "ax": 0,
                "showarrow": True,
                'arrowhead': 2,
            },
            {
                "yanchor": "bottom",
                "xref": "x",
                "xanchor": "center",
                "yref": "y",
                "text": "My child<br>finishes<br>high school",
                "y": annotation_height(child_year+18), #2.25,
                "x": '{}-01-01'.format(child_year+18),
                "ay": -60,
                "ax": 0,
                "showarrow": True,
                'arrowhead': 2,
            },
            {
                "yanchor": "bottom",
                "xref": "x",
                "xanchor": "center",
                "yref": "y",
                "text": "My first<br>grandchild<br>is born",
                "y": annotation_height(child_year+18+18), #3.0,
                "x": '{}-01-01'.format(child_year+18+18),
                "ay": -100,
                "ax": 0,
                "showarrow": True,
                'arrowhead': 2,
            },
            {
                "yanchor": "bottom",
                "xref": "x",
                "xanchor": "center",
                "yref": "y",
                "text": "My child<br>retires",
                "y": annotation_height(child_year+67), #3.5,
                "x": '{}-01-01'.format(child_year+67),
                "ay": -60,
                "ax": 0,
                "showarrow": True,
                'arrowhead': 2,
            }
            ]

    if child_year < self_year:
        annotation = annotation[:-4]
    figure={
        'data': data,
        'layout': {
            'legend': {
                'orientation': 'h',
                "x": 0.5,
                'xanchor': 'center'
            },
            'margin': {
                'l': 80,
                'r': 50,
                't': 40
            },
            'annotations': annotation,
            'hovermode': 'closest',
            'yaxis': {
                'ticksuffix': '°C',
                'title': 'Observed & Projected Temperature Anomaly',
                'showgrid': False,
            },
            'xaxis': {
                'showgrid': False,
                # 'title': 'Year'
            },
            # "font": {
            #     "family": "Roboto",
            #     "size": 14
            # }
        }
    }

    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
