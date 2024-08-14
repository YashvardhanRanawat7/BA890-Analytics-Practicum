import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import snowflake.connector
from dash_extensions import BeforeAfter
import plotly.graph_objs as go
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import snowflake.connector
import plotly.graph_objs as go
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import snowflake.connector
import plotly.graph_objs as go
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
import traceback


# Snowflake connection (replace with your actual credentials)
'''
conn = snowflake.connector.connect(
    account='zljhhxe-cbb45257',
    user='YASHVARDHAN7',
    password='24s5EDSgDz3JjFW',
    warehouse='MBTA',
    database='MBTA_DB',
    schema='MBTA'
)
'''


# Snowflake connection function with error handling
def get_snowflake_data(query):
    try:
        conn = snowflake.connector.connect(
            account='zljhhxe-cbb45257',
            user='YASHVARDHAN7',
            password='24s5EDSgDz3JjFW',  # Replace with actual password
            warehouse='MBTA',
            database='MBTA_DB',
            schema='MBTA'
        )
        cur = conn.cursor()
        cur.execute(query)
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(data, columns=columns)
        cur.close()
        conn.close()
        print(f"Query executed successfully. Returned {len(df)} rows.")
        print("DataFrame columns:", df.columns.tolist())
        print(df.head())  # Print first few rows for debugging
        return df
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        print(f"Query: {query}")
        print(traceback.format_exc())
        return pd.DataFrame()  # Return empty DataFrame on error

# Fetch subway lines from Snowflake
lines_query = """
SELECT line_id, line_long_name, line_short_name
FROM lines
WHERE line_id IN (
    SELECT DISTINCT line_id
    FROM routes
    WHERE route_desc = 'Rapid Transit'  -- Subway lines
)
"""
lines_df = get_snowflake_data(lines_query)

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("MBTA Subway Trip Dashboard", className="text-center mb-4"), width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Label("Select a Line:"),
            dcc.Dropdown(
                id='line-dropdown',
                options=[{'label': name if name else id, 'value': id} 
                         for id, name in zip(lines_df['LINE_ID'], lines_df['LINE_LONG_NAME'])],
                placeholder="Select a line"
            )
        ], width=6),
        dbc.Col([
            dbc.Label("Select Time Period:"),
            dcc.Dropdown(
                id='time-period-dropdown',
                options=[
                    {'label': 'Past Week', 'value': '1W'},
                    {'label': 'Past Month', 'value': '1M'},
                    {'label': 'Past Year', 'value': '1Y'}
                ],
                value='1W',
                placeholder="Select time period"
            )
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='stops-map'), width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Label("Start Stop:"),
            dcc.Dropdown(id='start-stop-dropdown', placeholder="Select start stop")
        ], width=6),
        dbc.Col([
            dbc.Label("End Stop:"),
            dcc.Dropdown(id='end-stop-dropdown', placeholder="Select end stop")
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Average Travel Time", className="card-title"),
                    html.H2(id='avg-travel-time', className="card-text")
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Average Speed", className="card-title"),
                    html.H2(id='avg-speed', className="card-text")
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Average Dwell Time", className="card-title"),
                    html.H2(id='avg-dwell-time', className="card-text")
                ])
            ])
        ], width=4)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='performance-graph'), width=12)
    ]),

    # Debug information
    html.Div(id='debug-info', style={'whiteSpace': 'pre-wrap'})
], fluid=True)

# Callbacks
@app.callback(
    [Output('stops-map', 'figure'),
     Output('debug-info', 'children')],
    Input('line-dropdown', 'value')
)
def update_map(selected_line):
    debug_info = f"Selected line: {selected_line}\n"
    if not selected_line:
        return go.Figure(), debug_info + "No line selected."
    
    line_stops_query = f"""
    SELECT DISTINCT s.STOP_ID, s.STOP_NAME, s.STOP_LAT, s.STOP_LON
    FROM STOPS s
    JOIN STOP_TIMES st ON s.STOP_ID = st.STOP_ID
    JOIN TRIPS t ON st.TRIP_ID = t.TRIP_ID
    JOIN ROUTES r ON t.ROUTE_ID = r.ROUTE_ID
    WHERE r.LINE_ID = '{selected_line}'
    """
    debug_info += f"Executing query:\n{line_stops_query}\n\n"
    
    line_stops_df = get_snowflake_data(line_stops_query)
    
    debug_info += f"Stops query returned {len(line_stops_df)} rows.\n"
    debug_info += f"Columns in result: {line_stops_df.columns.tolist()}\n"
    debug_info += f"Sample data:\n{line_stops_df.head().to_string()}\n"

    if line_stops_df.empty:
        debug_info += "No stops data available for the selected line.\n"
        debug_info += "Checking individual table contents:\n"
        
        # Check STOPS table
        stops_check = get_snowflake_data("SELECT COUNT(*) as count FROM STOPS")
        debug_info += f"STOPS table count: {stops_check['COUNT'].iloc[0]}\n"
        
        # Check STOP_TIMES table
        stop_times_check = get_snowflake_data("SELECT COUNT(*) as count FROM STOP_TIMES")
        debug_info += f"STOP_TIMES table count: {stop_times_check['COUNT'].iloc[0]}\n"
        
        # Check TRIPS table
        trips_check = get_snowflake_data("SELECT COUNT(*) as count FROM TRIPS")
        debug_info += f"TRIPS table count: {trips_check['COUNT'].iloc[0]}\n"
        
        # Check ROUTES table
        routes_check = get_snowflake_data(f"SELECT COUNT(*) as count FROM ROUTES WHERE LINE_ID = '{selected_line}'")
        debug_info += f"ROUTES table count for selected LINE_ID: {routes_check['COUNT'].iloc[0]}\n"
        
        return go.Figure(), debug_info

    fig = px.scatter_mapbox(line_stops_df,
                            lat='STOP_LAT',
                            lon='STOP_LON',
                            hover_name='STOP_NAME',
                            zoom=10)
    fig.update_layout(mapbox_style="carto-positron", height=600)
    return fig, debug_info

