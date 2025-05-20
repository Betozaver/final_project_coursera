# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

unique_launch_sites = spacex_df['Launch Site'].unique()
ls = []
ls_dict = {}
ls.append({'label': 'All Sites', 'value': 'ALL'})
for i in unique_launch_sites:
    ls_dict['label'] = i
    ls_dict['value'] = i
    ls.append(ls_dict)
    ls_dict = {}

min_value = 0
max_value = 10000
print(ls)
print(unique_launch_sites)
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[html.H1('SpaceX Launch Records Dashboard',
    style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    # dcc.Dropdown(id='site-dropdown',...)
    html.Div(dcc.Dropdown(
        id='site-dropdown',
        options=ls,
        value='ALL',
        placeholder='Select a Launch Site',
        searchable=True,
    )),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    html.Div(dcc.RangeSlider(id='payload-slider',
                  min=0, max=10000, step=1000,
                  marks={0: '0', 100: '100'},
                  value=[min_payload, max_payload])),


    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        # 2) Count how many 0’s and 1’s
        counts = (
            filtered_df['class']
            .value_counts()
            .rename_axis('class')
            .reset_index(name='count')
        )

        # (Optional) map 0/1 to more meaningful labels
        counts['class'] = counts['class'].map({0: 'Failure', 1: 'Success'})

        # 3) Build the pie chart
        fig = px.pie(
            counts,
            names='class',
            values='count',
            title=f'Outcome Distribution for {entered_site}',
            hole=0.3
        )
        return fig
    else:
        filtered = filtered_df[filtered_df['Launch Site'] == entered_site]

        # 2) Count how many 0’s and 1’s
        counts = (
            filtered['class']
            .value_counts()
            .rename_axis('class')
            .reset_index(name='count')
        )

        # (Optional) map 0/1 to more meaningful labels
        counts['class'] = counts['class'].map({0: 'Failure', 1: 'Success'})

        # 3) Build the pie chart
        fig = px.pie(
            counts,
            names='class',
            values='count',
            title=f'Outcome Distribution for {entered_site}',
            hole=0.3
        )
        return fig
        # return the outcomes piechart for a selected site
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_scatter_plot(entered_site, payload):
    low, high = payload

    # 1) Filter by payload range first
    df_filtered = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
        ]

    # 2) If a specific site is selected, filter by site
    if entered_site != 'ALL':
        df_filtered = df_filtered[df_filtered['Launch Site'] == entered_site]
        title = f"Payload vs Outcome for {entered_site}"
    else:
        title = "Payload vs Outcome for All Sites"

    # 3) Build the scatter plot
    fig = px.scatter(
        df_filtered,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version',  # color by booster version
        title=title,
        labels={
            'Payload Mass (kg)': 'Payload Mass (kg)',
            'class': 'Mission Outcome (0 = Failure, 1 = Success)',
            'Booster Version': 'Booster Version'
        },
        hover_data=['Launch Site']
    )

    # 4) Return the figure
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
