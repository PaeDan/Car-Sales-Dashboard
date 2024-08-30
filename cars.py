import dash 
from dash import dcc, Input, Output, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px 

data = pd.read_csv('car_prices.csv')
data['state'] = data['state'].str.upper()  #Make all the states Capital where ca = CA
data = data[data['state'].str.len() <= 2] #Drops all states where its not in the abbreviated format 
data['make'] = data['make'].str.upper() #Makes all the manufacturers capital so that those who put kia = KIA
data = data.dropna(subset = 'make') #Drop any nans/nas

data['saledate'] = pd.to_datetime(data['saledate'], format= 'mixed', yearfirst= True, utc = True) #We want to make a new column for years and months
data['yearmonth'] = data['saledate'].dt.to_period('M') #This will drop the timezone and only get the year-month 

num_sales = len(data)

app = dash.Dash(__name__, external_stylesheets= [dbc.themes.BOOTSTRAP, 'style.css'])
app.layout = dbc.Container([

#The title
dbc.Row([
    dbc.Col(html.H1('Car Sales Dashboard'), className = 'text-center my-3', width= 12)
]),

#Display the number of car sales
dbc.Row([
    dbc.Col(html.Div(f'Total Car Sold : {num_sales}', className = 'text-center my-3 top-text'), width= 12)
], className= 'mb-5'),

#Bar plot for car models sold for each maker and a trend admission for each maker
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H4('Car Models Sold for Each Maker', className= 'Card Title'),
                dcc.Dropdown(
                    id = 'make-filter',
                    options = [{'label' : make, 'value' : make} for make in data['make'].unique()],
                    value = None,
                    placeholder= 'Choose a Manufacturer'
                ),
                dcc.Graph(id = 'model-distribution')
            ])
        ])
    ], width= 6),
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H4('Sales Trend for Manufacterurs', className= 'Card Title'),
                dcc.Graph(
                    id = 'trend-distribution'
                )
            ])
        ])
    ], width= 6)
]),

#Pie-chart to see which maker is sold by state 
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H4('Manufacterur by State', className= 'Card Title'),
                dcc.Dropdown(
                    id = 'state-filter',
                    options = [{'label' : state, 'value' : state} for state in data['state'].unique()],
                    value = None,
                    placeholder= 'Choose the State'
                ),
                dcc.Graph(
                    id = 'make-distribution'
                )
            ])
        ])
    ], width = 12)
]),

dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H4('Selling Price Distribution', className= 'Card Title'),
                dcc.Slider(
                    id = 'selling-slider',
                    min = data['sellingprice'].min(),
                    max = data['sellingprice'].max(),
                    value = data['sellingprice'].median(),
                    marks = {int(value) : f'${int(value):,}' for value in data['sellingprice'].quantile([0, 0.25, 0.5, 0.75, 1]).values},
                    step = 100
                ),
                dcc.Graph(
                    id = 'selling-distribution'
                )
            ])
        ])
    ], width= 12)
])

], fluid= True)

#Creating the callbacks
#The Bar chart for best car models for each manufacterur
@app.callback(
    Output('model-distribution', 'figure'),
    Input('make-filter', 'value')
)
def update_model(selected_maker):
    filter_data = data[data['make'] == selected_maker] if selected_maker else data
    filter_data = filter_data.groupby('model').size().reset_index(name = 'Sales')
    filter_data = filter_data.sort_values(by = 'Sales', ascending= False)
    filter_data = filter_data.head(10)
    fig = px.bar(filter_data, 
                 x= 'model',
                 y = 'Sales',
                 color = 'model',
                 barmode = 'group',
                 title = 'Top 10 Best Selling Models',
                 color_discrete_sequence= px.colors.qualitative.Set2)
    return fig

#The Pie-chart for which manfuacterurs are sold the most for each state
@app.callback(
    Output('make-distribution', 'figure'),
    Input('state-filter', 'value')
)
def update_make(selected_state):
    filter_data = data[data['state'] == selected_state] if selected_state else data 
    fig = px.pie(
        filter_data,
        names = 'make')
    return fig 

#The Trend Sales for each Model 
@app.callback(
    Output('trend-distribution', 'figure'),
    Input('make-filter', 'value')
)
def update_trend(selected_maker):
    filter_data = data[data['make'] == selected_maker] if selected_maker else data
    filter_data['yearmonth'] = filter_data['yearmonth'].astype(str)
    trend_data = filter_data.groupby('yearmonth').size().reset_index(name = 'Sales')
    fig = px.line(trend_data,
                  x= 'yearmonth',
                  y = 'Sales',
                  title= 'Sales Over Time')
    return fig

#The slider to see the Selling Price
@app.callback(
    Output('selling-distribution', 'figure'),
    Input('selling-slider', 'value')
)
def update_sellingprice(slider_value):
    filter_data = data[data['sellingprice'] <= slider_value] if slider_value else data
    fig = px.histogram(
        filter_data,
        x = 'sellingprice',
        nbins = 10
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug = True)
