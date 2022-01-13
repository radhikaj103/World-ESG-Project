import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import datetime as dt
import plotly.express as px
import plotly
import plotly.graph_objs as go


df_long = pd.read_csv('dataEnergyDashboard.csv')

app = dash.Dash()
application = app.server

df_long['Year'] = df_long['Year'].astype('int')

available_indicators = df_long['Indicator_Name'].unique()
available_countries = df_long['Country_Name'].unique()

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Total Energy Use'
            )            
        ],
        style={'width': '50%', 'display': 'block'}),
        

    ], 
        style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),
    
    
    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-bar',
            hoverData={'points': [{'customdata': 'Canada'}]}
        )
    ], style={'width': '75%', 'display': 'block', 'padding': '20 20'}),

    html.Div(dcc.Slider(
        id='crossfilter-year--slider',
        min=df_long['Year'].min(),
        max=df_long['Year'].max(),
        value=df_long['Year'].max(),
        step=None,
        marks={str(year): str(year) for year in df_long['Year'].unique()}
    ), style={'width': '75%', 'padding': '0px 20px 20px 20px'}),
    
     html.Div([
        dcc.Graph(id='x-time-series')
    ], style={'display': 'block', 'width': '75%'})
])


@app.callback(
    dash.dependencies.Output('crossfilter-indicator-bar', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-year--slider', 'value')])

def update_graph(xaxis_column_name, 
                 year_value):
    dff = df_long[df_long['Year'] == year_value]

    return {
        'data': [go.Bar(
            x=dff[dff['Indicator_Name'] == xaxis_column_name]['Value'],
            y=dff[dff['Indicator_Name'] == xaxis_column_name]['Country_Name'],
            text=dff[dff['Indicator_Name'] == xaxis_column_name]['Country_Name'],
            customdata=dff[dff['Indicator_Name'] == xaxis_column_name]['Country_Name'],
            orientation='h',
#            mode='markers',
            marker=dict(
                color='rgba(0,0,128, 1)' if xaxis_column_name == 'Total Energy Use' else 'rgba(0,128,0,1)' if xaxis_column_name == 'Energy Use from Renewables' else 'rgba(255,0,0,1)'
            )
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
            },
            yaxis={
                'title': 'Country',
            },
            margin={'l': 150, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
    }

def create_time_series(dff, title, xaxis_column_name):
    return {
        'data': [go.Scatter(
            x=dff['Year'],
            y=dff['Value'],
            mode='lines+markers',
             marker=dict(
                color='rgba(0,0,128, 1)' if xaxis_column_name == 'Total Energy Use' else 'rgba(0,128,0,1)' if xaxis_column_name == 'Energy Use from Renewables' else 'rgba(255,0,0,1)'
            )
        )],
        'layout': {
            'height': 400,
            'margin': {'l': 100, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear', 'title': 'Energy Use (kg of oil equivalent per capita)'},
            'xaxis': {'showgrid': False, 'title': 'Year'}
        }
    }

@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-bar', 'hoverData'),
     dash.dependencies.Input('crossfilter-xaxis-column', 'value')])
def update_x_timeseries(hoverData, xaxis_column_name):
    country_name = hoverData['points'][0]['customdata']
    dff = df_long[df_long['Country_Name'] == country_name]
    dff = dff[dff['Indicator_Name'] == xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, title, xaxis_column_name)

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port='80')
