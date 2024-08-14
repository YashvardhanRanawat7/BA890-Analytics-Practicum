import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
import os

# Snowflake connection (replace with your actual credentials)
conn = snowflake.connector.connect(
    account='zljhhxe-cbb45257',
    user='YASHVARDHAN7',
    password='24s5EDSgDz3JjFW',
    warehouse='MBTA',
    database='MBTA_DB',
    schema='MBTA'
)

# Function to fetch data from Snowflake
def fetch_data(query):
    cur = conn.cursor()
    cur.execute(query)
    df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
    cur.close()
    return df

# Fetch data for Green and Orange Lines
query = """
SELECT SERVICE_DATE, TRUNK_ROUTE_ID, BRANCH_ROUTE_ID, 
       AVG(TRAVEL_TIME_SECONDS) as AVG_SPEED,
       COUNT(DISTINCT TRIP_ID) as ROUND_TRIPS,
       AVG(DWELL_TIME_SECONDS) as AVG_DWELL_TIME,
       AVG(HEADWAY_TRUNK_SECONDS) as AVG_HEADWAY
FROM MBTA_DB.MBTA.MBTA_PERFORMANCE
WHERE TRUNK_ROUTE_ID IN ('Green', 'Orange')
GROUP BY SERVICE_DATE, TRUNK_ROUTE_ID, BRANCH_ROUTE_ID
ORDER BY SERVICE_DATE
"""
df = fetch_data(query)

# Convert SERVICE_DATE to datetime
df['SERVICE_DATE'] = pd.to_datetime(df['SERVICE_DATE'], format='%Y%m%d')

