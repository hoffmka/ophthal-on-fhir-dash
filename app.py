import dash
from aux import bcva_edtrs_to_logmar
from dash import Dash, dcc, html, Input, Output, callback
from fhir_pyrate import Pirate # Library for accessing FHIR resources

import pandas as pd
import plotly.graph_objs as go

########################
# BCVA of OLIVES DATASET
########################

# Setting up connection to the public HAPI FHIR server
search = Pirate(
    auth=None,
    base_url="http://hapi.fhir.org/baseR4", # Base URL of the FHIR server
    print_request_url=True,  # Print the URL calls for debugging
    num_processes=1,
)

# Retrieving observations related to BCVA for patient 201 from OLIVES dataset
observation_all = search.steal_bundles_to_dataframe(  # Non-parallel function that iterates through the bundles and returns them
    resource_type="Observation",
    request_params={
        "patient": "44491871",  # Patient 201 from OLIVES dataset
    },
)

# Filter observations for left eye
observation_left_eye = observation_all.loc[observation_all['bodySite_coding_0_code'] == '362503005']

# Filter observations for right eye
observation_right_eye = observation_all.loc[observation_all['bodySite_coding_0_code'] == '362502000']

# Convert BCVA scores to LogMAR for left eye
observation_left_eye['logmar_value'] = observation_left_eye['valueQuantity_value'].apply(bcva_edtrs_to_logmar)

# Convert BCVA scores to LogMAR for right eye
observation_right_eye['logmar_value'] = observation_right_eye['valueQuantity_value'].apply(bcva_edtrs_to_logmar)

#########################
# Initialize the Dash app
#########################
app = dash.Dash(__name__)

# Initialize figure
fig = go.Figure()


# Define the layout of the app
app.layout = html.Div([
    # Title section
    html.Div(
        children=[
            html.H1(children='Ophthalmology Dash App Example', 
                    style={'textAlign': 'center', 'marginBottom': 30})
        ],
        style={'backgroundColor': '#f2f2f2', 'padding': '20px 40px'}
    ),
    # Change yaxis unit section
    dcc.RadioItems(
        id='yaxis-type',
        options=['EDTRS letters score', 'logMAR'],
        value='EDTRS letters score',
        labelStyle={'display': 'inline-block', 'margin-right': '20px'}
    ),
    # Graph section
    dcc.Graph(
        id='visual-acuity',
        figure=fig
    )
])

# Define callback to update the graph based on the selected option
@callback(
    Output('visual-acuity', 'figure'),
    Input('yaxis-type', 'value'),)
def update_graph(yaxis_type):

    # Create new figure for updated graph
    fig = go.Figure()

    # Adding trace for visual acuity of left eye
    fig.add_trace(go.Scatter(
        x=observation_left_eye['effectiveDateTime'],
        y=observation_left_eye['valueQuantity_value'] if yaxis_type == 'EDTRS letters score' else observation_left_eye['valueQuantity_value'].apply(bcva_edtrs_to_logmar),
        name="Left Eye",
        mode='lines+markers',
    ))

    # Adding trace for visual acuity of right eye
    fig.add_trace(go.Scatter(
        x=observation_right_eye['effectiveDateTime'],
        y=observation_right_eye['valueQuantity_value'] if yaxis_type == 'EDTRS letters score' else observation_right_eye['valueQuantity_value'].apply(bcva_edtrs_to_logmar),
        name="Right Eye",
        mode='lines+markers',
    ))

    # Update layout
    fig.update_layout(
        title="Best Corrected Visual Acuity <br><sup>Patient 201 from the OLIVES Dataset</sup>",
        xaxis_title='Date',
        xaxis_hoverformat='%Y-%m-%d',
        #legend_title_text='Eyes',
        legend=dict(
            orientation="h",  # Set legend orientation to horizontal
            yanchor="bottom",  # Anchor legend to the bottom
            y=1.02,  # Adjust the position of the legend slightly above the bottom
            xanchor="right",  # Anchor legend to the right
            x=1  # Align legend to the right
        )
        )
    # Update layout dependent on selected option
    fig.update_yaxes(
        title='BCVA (ETDRS letters score)' if yaxis_type == 'EDTRS letters score' else 'BCVA (logMAR)',
        range=[0,110] if yaxis_type == 'EDTRS letters score' else [0,1.1]
        )

    # Add normal region to ETDRS
    fig.add_hrect(
        y0=85 if yaxis_type == 'EDTRS letters score' else bcva_edtrs_to_logmar(85), 
        y1=100 if yaxis_type == 'EDTRS letters score' else bcva_edtrs_to_logmar(100), 
        line_width=0, fillcolor="green", opacity=0.2,
        annotation_text="normal range", annotation_position="top left",
        annotation=dict(font_size=14, font_color="green", font_family="Times New Roman"),
        )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
