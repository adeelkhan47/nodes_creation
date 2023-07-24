"""Decision Tree Frontend for Athlethe Date"""

"""
Does not work yet:
Select a node in the network by clicking on it in the dropdown menu.
The text is saved for the node which is selected in the dropdown menu. 
and not for the node from which I just display the description. 

"""
import datetime
import json  # load json data from website

import dash_cytoscape as cyto  # show graph
import pandas as pd
from dash import Dash, dash_table, dcc, html, callback, Output, Input, State, \
    callback_context

from db_service import DatabaseService

database = DatabaseService(dbname="nodes_backend", user="postgres", password="postgres")
# required for the hierarchical network
cyto.load_extra_layouts()
# to change the node number
counter = 0

# # Website-url
# url = "https://inprove-sport.info/csv/getInproveDemo/hgnxjgTyrkCvdR"
# # Get website data
# response = requests.get(url)
# # Check if request is successful: status code 200
# if response.status_code == 200:
#     # Select json data
#     data_raw = response.json()
# else:
#     print("Error loading the website")

data_raw = database.get_url_data()
# Load data into a DataFrame
data = pd.json_normalize(data_raw, record_path=['res'])
data['testID'] = data['testID'].astype(str)

table = data.pivot_table(index="athleteID", columns="testID",
                         values="testValue")
# Create an additional column with the athletheID (the index of the table row)
# To display it later in the graph# columns now contain all testIDs and the
# AthletheID.
table["athID"] = table.index
# Create list with all athletheIDs
athlethe_names = table['athID'].to_list()

# Nodes to begin with.
# Node format is used by default in dash_cytoscape network
# = [{'data': {'id': 'everybody', 'label': '[1000, 1027, ...]'}}]
old_nodes = database.get_nodes()
if len(old_nodes) == 0:
    first_node = {'data': {'id': 'everybody', 'label': str(athlethe_names)}}
    database.add_nodes(first_node)
nodes = database.get_nodes()
# At the beginning there is only root node
edges = database.get_edges()
# At the beginning there are no Recommendations
recommendations = {}

# Stylesheet for the network
network_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'background-color': 'lightgrey',
            'font-size': 12,
            # place text in the middle
            'text-valign': 'center',
            'text-halign': 'center',
            # Label is the text that will be displayed in the nodes.
            # By data(id) I select the id of the node as text.
            # At the beginning this is everybody
            'label': 'data(id)'
        }
    },
    {
        'selector': 'edge',
        'style': {
            'line-color': 'yellow',
            # in the label of the edges I store the threshold description
            'label': 'data(label)',
            'font-size': 9
        }
    }
]


def set_logs(text):
    current_datetime = datetime.datetime.now()
    time_ = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    database.add_logs(f'{time_}  {text}')


# Define style for testID buttons
def testID_buttons_style():
    return {
        'font-size': 20,
        'width': '50px',
        'height': '50px',
        'margin': '12px',
        "padding": "13px",
        'border-radius': "50%",
        'background-color': 'orange'
    }


# Initialize the app
app = Dash(__name__, title="Athletic Analysis", prevent_initial_callbacks=True,
           suppress_callback_exceptions=True)

app.layout = html.Div([

    html.H1("Athletic Data Analysis"),

    dash_table.DataTable(
        # Expects list of dicts
        # Data for the table.
        # From each row of my PivotTable (i.e. each athlete) a separate
        # dictionary is created with the testIDs as keys
        data=table.to_dict('records'),
        # The i in the columns (testID) is used both as column header and ID
        columns=[{'name': i, 'id': i} for i in table.columns],
        page_size=5,
        id='data',
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white'
        },
        style_data={
            'backgroundColor': 'grey',
            'color': 'white'
        },
    ),

    # Div contains Threshold-menu, Note-selection-menu, Node-buttons on the
    # left side and Recommendations on the right side.
    html.Div([
        # store Threshold-Menu, Note-selection-menu, node-buttons
        html.Div
            (children=[

            # User input Threshold
            html.Label("Threshold: "),
            dcc.Input(id='threshold', type='number', min=1, max=10),

            # Leerzeile
            html.Br(),
            html.Br(),

            # Node selection drop-down menu
            html.Label("Please select a node: "),
            # takes options (a list with all elements that are displayed) and
            # value (default element) as input
            dcc.Dropdown(id="nodes-dropdown"),

            # Creates buttons for each column index of the pivottable
            # Omit the column with athletheID
            # the id of each node is: "str(i)) for i in table.columns " !!
            html.Div(

                children=[
                    html.Button(style=testID_buttons_style(), children=f"{i}",
                                id=str(i)) for i in table.columns if
                    i != 'athID'], style={'align-items': 'center'}
            ),

            html.Br(),
        ],
            style={'width': '45%', 'display': 'inline-block'}),

        # write/store Recommendations
        html.Div(children=[

            html.Button('Save Recommendations', id='save-text'),

            html.Br(),

            dcc.Textarea(
                id='text',
                value='',
                style={'width': 400, 'height': 100},
            ),

            # This only exists because callback requires an output, but
            #  nothing is displayed with it (update_text() always returns "")
            html.Div(id='hidden-div', children="test")
        ],

            style={'width': '45%', 'display': 'inline-block',
                   'float': 'right'}),
    ]),

    # Display the node description that was selected
    html.Div(id='node-description-output'),

    html.Br(),

    # Network
    cyto.Cytoscape(
        id='network',
        # bsp node = {'data': {'id': 'one', 'label': 'Node 1'}
        # edge = {'data': {'source': 'one', 'target': 'two', 'label': 'text'}}
        # node has 'id' and edge has 'source' and 'target'
        # at beginning:
        # node = [{'data': {'id': 'everybody', 'label': '[1000, 1027, ...]'}}]
        # edges = []
        elements=edges + nodes,
        style={'width': '100%', 'height': '500px'},
        layout={'name': 'dagre', 'animate': True},  # evtl 'locked'=True
        stylesheet=network_stylesheet
    )])