# Initialize the Dash app
app = dash.Dash(__name__)

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Enhanced MBTA Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
            
            body {
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #003c71;
                text-align: center;
                padding: 20px 0;
                font-weight: 700;
                font-size: 2.5em;
            }
            .summary-box {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
            }
            .summary-item {
                text-align: center;
                flex: 1;
                min-width: 150px;
                margin: 10px;
                padding: 15px;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            .summary-item:hover {
                transform: translateY(-5px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            }
            .summary-item h3 {
                margin: 0;
                font-size: 28px;
                font-weight: 700;
            }
            .summary-item p {
                margin: 5px 0 0;
                font-size: 14px;
                color: #666;
                font-weight: 300;
            }
            .graph-container {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .tabs-container {
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define the layout
app.layout = html.Div([
    html.Div([
        html.H1("MBTA Green and Orange Lines Performance Dashboard"),
        
        html.Div([
            dcc.Tabs([
                dcc.Tab(label="Green Line", value="green"),
                dcc.Tab(label="Green Line B", value="green-b"),
                dcc.Tab(label="Green Line C", value="green-c"),
                dcc.Tab(label="Green Line D", value="green-d"),
                dcc.Tab(label="Orange Line", value="orange"),
            ], id="line-tabs"),
        ], className="tabs-container"),
        
        html.Div([
            html.Div([
                html.H3(id="avg-speed"),
                html.P("Avg Speed (MPH)")
            ], className="summary-item"),
            html.Div([
                html.H3(id="avg-round-trips"),
                html.P("Avg Daily Round Trips")
            ], className="summary-item"),
            html.Div([
                html.H3(id="avg-dwell-time"),
                html.P("Avg Dwell Time (sec)")
            ], className="summary-item"),
            html.Div([
                html.H3(id="avg-headway"),
                html.P("Avg Headway (min)")
            ], className="summary-item"),
        ], className="summary-box"),
        
        html.Div([
            dcc.Tabs([
                dcc.Tab(label="Past week", value="week"),
                dcc.Tab(label="Past month", value="month"),
                dcc.Tab(label="Past year", value="year"),
                dcc.Tab(label="All time", value="all"),
            ], id="time-range-tabs"),
        ], className="tabs-container"),
        
        html.Div([
            html.Div([
                dcc.Graph(id='speed-graph')
            ], className="graph-container"),
            
            html.Div([
                dcc.Graph(id='headway-graph')
            ], className="graph-container"),
            
            html.Div([
                dcc.Graph(id='dwell-time-graph')
            ], className="graph-container"),
        ]),
    ], className="container")
])

# Callback to update graphs and summary based on selected line and time range
@app.callback(
    [Output('speed-graph', 'figure'),
     Output('headway-graph', 'figure'),
     Output('dwell-time-graph', 'figure'),
     Output('avg-speed', 'children'),
     Output('avg-round-trips', 'children'),
     Output('avg-dwell-time', 'children'),
     Output('avg-headway', 'children')],
    [Input('line-tabs', 'value'),
     Input('time-range-tabs', 'value')]
)
def update_dashboard(selected_line, time_range):
    if selected_line == 'green':
        df_filtered = df[df['TRUNK_ROUTE_ID'] == 'Green']
        line_color = '#00843D'  # Green
    elif selected_line == 'green-b':
        df_filtered = df[(df['TRUNK_ROUTE_ID'] == 'Green') & (df['BRANCH_ROUTE_ID'] == 'Green-B')]
        line_color = '#003DA5'  # Blue for Green-B
    elif selected_line == 'green-c':
        df_filtered = df[(df['TRUNK_ROUTE_ID'] == 'Green') & (df['BRANCH_ROUTE_ID'] == 'Green-C')]
        line_color = '#00AA4F'  # Lighter Green for Green-C
    elif selected_line == 'green-d':
        df_filtered = df[(df['TRUNK_ROUTE_ID'] == 'Green') & (df['BRANCH_ROUTE_ID'] == 'Green-D')]
        line_color = '#8F4E7D'  # Purple for Green-D
    else:  # Orange Line
        df_filtered = df[df['TRUNK_ROUTE_ID'] == 'Orange']
        line_color = '#ED8B00'  # Orange

    if time_range == 'week':
        df_filtered = df_filtered[df_filtered['SERVICE_DATE'] > df_filtered['SERVICE_DATE'].max() - pd.Timedelta(days=7)]
    elif time_range == 'month':
        df_filtered = df_filtered[df_filtered['SERVICE_DATE'] > df_filtered['SERVICE_DATE'].max() - pd.Timedelta(days=30)]
    elif time_range == 'year':
        df_filtered = df_filtered[df_filtered['SERVICE_DATE'] > df_filtered['SERVICE_DATE'].max() - pd.Timedelta(days=365)]
    
    # Calculate averages for summary
    avg_speed = df_filtered['AVG_SPEED'].mean()
    avg_round_trips = df_filtered['ROUND_TRIPS'].mean()
    avg_dwell_time = df_filtered['AVG_DWELL_TIME'].mean()
    avg_headway = df_filtered['AVG_HEADWAY'].mean() / 60  # Convert to minutes
    
    # Speed graph
    speed_fig = go.Figure()
    speed_fig.add_trace(go.Scatter(x=df_filtered['SERVICE_DATE'], y=df_filtered['AVG_SPEED'],
                                   mode='lines', name='MPH', line=dict(color=line_color, width=3)))
    speed_fig.update_layout(
        title='Average Speed Over Time',
        xaxis_title='Date',
        yaxis_title='MPH',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Roboto, sans-serif", size=12),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    
    # Headway graph
    headway_fig = go.Figure()
    headway_fig.add_trace(go.Scatter(x=df_filtered['SERVICE_DATE'], y=df_filtered['AVG_HEADWAY'] / 60,
                                     mode='lines', name='Minutes', line=dict(color=line_color, width=3)))
    headway_fig.update_layout(
        title='Average Headway Over Time',
        xaxis_title='Date',
        yaxis_title='Minutes',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Roboto, sans-serif", size=12),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    
    # Dwell time graph
    dwell_time_fig = go.Figure()
    dwell_time_fig.add_trace(go.Scatter(x=df_filtered['SERVICE_DATE'], y=df_filtered['AVG_DWELL_TIME'],
                                        mode='lines', name='Seconds', line=dict(color=line_color, width=3)))
    dwell_time_fig.update_layout(
        title='Average Dwell Time Over Time',
        xaxis_title='Date',
        yaxis_title='Seconds',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Roboto, sans-serif", size=12),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    
    return (speed_fig, headway_fig, dwell_time_fig, 
            f"{avg_speed:.2f}", f"{avg_round_trips:.0f}", 
            f"{avg_dwell_time:.0f}", f"{avg_headway:.1f}")

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)