@app.callback(
    [Output('start-stop-dropdown', 'options'),
     Output('end-stop-dropdown', 'options')],
    Input('line-dropdown', 'value')
)
def update_stop_options(selected_line):
    if not selected_line:
        return [], []
    
    line_stops_query = f"""
    SELECT DISTINCT s.STOP_ID, s.STOP_NAME
    FROM STOPS s
    JOIN STOP_TIMES st ON s.STOP_ID = st.STOP_ID
    JOIN TRIPS t ON st.TRIP_ID = t.TRIP_ID
    JOIN ROUTES r ON t.ROUTE_ID = r.ROUTE_ID
    WHERE r.LINE_ID = '{selected_line}'
    ORDER BY s.STOP_NAME
    """
    line_stops_df = get_snowflake_data(line_stops_query)
    
    options = [{'label': name, 'value': id} for id, name in zip(line_stops_df['STOP_ID'], line_stops_df['STOP_NAME'])]
    return options, options

@app.callback(
    [Output('avg-travel-time', 'children'),
     Output('avg-speed', 'children'),
     Output('avg-dwell-time', 'children'),
     Output('performance-graph', 'figure')],
    [Input('line-dropdown', 'value'),
     Input('start-stop-dropdown', 'value'),
     Input('end-stop-dropdown', 'value'),
     Input('time-period-dropdown', 'value')]
)
def update_metrics(selected_line, start_stop, end_stop, time_period):
    if not all([selected_line, start_stop, end_stop, time_period]):
        return "N/A", "N/A", "N/A", go.Figure()
    
    # Calculate date range
    end_date = datetime.now().date()
    if time_period == '1W':
        start_date = end_date - timedelta(days=7)
    elif time_period == '1M':
        start_date = end_date - timedelta(days=30)
    else:  # '1Y'
        start_date = end_date - timedelta(days=365)
    
    performance_query = f"""
    SELECT SERVICE_DATE, AVG(TRAVEL_TIME_SECONDS) as avg_travel_time,
           AVG(TRAVEL_TIME_SECONDS / 60) as avg_travel_time_minutes,
           AVG(DWELL_TIME_SECONDS) as avg_dwell_time_seconds
    FROM MBTA_PERFORMANCE mp
    JOIN ROUTES r ON mp.ROUTE_ID = r.ROUTE_ID
    WHERE r.LINE_ID = '{selected_line}'
      AND mp.STOP_ID IN (
        SELECT STOP_ID
        FROM STOP_TIMES st
        JOIN TRIPS t ON st.TRIP_ID = t.TRIP_ID
        JOIN ROUTES r ON t.ROUTE_ID = r.ROUTE_ID
        WHERE r.LINE_ID = '{selected_line}'
        AND STOP_SEQUENCE BETWEEN (
          SELECT MIN(STOP_SEQUENCE)
          FROM STOP_TIMES
          WHERE STOP_ID = '{start_stop}'
        ) AND (
          SELECT MAX(STOP_SEQUENCE)
          FROM STOP_TIMES
          WHERE STOP_ID = '{end_stop}'
        )
      )
      AND SERVICE_DATE BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY SERVICE_DATE
    ORDER BY SERVICE_DATE
    """
    performance_df = get_snowflake_data(performance_query)
    
    if performance_df.empty:
        return "No data", "No data", "No data", go.Figure()

    avg_travel_time = performance_df['AVG_TRAVEL_TIME_MINUTES'].mean()
    avg_dwell_time = performance_df['AVG_DWELL_TIME_SECONDS'].mean() / 60  # Convert to minutes
    
    # Calculate distance between stops (simplified calculation)
    distance_query = f"""
    SELECT 
        2 * 3961 * asin(
            sqrt(
                power(sin((end_stop.STOP_LAT - start_stop.STOP_LAT) * pi() / 360), 2) +
                cos(start_stop.STOP_LAT * pi() / 180) *
                cos(end_stop.STOP_LAT * pi() / 180) *
                power(sin((end_stop.STOP_LON - start_stop.STOP_LON) * pi() / 360), 2)
            )
        ) as distance_miles
    FROM 
        STOPS start_stop,
        STOPS end_stop
    WHERE 
        start_stop.STOP_ID = '{start_stop}'
        AND end_stop.STOP_ID = '{end_stop}'
    """
    distance_df = get_snowflake_data(distance_query)
    
    if distance_df.empty:
        avg_speed = 0
    else:
        distance = distance_df['DISTANCE_MILES'].iloc[0]
        avg_speed = distance / (avg_travel_time / 60)  # mph
    
    fig = px.line(performance_df, x='SERVICE_DATE', y='AVG_TRAVEL_TIME_MINUTES',
                  title=f"Average Travel Time: {start_stop} to {end_stop}")
    fig.update_layout(yaxis_title="Travel Time (minutes)")
    
    return (f"{avg_travel_time:.2f} minutes", 
            f"{avg_speed:.2f} mph", 
            f"{avg_dwell_time:.2f} minutes", 
            fig)

if __name__ == '__main__':
    app.run_server(debug=True)