# Corrected SpaceX Dash app (inclusive payload filter, readable pie labels, improved marks)
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the cleaned CSV (fallback to original if cleaned not present)
import os
csv_path = "spacex_launch_dash_clean.csv" if os.path.exists("spacex_launch_dash_clean.csv") else "spacex_launch_dash.csv"
spacex_df = pd.read_csv(csv_path)

# Ensure consistent column names (strip whitespace)
spacex_df.columns = [c.strip() for c in spacex_df.columns]

# Create readable outcome label
if 'class' in spacex_df.columns:
    spacex_df['OutcomeLabel'] = spacex_df['class'].map({0: 'Failure', 1: 'Success'})
else:
    spacex_df['OutcomeLabel'] = spacex_df.get('Mission Outcome', spacex_df.iloc[:,0]).astype(str)

# payload min/max
if 'Payload Mass (kg)' in spacex_df.columns:
    max_payload = int(spacex_df['Payload Mass (kg)'].max())
    min_payload = int(spacex_df['Payload Mass (kg)'].min())
else:
    min_payload, max_payload = 0, 10000

# Create Dash app
app = dash.Dash(__name__)
server = app.server

# Launch sites options
uniquelaunchsites = spacex_df['Launch Site'].unique().tolist() if 'Launch Site' in spacex_df.columns else []
launchsites = [{'label': 'All Sites', 'value': 'All Sites'}] + [{'label': s, 'value': s} for s in uniquelaunchsites]

# Slider marks for clarity
def make_marks(min_v, max_v):
    step = max(1000, (max_v - min_v)//5)
    marks = {min_v: str(min_v)}
    for val in range(min_v+step, max_v, step):
        marks[val] = f"{val}"
    marks[max_v] = str(max_v)
    return marks

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36','font-size': 40}),
    dcc.Dropdown(id='site_dropdown', options=launchsites, value='All Sites', placeholder="Select a Launch Site here", searchable=True),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload_slider', min=min_payload, max=max_payload, step=100, marks=make_marks(min_payload, max_payload), value=[min_payload, max_payload]),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

@app.callback(Output('success-pie-chart', 'figure'), Input('site_dropdown', 'value'))
def get_pie_chart(site_dropdown):
    df = spacex_df.copy()
    if site_dropdown == 'All Sites':
        # show total successful launches by site
        if 'class' in df.columns:
            successes = df[df['class']==1].groupby('Launch Site').size().reset_index(name='count')
            fig = px.pie(successes, names='Launch Site', values='count', title='Total Successful Launches by Site')
        else:
            fig = px.pie(df, names='Launch Site', title='Total Launches by Site')
    else:
        # show success vs failure for the selected site (readable labels)
        site_df = df[df['Launch Site'] == site_dropdown]
        if 'OutcomeLabel' in site_df.columns:
            counts = site_df['OutcomeLabel'].value_counts().reset_index()
            counts.columns = ['Outcome','count']
            fig = px.pie(counts, names='Outcome', values='count', title=f'Total Launch Outcomes for site {site_dropdown}')
        else:
            fig = px.pie(site_df, names='class', title=f'Total Launches for site {site_dropdown}')
    return fig

@app.callback(Output('success-payload-scatter-chart', 'figure'),
              Input('site_dropdown', 'value'),
              Input('payload_slider', 'value'))
def update_scattergraph(site_dropdown, payload_slider):
    low, high = payload_slider
    df = spacex_df.copy()
    # inclusive filtering to include endpoints
    if 'Payload Mass (kg)' in df.columns:
        mask = (df['Payload Mass (kg)'] >= low) & (df['Payload Mass (kg)'] <= high)
    else:
        mask = pd.Series([True]*len(df))
    if site_dropdown != 'All Sites':
        df = df[df['Launch Site'] == site_dropdown]
    df = df[mask]
    color_col = 'Booster Version Category' if 'Booster Version Category' in df.columns else ('Booster Version' if 'Booster Version' in df.columns else None)
    fig = px.scatter(df, x="Payload Mass (kg)" if 'Payload Mass (kg)' in df.columns else None, y="class" if 'class' in df.columns else None, color=color_col, size='Payload Mass (kg)' if 'Payload Mass (kg)' in df.columns else None, hover_data=['Flight Number'] if 'Flight Number' in df.columns else None)
    fig.update_layout(title='Payload vs Launch Outcome (0 = Failure, 1 = Success)', yaxis_title='class', xaxis_title='Payload Mass (kg)')
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)