import dash
from dash import dcc, html, Input,Output,State
import seaborn as sns
import plotly.express as px
from dash.exceptions import PreventUpdate
import io
import base64
import pandas as pd

# Load the my_df dataset from Seaborn
# my_df = pd.read_csv(r"C:\Users\User\OneDrive\Documents\CS 450\project 1\njtdata18-19 - Copy.csv", low_memory=False).dropna()
# my_df.to_csv("njt.csv")
my_df = pd.read_csv("njt.csv").dropna()
model_pipeline=None

# custom color scheme based on NJT branding
custom_colors = {
            'ACRL': '#54A8DD',
            'BERG': '#005DAA',
            'M&E': '#00A94F',
            'MAIN': '#FFCF01',
            'MNEG': '#A2D5AE',
            'MOBO': '#E66B5B',
            'NEC': '#EF3E42',
            'NJCL': '#00A4E4',
            'PASC': '#8E258D',
            'RARV': '#FAA634',
            'line': '#000000',
            'Mon': '#1f77b4',
            'Tue': '#ff7f0e',
            'Wed': '#2ca02c',
            'Thu': '#d62728',
            'Fri': '#9467bd',
            'Sat': '#8c564b',
            'Sun': '#e377c2',
            '01': '#1f77b4',
            '02': '#ff7f0e',
            '03': '#2ca02c',
            '04': '#d62728',
            '05': '#9467bd',
            '06': '#8c564b',
            '07': '#e377c2',
            '08': '#7f7f7f',
            '09': '#bcbd22',
            '10': '#17becf',
            '11': '#aec7e8',
            '12': '#ffbb78'
        }

# Get the categorical columns
categorical_columns = ['line', 'month', 'day_of_week']

# Get the numeric columns
numeric_columns = ['delay_minutes', 'status']

dropdown1=html.Div(className="dropdown1_div",children=[html.P("Select x: "),dcc.Dropdown(id='x_dropdown_id',options=categorical_columns, value=None,style=dict(width=150,marginLeft=2))])
dropdown2=html.Div(className="dropdown2_div",children=[html.P("Select y: "),dcc.Dropdown(id='y_dropdown_id',options=numeric_columns, value=None,style=dict(width=150,marginLeft=2))])
radio_items=dcc.RadioItems(id='cat_radio_items_id',options=categorical_columns, value=None,inline=True)
check_list = dcc.Checklist(id="checklist",options=my_df['line'].unique(),value=[],inline=True)

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(className="parent_container", children=[
    html.Div(id="row1", children=[html.H3("NJ Transit Train Data Dashboard")]),
    html.Div(id="row2", children=[]),
    html.Div(id="row3", children=[
        html.Div(className="row3_child1", children=[
            html.Div([dropdown1, dropdown2], style={'display': 'inline-block', 'width': '100%'}), 
            html.Div(dcc.Graph(id='graph1', style={'width': '100%'}), style=dict(width="100%"))
        ]),
        html.Div(className="row3_child2", children=[
            html.Div([check_list], style={'display': 'inline-block'}),
            html.Div(dcc.Graph(id='graph2', style={'width': '100%'}), style=dict(width="100%"))
        ]),
    ]),
    html.Div(id="row4", children=[
        html.Div(className="row4_child1", children=[
            html.Div([
                dcc.RadioItems(
                    id='status-radio',
                    options=[
                        {'label': 'Cancelled', 'value': 'cancelled'},
                        {'label': 'Estimated', 'value': 'estimated'}
                    ],
                    value='cancelled',  # Default value
                    labelStyle={'display': 'block'}
                ),
            ], style={'width': '80%', 'margin': 'auto'}),
            html.Div([
                dcc.Graph(id='graph3')
            ], style={'width': '80%', 'margin': 'auto'})
        ]),
        html.Div(className="row4_child2", style={'display': 'flex', 'flexDirection': 'row'}, children=[
            html.Div([
                dcc.Dropdown(
                    id='line-dropdown',
                    options=[{'label': i, 'value': i} for i in my_df['line'].unique()],
                    value=my_df['line'].unique()[0],
                    clearable=False
                )
            ], style={'width': '25%', 'margin': 'auto', 'textAlign': 'center'}),
            dcc.Graph(id='graph4', style={'width': '90%', 'height': '400px'})
        ])
    ])
])