def update_app_layout():
    global app
    app.layout = app.layout = html.Div([

        html.H1("Athletic Data Analysis"),

        dash_table.DataTable(
            # Expects list of dicts
            # Data for the table.
            # From each row of my PivotTable (i.e. each athlete) a separate
            # dictionary is created with the testIDs as keys
            data=table.to_dict('records'),
            # The i in the columns (testID) is used both as column header and ID
            columns=[{'name': i, 'id': i} for i in table.columns],
            page_size=5,
            id='data',
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
            },
            style_data={
                'backgroundColor': 'grey',
                'color': 'white'
            },
        ),

        # Div contains Threshold-menu, Note-selection-menu, Node-buttons on the
        # left side and Recommendations on the right side.
        html.Div([
            # store Threshold-Menu, Note-selection-menu, node-buttons
            html.Div
                (children=[

                # User input Threshold
                html.Label("Threshold: "),
                dcc.Input(id='threshold', type='number', min=1, max=10),

                # Leerzeile
                html.Br(),
                html.Br(),

                # Node selection drop-down menu
                html.Label("Please select a node: "),
                # takes options (a list with all elements that are displayed) and
                # value (default element) as input
                dcc.Dropdown(id="nodes-dropdown"),

                # Creates buttons for each column index of the pivottable
                # Omit the column with athletheID
                # the id of each node is: "str(i)) for i in table.columns " !!
                html.Div(

                    children=[
                        html.Button(style=testID_buttons_style(), children=f"{i}",
                                    id=str(i)) for i in table.columns if
                        i != 'athID'], style={'align-items': 'center'}
                ),

                html.Br(),
            ],
                style={'width': '45%', 'display': 'inline-block'}),

            # write/store Recommendations
            html.Div(children=[

                html.Button('Save Recommendations', id='save-text'),

                html.Br(),

                dcc.Textarea(
                    id='text',
                    value='',
                    style={'width': 400, 'height': 100},
                ),

                # This only exists because callback requires an output, but
                #  nothing is displayed with it (update_text() always returns "")
                html.Div(id='hidden-div', children="test")
            ],

                style={'width': '45%', 'display': 'inline-block',
                       'float': 'right'}),
        ]),

        # Display the node description that was selected
        html.Div(id='node-description-output'),

        html.Br(),

        # Network
        cyto.Cytoscape(
            id='network',
            # bsp node = {'data': {'id': 'one', 'label': 'Node 1'}
            # edge = {'data': {'source': 'one', 'target': 'two', 'label': 'text'}}
            # node has 'id' and edge has 'source' and 'target'
            # at beginning:
            # node = [{'data': {'id': 'everybody', 'label': '[1000, 1027, ...]'}}]
            # edges = []
            elements=database.get_nodes() + database.get_edges(),
            style={'width': '100%', 'height': '500px'},
            layout={'name': 'dagre', 'animate': True},  # evtl 'locked'=True
            stylesheet=network_stylesheet
        )])

    @callback(Output('node-description-output', 'children'),

              Input('network', 'tapNodeData'))
    def displayTapNodeData(data):
        """Shows All Athletes of the network node
        When a node in the network is pressed, displayTapNodeData is called with
        the node data and all athletes of the node are displayed in the
        node-description-output element.

        """
        if data:
            # data['label'] stores all athletes of this node
            return "Node description: " + data['label']


# Drop down list box - only nodes without a successor, pre-select the first one


@callback(Output("nodes-dropdown", "options"),
          Output("nodes-dropdown", "value"),
          Input('network', 'elements')
          # wird aufgerufen wenn sich node/edge im netzwerk ändert
          )
