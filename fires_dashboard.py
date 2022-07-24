# -*- coding: utf-8 -*-
"""
Created on Sun Jul 24 16:38:23 2022

@author: Victor
"""

import pandas as pd

import plotly.express as px

import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State

import json
from urllib.request import urlopen

df = pd.read_csv('fires.csv')

with urlopen('https://raw.githubusercontent.com/codeforgermany/click_that_hood/master/public/data/brazil-states.geojson') as response:
    Brazil = json.load(response)
    
br = df.groupby(['year','state'])[['number','Latitude','Longitude']].sum().reset_index()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
        
    [
        dbc.Row([
            dbc.Col([
                html.H1("Total Fires in Brazil", style={'textAlign': 'center','color': '#DC143C', 'font-size': 30}),
            ], width=12),
        dbc.Row([
                dbc.Col([
                    html.P("Brazil", style={'textAlign': 'center','color': '#DC143C', 'font-size': 24}),
                    html.Div([
                    dcc.Dropdown(id='box-year', options=[{'label': x, 'value':x} for x in df['year'].unique()],
                                value=2000, placeholder='Select Year',
                                 style={'width':'100%', 'text-align-last' : 'center'}),
                    dcc.Graph(id='map', figure={}),
                    html.P(' '),
                    dcc.Graph(id='bar', figure={})])
                ],
                    width=8,
                    style={"height": "100%"},
                ),
                dbc.Col([
                    html.P("States", style={'textAlign': 'center','color': '#DC143C', 'font-size': 24}),
                    html.Div([
                        dcc.Dropdown(id='dropdown_box-state', options=[{'label': x, 'value':x} for x in df['state'].unique()],
                                    value='Acre', placeholder='Select the State',
                                     style={'width':'100%', 'text-align-last' : 'center'}),
                        dcc.Graph(id='bar-fig', figure={}),
                        html.P(' '),
                        dcc.Graph(id='line-fig', figure={})],
                        )
                        ],
                    width=4,
                    style={"height": "100%"},
)
                    ],

                ),
            ],
            className="h-75",
        ),

    ],
    style={"height": "100vh", 'backgroundColor':'black'},
)

@app.callback(
        Output(component_id='bar-fig', component_property='figure'),
        Output(component_id='line-fig', component_property='figure'),
        [Input(component_id='dropdown_box-state', component_property='value')]
            )

def update_chart1(state):
    state = df[df['state'] == state]
    text = str(round(state['number'].mean(), 2))
    bar_fig = px.bar(state.groupby('month')['number'].mean(), color_discrete_sequence =['red']*3, template='plotly_dark')
    bar_fig.update_layout(title='Average Fires by Month', xaxis_title=None, yaxis_title=None, showlegend=False, height=400)
    bar_fig.add_hline(y=state['number'].mean(), line_width=2, line_dash="dash", line_color="white",
                         annotation_text="Mean = "+text)
    
    line_fig = px.line(state.groupby('year')['number'].sum(), markers=True, template='plotly_dark')
    line_fig.update_layout(title='Total Fires : 1998 - 2017', xaxis_title=None, yaxis_title=None, showlegend=False,
                          height=400)
    line_fig.update_traces(line_color='#FF0000', line_width=3)
    
    return [bar_fig, line_fig]


@app.callback(
        Output(component_id='bar', component_property='figure'),
        Output(component_id='map', component_property='figure'),
        [Input(component_id='box-year', component_property='value')]
            )

def update_chart2(year):
    year_df = br[br['year'] == year]
    map_fig = px.choropleth(
        year_df,
        geojson = Brazil,
        featureidkey='properties.name',
        locations = 'state',
        color = "number",
        color_continuous_scale = "amp",
        hover_name = 'state',
        template='plotly_dark'
    )
    map_fig.update_geos(fitbounds = 'geojson', visible = False)
    map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},coloraxis_colorbar=dict(title=None, orientation = 'h', y=0), height=400)

    year_state = df[df['year'] == year]
    bar_fig2 = px.bar(year_state.groupby('state')['number'].sum().sort_values(ascending=False)[:10], color_discrete_sequence =['red']*3,
            template='plotly_dark')
    bar_fig2.update_layout(title='States with most Reported Fires', xaxis_title=None, yaxis_title=None, showlegend=False,
                          height=400)
    
    return [map_fig, bar_fig2]


if __name__ == "__main__":
    app.run_server()