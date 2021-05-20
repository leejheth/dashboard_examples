"""
Dash port of Shiny iris k-means example:
https://shiny.rstudio.com/gallery/kmeans-example.html
"""
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from sklearn import datasets
from sklearn.cluster import KMeans

iris_raw = datasets.load_iris()
iris = pd.DataFrame(iris_raw["data"], columns=iris_raw["feature_names"])

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("X variable"),
                dcc.Dropdown(
                    id="x-variable",
                    options=[
                        {"label": col, "value": col} for col in iris.columns 
                        # the value next to the "value" has to match the value & data type of your actual data!
                    ],
                    value="sepal length (cm)", # initial (default) value
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Y variable"),
                dcc.Dropdown(
                    id="y-variable",
                    options=[
                        {"label": col, "value": col} for col in iris.columns
                    ],
                    value="sepal width (cm)",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Cluster count"),
                dbc.Input(id="cluster-count", type="number", value=3),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Extra"),
                dbc.Input(id="extra-count", type="number", value=4),
            ]
        ),
    ],
    body=True,
)

controls2 = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("dummy variable"),
                dcc.Dropdown(
                    id="dummy-variable",
                    options=[
                        {"label": number+10, "value": number+10} for number in range(5)
                    ],
                    value=13, # initial (default) value
                ),
            ]
        ),
    ],
    body=True,
)


app.layout = dbc.Container(
    [
        html.H1("Iris k-means clustering", style={'text-align': 'center'}),
        html.Hr(), # insert a horizontal line
        dbc.Alert("Welcome to Jihyun's dashboard!", color="primary"),
        html.Br(), # insert a line break
        dbc.Alert(
        	"Trying out different functions now!", 
        	color="secondary",
        	id="alert-fade",
            dismissable=True,
            is_open=True,
        ),
        html.Hr(),
        dbc.Button(
            "Toggle alert button with fade", 
            id="alert-toggle-fade", 
            className="mr-1"
        ),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(dcc.Graph(id="cluster-graph"), md=8),
            ],
            align="center",
        ),
        html.H1("Second header line", style={'text-align': 'center'}),
        html.Div(id='output_container', children=[]),
        dcc.Graph(id='my_bee_map', figure={}),
        dbc.Row(
            [
                dbc.Col(controls2, md=2),
                dbc.Col(dcc.Graph(id="dummy"), md=5),
                dbc.Col(dcc.Graph(id="dummy2"), md=5),
            ],
            align="center", # why this doesn't work???
        ),
    ],
    fluid=True,
)


@app.callback(
    Output(component_id='alert-fade', component_property='is_open'),
    [Input(component_id='alert-toggle-fade', component_property='n_clicks')],
    [State(component_id='alert-fade', component_property='is_open')],
)
def toggle_alert(n, is_open): # for every callback you need a function for that
    if n:
        return not is_open
    return is_open

    
@app.callback(
    Output(component_id='cluster-graph', component_property='figure'),
    [
        Input(component_id='x-variable', component_property='value'),
        Input(component_id='y-variable', component_property='value'),
        Input(component_id='cluster-count', component_property='value'),
        Input(component_id='extra-count', component_property='value')
    ],
)
def make_graph(x, y, n_clusters, extra):  # as many arguments as you have as inputs
    # minimal input validation, make sure there's at least one cluster
    km = KMeans(n_clusters=max(n_clusters, 1))
    df = iris.loc[:, [x, y]]
    km.fit(df.values)
    df["cluster"] = km.labels_

    centers = km.cluster_centers_

    data = [
        go.Scatter(
            x=df.loc[df.cluster == c, x],
            y=df.loc[df.cluster == c, y],
            mode="markers",
            marker={"size": 8},
            name="Cluster {}".format(c),
        )
        for c in range(n_clusters)
    ]

    data.append(
        go.Scatter(
            x=centers[:, 0],
            y=centers[:, 1],
            mode="markers",
            marker={"color": "#000", "size": 12, "symbol": "diamond"},
            name="Cluster centers",
        )
    )

    data.append(
        go.Scatter(
            x=len(centers[:, 0])*[extra],
            y=centers[:, 1],
            mode="markers",
            marker={"color": "#010", "size": 8},
            name="Extra",
        )
    )

    layout = {"xaxis": {"title": x}, "yaxis": {"title": y}}

    return go.Figure(data=data, layout=layout)


# make sure that x and y values can't be the same variable
def filter_options(v):
    """Disable option v"""
    return [
        {"label": col, "value": col, "disabled": col == v}
        for col in iris.columns
    ]


# functionality is the same for both dropdowns, so we reuse filter_options
app.callback(Output("x-variable", "options"), [Input("y-variable", "value")])(
    filter_options
)
app.callback(Output("y-variable", "options"), [Input("x-variable", "value")])(
    filter_options
)


if __name__ == "__main__":
    app.run_server(debug=True, port=8888)