def get_end_nodes(*args):
    """Stores the leave nodes in Dropdown Menu
    If any of the elements (nodes + edges) in the network is changed, then
    get_end_nodes is called with the elements as input.
    The dropdown menu (in which the nodes are selected to which the
    threshold is applied) will then be adjusted so that only the lowest nodes
    (leaves) are displayed there

    """
    # Get all nodes from elemente
    # remember: node has 'id' and edge has 'source' and 'target'
    nodes = [item for item in args[0] if next(iter(item['data'])) == "id"]
    # If there is only the root node
    if len(nodes) == 1:
        return [nodes[0]['data']['id']], nodes[0]['data']['id']
    # Get all edges from elements
    edges = [item for item in args[0] if next(iter(item['data'])) == "source"]
    # Store the nodes which are available for the next threshold selection
    end_nodes = []
    # All nodes that are the starting point of an edge
    node_ids = {n['data']['source'] for n in edges}
    for n in nodes:
        # All nodes that are not the starting point of an edge -> These nodes
        # are leaves -> A threshold can be applied to them
        if n['data']['id'] not in node_ids:
            # store the id of these nodes
            end_nodes.append(n['data']['id'])
    # value is the default node that is displayed in the dropdown menu
    value = end_nodes[0]

    return end_nodes, value


# test how to execute a function when a id was selected

@callback(Output('network', 'elements'),
          [Input(str(i), "n_clicks") for i in table.columns if i != 'athID'],
          State('network', 'elements'),
          State('threshold', 'value'),
          State("nodes-dropdown", "value"))
def update_elements(*args):
    global counter
    ctx = callback_context
    cur_testID = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
    elements = args[len(table.columns) - 1]
    nodes = database.get_nodes()
    edges = database.get_edges()
    threshold = args[len(table.columns)]
    topnode = str(args[len(table.columns) + 1])

    # If it is the first run or a button was clicked
    if ctx.triggered or cur_testID == None:
        counter = counter + 1
        if cur_testID != '' and threshold != None:
            atleths = [item for item in nodes if item["data"]["id"] == topnode][0]["data"]["label"]
            df_ath = table.loc[json.loads(atleths)]
            df_ath = (df_ath[cur_testID])
            nodes1, edges1 = data_split(df_ath, cur_testID, threshold, topnode, counter)
            set_logs(f"New nodes created for {topnode} with threshold = {threshold} and counter is = {counter}")
            edges.extend(edges1)
            nodes.extend(nodes1)
            for each in edges1:
                database.add_edges(each)
            for each in nodes1:
                database.add_nodes(each)

        if threshold:
            database.add_threshold(threshold)
        update_app_layout()
        return edges + nodes


def data_split(athl, testID, threshold, topnode, cur_counter):
    """Function splits the athlethes in two nodes"""
    # Create two tables the right athlets
    athl_left = athl[athl <= threshold]
    athl_right = athl[athl > threshold]

    """
    remember:
    node = {'data': {'id': 'one', 'label': 'Node 1'}}
    edge =  {'data': {'source': 'one', 'target': 'two', 'label': 'Node 1'}}] 
    """

    # Create 2 new nodes. Id of the left one is node{cur_counter}-l and of the
    # right one node{cur_counter}-r. In the label I write the respective
    # athleths which the node contains.
    nodes = [{'data': {'id': my_id, 'label': my_label}} for my_id, my_label in
             ((f"node{cur_counter}-l", str(athl_left.index.tolist())),
              (f"node{cur_counter}-r", str(athl_right.index.tolist())))]

    # Create 2 new edges from the topnode (source) to the two new nodes.
    # As label of the edges I store the threshold which was applied.
    # To the left node this is: {testID}<={threshold}".
    # Remeber: The Treshold label ist displayed in the network Stylsheet as
    # Edge label
    edges = [{'data': {'source': source, 'target': target, 'label': label}} for
             source, target, label in
             ((topnode, f"node{cur_counter}-l", f"{testID}<={threshold}"),
              (topnode, f"node{cur_counter}-r", f"{testID}>{threshold}"))]
    return nodes, edges


# callback recommendations - save

@callback(Output('hidden-div', 'children'),
          Input('save-text', 'n_clicks'),
          State('text', 'value'),
          State("nodes-dropdown", "value"))
def update_text(*args):
    """
    Is called wenn save-text is clicked.
    Takes the current state of the text and the current node in the dropdown
    menu als input.
    Caution. The text applies to the node that is currently selected in the
    dropdown menu and not the node for which you are currently displaying the
    description. Since only the leaves are displayed in the dropdown menu,
    the recommendation can only be displayed for them.
    args[2] is the selected node in the Dropdown menu

    args[1] is the text
    """
    # if a node in the dropdown menu is selected
    if args[2] != None:
        # store the text for the node in the dictionary
        recommendations[args[2]] = args[1]
        database.add_recommendations(args[1], args[2])
        set_logs(f"Recommendation set for node = {args[2]} is  {args[1]}")
    # have to retrun something
    return ''


@callback(Output("text", "value"),
          Input("nodes-dropdown", "value"))
def load_recommendations(id):
    """
    When a node is selected in the dropdown menu, the matching text is displayed
    """
    try:
        text = database.get_recommendations(id)
        set_logs(f"Recommendation for node = {id} ")
    except:
        text = ''
    if text is None:
        return ""
    return text


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8077)