# GRAPH 1 - Categorical x vs Numerical y
@app.callback(Output('graph1', 'figure'), [Input('x_dropdown_id', 'value'), Input('y_dropdown_id', 'value')])
def update_graph1(x_val, y_val):
    if y_val is not None and x_val is not None:
        if y_val == 'status':
            avg_y = my_df[my_df['status'] == 'cancelled'].groupby(x_val).size().reset_index(name='count')
            figure = px.bar(avg_y, x=x_val, y='count', color='count', text='count')
            figure.update_yaxes(title_text='Number of Cancellations')
        else:
            my_df[y_val] = pd.to_numeric(my_df[y_val], errors='coerce')
            avg_y = my_df.groupby(x_val)[y_val].mean().reset_index()
            avg_y_sorted = avg_y.sort_values(by=y_val, ascending=True)
            figure = px.bar(avg_y_sorted, x=x_val, y=y_val, text=y_val, color_discrete_map=custom_colors, color=x_val)
            figure.update_yaxes(title_text=y_val + ' (average)')

        figure.update_layout(plot_bgcolor="#f7f7f7")
        figure.update_traces(marker_line_color='rgb(8,48,107)', marker_line_width=1.5, opacity=0.6)
        return figure
    else:
        raise PreventUpdate



# GRAPH 2 - Delay minutes over time grouped by train line
@app.callback(Output('graph2', 'figure'), [Input('checklist', 'value')])
def update_graph2(selected_value):
    if not selected_value:
        return {}
    
    filtered_df = my_df[my_df['line'].isin(selected_value) & (my_df['delay_minutes'] > 5)]
    fig = px.scatter(filtered_df, x='date', y='delay_minutes', color = 'line', color_discrete_map=custom_colors, labels={'delay_minutes': 'Delay Minutes >5'}, title='Delay Time by Train Line 2018-19')
    fig.update_layout(xaxis={'showticklabels': False})  # Turn off x-axis tick labels

    return fig

# GRAPH 3 - 
@app.callback(Output('graph3', 'figure'), [Input('status-radio', 'value')])
def update_graph3(selected_status):
    filtered_df = my_df[my_df['status'] == selected_status]
    df_counts = filtered_df.groupby(['month', 'status']).size().reset_index(name='count')
    
    # Set color map
    colors = {'estimated': 'yellow', 'cancelled': 'red'}
    
    fig = px.bar(df_counts, x='month', y='count', color='status', color_discrete_map=colors,
                 barmode='group', labels={'month': 'Month', 'count': 'Count'},title='Status by Month')
    
    fig.update_layout(bargap=0.2)
    return fig




# GRAPH 4 - 
@app.callback(Output('graph4', 'figure'), [Input('line-dropdown', 'value')])
def update_graph4(line):
    filtered_df = my_df[(my_df['line'] == line)]
    
    # Calculate the delay ranges
    bins = [-1, 5, 10, 15, 20, 25, 30, 35, float('inf')]
    labels = ['0-5', '6-10', '11-15', '16-20', '21-25', '26-30', '31-35', '>35']
    filtered_df['delay_range'] = pd.cut(filtered_df['delay_minutes'], bins=bins, labels=labels)
    
    # Calculate the count of delays in each range
    delay_counts = filtered_df['delay_range'].value_counts().reset_index()
    delay_counts.columns = ['delay_range', 'count']
    
    # Create the pie chart
    fig = px.pie(delay_counts, values='count', names='delay_range', title='Distribution of Delays')
    
    return fig




# method to calculate delay rate based on historical data to/from a location
def calculcate_delay_rate(line):
    # takes to location and from location and also time of day

    # filter df by to and from,, so it is only columns with the same to and from value
    # 

    count = (my_df['line'] == line).sum()
    #print(f"Number of rows where line is 'NEC': {count}")

    count_delayed = ((my_df['line'] == line) & (my_df['delay_minutes'] >= 5)).sum()
    #print(f"Number of rows where line is 'NEC' and delay_minutes >= 5: {count_delayed}")

    return count_delayed/count

# do not know what this does lol
def update_output(contents):
    global my_df
    if(contents is not None):
        content_string = contents.split(',')[1]
        decoded = base64.b64decode(content_string)
        my_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), skiprows=[0]).dropna()
        # Get the categorical columns
        categorical_columns = my_df.select_dtypes(include=['object', 'category']).columns.tolist()
        # Get the numeric columns
        numeric_columns = my_df.select_dtypes(include=['number']).columns.tolist()
        return categorical_columns, numeric_columns
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)
