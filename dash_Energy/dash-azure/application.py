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


df_long = pd.read_csv('top20_NetEnergy_DashboardData.csv')

app = dash.Dash()
application = app.server

df_long['Year'] = df_long['Year'].astype('int')
df_long = df_long.sort_values('Year')
available_indicators = df_long[df_long['Indicator_Name'] != 'Natural Resources Depletion (% of GNI)']['Indicator_Name'].unique()
available_countries = df_long['Country_Name'].unique()

income_fig = px.choropleth(df_long[df_long['Year'] == 2014].sort_values('Income_Group'), locations="Country_Code",
                    color="Income_Group", width=600,
                    hover_name="Country_Name", # column to add to hover information
                    category_orders={
        "Income_Group": [
            'High income',
            'Upper middle income',
           'Lower middle income'
        ]
    },
                    color_discrete_map= {
                        'High income': 'rgb(13, 48, 100)',
                        'Upper middle income': 'rgb(126, 77, 143)',
                        'Lower middle income': 'rgb(193, 100, 121)'
                    },
                   labels={'Income_Group': 'Income Group'},
                   title ='Income Group of Countries')

income_fig.update_layout(
    title_font_size=22,
    margin=dict(l=40, r=2, t=40, b=5),
)


app.layout = html.Div([
    html.H1("Energy Use Dashboard"),
    html.H2("Top 20 Countries with the Highest Average Energy Use"),
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Net Energy Use'
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
    ], style={'width': '50%', 'height':'60%', 'display': 'inline-block', 'padding': '20 20'}),
    
     html.Div([
        dcc.Graph(figure=income_fig
        )
    ], style={'width': '50%', 'display': 'inline-block', 'padding': '5 0 5 5'}),
    

    html.Div(dcc.Slider(
        id='crossfilter-year--slider',
        min=df_long['Year'].min(),
        max=df_long['Year'].max(),
        value=df_long['Year'].max(),
        step=None,
        marks={str(year): str(year) for year in df_long['Year'].unique()}
    ), style={'width': '50%', 'padding': '0px 20px 20px 20px'}),
    
     html.Div([
        dcc.Graph(id='x-time-series')
    ], style={'display': 'inline-block', 'width': '50%'}),
    
     html.Div([
        dcc.Graph(id='natDepl-time-series')
    ], style={'display': 'inline-block', 'width': '50%'}),
    
     html.Div([
        html.H4('Data Source: ', style={'display': 'inline-block', 'marginRight': 10}),
        dcc.Link(html.A("The World Bank Data Catalog"), href='https://datacatalog.worldbank.org/search/dataset/0037651/Environment--Social-and-Governance-Data', target="_blank"),
    ], style={'width': '50%', 'padding': '0px 20px 20px 20px'})
    
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
                color='rgba(0,0,128, 1)' if (xaxis_column_name == 'Net Energy Use' or xaxis_column_name == 'Energy Use Per Capita') else 'rgba(0,128,0,1)' if 'Renewables' in xaxis_column_name else 'rgba(255,0,0,1)'
            )
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
            },
            yaxis={
                'title': '',
            },
            margin={'l': 150, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
    }

def create_time_series(dff, title, xaxis_column_name):
    return {
        'data': [go.Scatter(
#            x=dff['Year'].sort_values(ascending=False),
            x=dff['Year'],
            y=dff['Value'],
            mode='lines+markers',
             marker=dict(
                color='rgba(0,0,128, 1)' if (xaxis_column_name == 'Net Energy Use' or xaxis_column_name == 'Energy Use Per Capita') else 'rgba(0,128,0,1)' if 'Renewables' in xaxis_column_name else 'rgba(255,0,0,1)'
            )
        )],
        'layout': {
            'height': 400,
            'margin': {'l': 100, 'b': 30, 'r': 10, 't': 40},
            'annotations': [{
                'x': 0, 'y': 1, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title,
                'font': dict(
                        color="black",
                        size=16
                        )
            }],
            'yaxis': {'type': 'linear', 'title': 'Energy Use (kg of oil equivalent)'},
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

@app.callback(
    dash.dependencies.Output('natDepl-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-bar', 'hoverData'),
     dash.dependencies.Input('crossfilter-xaxis-column', 'value')])
def update_natDepl_timeseries(hoverData, xaxis_column_name):
    country_name = hoverData['points'][0]['customdata']
    dff2 = df_long[df_long['Country_Name'] == country_name]
    dff2 = dff2[dff2['Indicator_Name'] == 'Natural Resources Depletion (% of GNI)']
    title = '<b>{}</b><br>{}'.format(country_name, 'Natural Resources Depletion (% of GNI)')
    return {
        'data': [go.Scatter(
            x=dff2['Year'],
            y=dff2['Value'],
            mode='lines+markers',
             marker=dict(
                color='rgba(0,0,128, 1)' if (xaxis_column_name == 'Net Energy Use' or xaxis_column_name == 'Energy Use Per Capita') else 'rgba(0,128,0,1)' if 'Renewables' in xaxis_column_name else 'rgba(255,0,0,1)'
            )
        )],
        'layout': {
            'height': 400,
            'margin': {'l': 100, 'b': 30, 'r': 10, 't': 40},
            'annotations': [{
                'x': 0, 'y': 1, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title,
                'font': dict(
                        color="black",
                        size=16
                        )
            }],
            'yaxis': {'type': 'linear', 'title': 'Natural Resources Depletion (% of GNI)', 'range':[0, max(dff2['Value'])+1]},
            'xaxis': {'showgrid': False, 'title': 'Year'}
        }
    }

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port='80')
