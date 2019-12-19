##################### 1. Set-up #####################################
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
from datetime import date
from datetime import timedelta

#import functions from our load.py file
from load import groupby_hour, groupby_borough, get_cause_injured, get_sunburst_df, locations_311, locations_top10types_311, events_heatmap, event_type_unique

#define some colors for layout
background = '#29323D'
ny_orange = '#FF6600'
ny_blue = '#003585'
colors = ['#FFFFFF', '#D79922', '#F13C20', '#EFE2BA', '#4056A1', '#C5CBE3']

borough_colors = ['#66FCF1', '#E3AFBC', '#CCCCCC','#8860D0', '#116466', '#CB2D6F']

font_family = 'Open Sans'
legend_color = '#FFFFFF'
legend_size = 14
axis_title_size = 16
graph_title_size = 18
graph_title_color = '#FFFFFF'

#define some relevant permission tokens
mapbox_access_token = 'pk.eyJ1IjoiaXZpdmVrIiwiYSI6ImNrNGI1Y3JocDBhZ3czbm9na28ydzdqcjIifQ.JGbISBeL_5tKAu-moLDEWg'
mapbox_style = "mapbox://styles/ivivek/ck4b5dzrb04d61cqmlxy1oh7v/draft"

# Dictionary of important locations in New York
list_of_locations = {
    "Manhattan: Madison Square Garden": {"lat": '40.7505', "lon": '-73.9934'},
    "Manhattan: New York Stock Exchange": {"lat": '40.7069', "lon": '-74.0113'},
    "Manhattan: United Nations HQ": {"lat": "40.7489", "lon": "-73.9680"},
    "Manhattan: Grand Central Station": {"lat": '40.7527', "lon": "-73.9772"},
    "Manhattan: The Metropolitan Museum of Art": {"lat": "40.7794", "lon": "-73.9632"},
    "Manhattan: Columbia University": {"lat": "40.8075", "lon": "-73.9626"},
    "Bronx: Yankee Stadium": {"lat": '40.8296', "lon": '-73.9262'},
    "Brooklyn: Grand Army Plaza": {"lat": "40.673671", "lon": "-73.970065"},
    "Brooklyn: Coney Island": {"lat": "40.581588", "lon": "-73.971310"},
    "Queens: JFK Airport": {"lat": '40.656987', "lon": '-73.785607'},
    "Queens: Flushing": {"lat": "40.759073", "lon": "-73.829803"},
    "Staten Island: Ferry Terminal": {"lat": "40.643990", "lon": "-74.074634"},
}

options_locations = [{"label":location, "value":location} for location in list_of_locations]


##################### 2. Loading data #####################################

#2.1. accidents
by_hour = groupby_hour()
by_borough = groupby_borough()
cause_acc = get_cause_injured()
sunburst_df = get_sunburst_df(cause_acc)

#2.2. 311 calls
locations_311 = locations_311()

#Load in top 10 types of calls
top10_df = locations_top10types_311()
top10 = [i[0] for i in top10_df.values]
options_types = [{"label":t, "value":t} for t in top10]
options_types = [{'label': 'All', 'value': 'All'}] + options_types

#Assigning colors to the types of calls
palette = ['#CB2D6F', '#65FCB6', '#BCB0E8', '#FCC465', '#bfef45', '#808000', '#ffe119', '#f032e6', '#911eb4', '#66FCF1']
colors = {t:c for t,c in zip(top10, palette)}
colors['others'] = '#9965FC'

#2.3. events
my_events = events_heatmap()
event_type_unique = event_type_unique()

#Define date for default view
today = date.today()
dates = my_events['dates'].unique()
dates = np.insert(dates,0,("Next Week", "Next Two Weeks", "Next Three Weeks", "Next Four Weeks"))
dates_default = dates[0]
df_default = my_events[(my_events['dates'] == dates_default)]
next_week = [today + timedelta(days=x) for x in range(7)]
next_two_weeks = [today + timedelta(days=x) for x in range(14)]
next_three_weeks = [today + timedelta(days=x) for x in range(21)]
next_four_weeks = [today + timedelta(days=x) for x in range(28)]

#Create list of unique event types
event_type_list = []
for sublist in event_type_unique.values.tolist():
    for item in sublist:
        event_type_list.append(item)

#Create gap_fill dataframe to fill in missing boroughs and event types for x and y axis
data = []
borough = ['Manhattan', 'Bronx', 'Queens', 'Brooklyn', 'Staten Island']
for i in borough:
 for j in event_type_list:
  data.append([i,j])
gap_fill = pd.DataFrame(data,columns=['event_borough','event_type'])

#Custom colorscale
custom_colorscale = [
       [0, "#E0FAF8"],
       [0.0001, "#E0FAF8"],

       [0.0001,"#C1F6F2"],
       [0.1, "#C1F6F2"],

       [0.1, "#A9F2EC"],
       [0.2, "#A9F2EC"],

       [0.2, "#66FCF1"],
       [0.3, "#66FCF1"],

       [0.3, "#57DCD2"],
       [0.4, "#57DCD2"],

       [0.4, "#2ED1C5"],
       [0.5, "#2ED1C5"],

       [0.5, "#06C6B8"],
       [0.6, "#06C6B8"],

       [0.6, "#04B1A5"],
       [0.7, "#04B1A5"],

       [0.7, "#039D92"],
       [0.8, "#039D92"],

       [0.8, "#02887F"],
       [0.9, "#02887F"],

       [0.9, "#01746C"],
       [1.0, "#01746C"]
]


##################### 3. App #####################################

#Start dashboard structure
app = dash.Dash('dashboard')

app.layout = html.Div(className = 'layout', children = [
    html.H1('NYC at a Glance', className = 'title'),
    html.H4('A glimpse of 311 calls, events and accidents in the city of New York', className='subtitle'),
    
    #empty DIV to allow some space between titles and graph
    html.Div(className = 'gap-50'),
    
    html.H4('311 Calls', className='section-title'),
    html.H4('Where were the 311 Calls made in the past week and what were the problems?', className='section-subtitle'),
    
    #### 1. Map (Calls)
    # 1.1. Controls
    html.H4('Select a Location', className='left-subtitle'),
    html.H4('Select Complaint Types', className='right-subtitle'),
    
    html.Div(className = 'gap-60'),
    
    html.Div(className='left-half', children =
        dcc.Dropdown(
            id='location-dropdown',
            options=options_locations,
            value=None,
            style={'height': '100%', 'width': '100%'}
        )),
    html.Div(className='right-half', children =
        dcc.Dropdown(
            id='type-dropdown',
            options=options_types,
            value=[i['value'] for i in options_types[1:4]],
            multi=True,
            style={'height': '100%', 'width': '100%'})),
    html.Div(className = 'gap-50'),
    
    # 1.2. Figure
    html.Div(className='map', children = [
    dcc.Graph(id="my-map",
        figure={})
    ],
        style={"width" : "100%", "height": "600px"}),

    html.Div(className = 'gap-50'),

    #### 2. HeatMap (Events)
    
    html.H4('Upcoming Events', className='section-title'),

    # 2.1. Figure
    html.H4('What events are coming up in the next month and where are they happening?', className='section-subtitle'),
    html.H4('Select Date', className='left-subtitle'),
    html.Div(className = 'gap-60'),
    html.Div([
    html.Div([
        dcc.Dropdown(
            id='dates_dropdown',
            options=[{'label': date, 'value': date} for date in dates],
            value = dates_default
        ),
    ],
             style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div(className = 'gap-30'),

        dcc.Graph(id='heatmap',
                  figure = {
                      'data': [go.Heatmap(
                          x=df_default['event_borough'],
                          y=df_default['event_type'],
                          z=df_default['event_count'],
                          name = 'first legend group',

                          colorscale=custom_colorscale)],
                      'layout': go.Layout(
                          margin = dict(r=200,l=200),
                          xaxis = dict(title = 'Borough'),
                          yaxis = dict( title = dict(text = 'Event Type', standoff = 20)),
                      )})
    ]),

    html.Div(className = 'gap-50'),

    #### 3. BarGraphs & BubbleGraphs (Accidents)
    
    html.H4('Accidents', className='section-title'),
    html.H4('Who has been getting injured in the past week?', className='section-subtitle'),

    # 3.1. Controls
    
    html.H4('Select Type of Road User', className='left-subtitle'),
    html.Div(className = 'gap-60'),

    html.Div(className='accidents-controls', children = [
        dcc.RadioItems(
                id='accidents-buttons',
                options=[{'label': 'All', 'value': 0},
                {'label': 'Pedestrians', 'value': 1},
                {'label': 'Cyclists', 'value': 2},
                {'label': 'Motorists', 'value': 3}],
                value = 0,
                labelStyle={'display': 'inline-block'}
            )
        ]),
    
    html.Div(className = 'gap-30'),

    # 3.2. Figures

    html.Div(className='accidents-bars', children = [
        #accidents bar graph
        dcc.Graph(id='accidents-bars')
        ],
        style={"height": '500px', "width" : "100%"}),
    
    html.Div(className='accidents-bubbles', children = [
        #accidents bubble graph
        dcc.Graph(id='accidents-bubbles')
        ],
        style={"height": '500px', "width" : "100%"}),

    #### 4. Sunburst (Accidents)

    # 4.1. Figure
    html.H4('What is causing injuries from traffic accidents in the city?', className='section-subtitle'),
    html.Div(className = 'gap-30'),
    
    html.Div(className='sunburst', children = [
    #sunburst figure for accidents
    dcc.Graph(id='accidents-sunburst',
        figure = go.Figure(
            go.Sunburst(
            labels= sunburst_df['labels'],
            parents= sunburst_df['parents'],
            values= sunburst_df['number'],
            branchvalues="total",
            insidetextfont = {"family": font_family, "size": 14, "color": legend_color},
            outsidetextfont = {"family": font_family, "size": 14, "color": legend_color},
            marker = {"line": {"width": 2},
                      "colors": [background, '#CB2D6F','#66FCF1', '#9A174F', '#CCCCCC',
                                       '#00C2CC','#66FCF1', '#9A174F', '#CCCCCC',
                                       '#116466','#66FCF1', '#9A174F', '#CCCCCC',
                                       '#A3A3A3','#66FCF1', '#9A174F', '#CCCCCC',
                                       '#501F3A','#66FCF1', '#9A174F', '#CCCCCC']
                                       },
            leaf = {'opacity': 0.25}
            ),
            layout =  {'margin': dict(t=0, l=0, r=0, b=0),
                            'paper_bgcolor': background,
                            'plot_bgcolor': background,
                            'height': 600}
        ))
    ],
    style={"height": '600px', "width" : "100%"})
])


##################### 4. Callbacks ###################################

#### 4.1. Calls
@app.callback(
    dash.dependencies.Output('my-map', 'figure'),
    [dash.dependencies.Input('location-dropdown', 'value'),
     dash.dependencies.Input('type-dropdown', 'value')])
def update_output(value, value_type):
    top = 0
    bottom = 0
    right = 0
    left = 0
    if len(value_type) == 0:
        if value is None:
            updated = dict(data=[
                        dict(
                            lat=["30.0000"],
                            lon=["30.0000"],
                            mode='markers',
                            marker=go.scattermapbox.Marker(
                            size=0
                            ),
                            type="scattermapbox",
                            hoverinfo=None
                        )
                    ],
                    layout=dict(
                        mapbox=dict(
                            layers=[],
                            accesstoken=mapbox_access_token,
                            style=mapbox_style,
                            center=dict(
                                lat=40.7128,
                                lon=-73.9750
                            ),
                            pitch=0,
                            zoom=12,
                        ),
                        margin=dict(t=top, b=bottom, l=left, r=right),
                        height=600,
                        autosize=True,
                        paper_bgcolor = background, plot_bgcolor = background,
                        legend = dict(font = dict(family = font_family, size = legend_size, color = legend_color))
                        ))
        else:
            updated = dict(data=[
                        dict(
                            lat=[list_of_locations[value]['lat']],
                            lon=[list_of_locations[value]['lon']],
                            mode='markers',
                            marker=go.scattermapbox.Marker(
                            size=10,
                            color='#f58231'
                            ),
                            type="scattermapbox",
                            name=value,
                            hoverinfo='text',
                            text=value,
                        )
                    ],
                    layout=dict(
                        mapbox=dict(
                            layers=[],
                            accesstoken=mapbox_access_token,
                            style=mapbox_style,
                            center=dict(
                                lat=list_of_locations[value]['lat'],
                                lon=list_of_locations[value]['lon']
                            ),
                            pitch=0,
                            zoom=13,
                        ),
                        showlegend=True,
                        margin=dict(t=top, b=bottom, l=left, r=right),
                        height=600,
                        autosize=True,
                        paper_bgcolor = background, plot_bgcolor = background,
                        legend = dict(font = dict(family = font_family, size = legend_size, color = legend_color))
                        ))
    elif 'All' in value_type:

        data_filtered = []

        for y in top10:

            indices = [i for i,x in enumerate(locations_311.complaint_type) if x == y]
            locations_311_type = locations_311.iloc[indices,:]

            data_filtered.append(dict(
                lat=[i for i in locations_311_type.latitude],
                lon=[i for i in locations_311_type.longitude],
                mode='markers',
                marker=go.scattermapbox.Marker(
                size=5,
                color = colors[y]
                ),
                type="scattermapbox",
                name=y,
                hoverinfo='text',
                text=[str(i)+'<br>'+str(y)+'<br>'+str(k) for i,k in zip(locations_311_type.agency_name, locations_311_type.descriptor)]
            ))

        indices = [i for i,x in enumerate(locations_311.complaint_type) if x not in top10]
        locations_311_others = locations_311.iloc[indices,:]
        data_filtered.append(
            dict(
                lat=[i for i in locations_311_others.latitude],
                lon=[i for i in locations_311_others.longitude],
                mode='markers',
                marker=go.scattermapbox.Marker(
                size=5,
                color = colors['others']
                ),
                type="scattermapbox",
                name='Others',
                hoverinfo='text',
                text=[str(i)+'<br>'+str(j)+'<br>'+str(k) for i,j,k in zip(locations_311_others.agency_name, locations_311_others.complaint_type, locations_311_others.descriptor)]
            )
        )

        if value is None:
            updated = dict(data=data_filtered,
                    layout=dict(
                         mapbox=dict(
                            layers=[],
                            accesstoken=mapbox_access_token,
                            style=mapbox_style,
                            center=dict(
                                lat=40.7128,
                                lon=-73.9750
                            ),
                            pitch=0,
                            zoom=12,
                        ),
                        showlegend=True,
                        margin=dict(t=top, b=bottom, l=left, r=right),
                        height=600,
                        autosize=True,
                        paper_bgcolor = background, plot_bgcolor = background,
                        legend = dict(font = dict(family = font_family, size = legend_size, color = legend_color))
                        ))
        else:
             updated = dict(data=[dict(
                            lat=[list_of_locations[value]['lat']],
                            lon=[list_of_locations[value]['lon']],
                            mode='markers',
                            marker=go.scattermapbox.Marker(
                            size=10,
                            color='#f58231'
                            ),
                            type="scattermapbox",
                            name=value,
                            hoverinfo='text',
                            text=value,
                        )
                    ] + data_filtered,
                    layout=dict(
                        mapbox=dict(
                            layers=[],
                            accesstoken=mapbox_access_token,
                            style=mapbox_style,
                            center=dict(
                                lat=list_of_locations[value]['lat'],
                                lon=list_of_locations[value]['lon']
                            ),
                            pitch=0,
                            zoom=13,
                        ),
                        showlegend=True,
                        margin=dict(t=top, b=bottom, l=left, r=right),
                        height=600,
                        autosize=True,
                        paper_bgcolor = background, plot_bgcolor = background,
                        legend = dict(font = dict(family = font_family, size = legend_size, color = legend_color))
                        ))
    else:

        data_filtered = []

        for y in value_type:

            indices = [i for i,x in enumerate(locations_311.complaint_type) if x == y]
            locations_311_type = locations_311.iloc[indices,:]

            data_filtered.append(dict(
                lat=[i for i in locations_311_type.latitude],
                lon=[i for i in locations_311_type.longitude],
                mode='markers',
                marker=go.scattermapbox.Marker(
                size=5,
                color = colors[y]
                ),
                type="scattermapbox",
                name=y,
                hoverinfo='text',
                text=[str(i)+'<br>'+str(y)+'<br>'+str(k) for i,k in zip(locations_311_type.agency_name, locations_311_type.descriptor)]
            ))

        if value is None:
            updated = dict(data=data_filtered,
                    layout=dict(
                        mapbox=dict(
                            layers=[],
                            accesstoken=mapbox_access_token,
                            style=mapbox_style,
                            center=dict(
                                lat=40.7128,
                                lon=-73.9750
                            ),
                            pitch=0,
                            zoom=12,
                        ),
                        showlegend=True,
                        margin=dict(t=top, b=bottom, l=left, r=right),
                        height=600,
                        autosize=True,
                        paper_bgcolor = background, plot_bgcolor = background,
                        legend = dict(font = dict(family = font_family, size = legend_size, color = legend_color))
                        ))
        else:
             updated = dict(data=[
                        dict(
                            lat=[list_of_locations[value]['lat']],
                            lon=[list_of_locations[value]['lon']],
                            mode='markers',
                            marker=go.scattermapbox.Marker(
                            size=10,
                            color='#f58231'
                            ),
                            type="scattermapbox",
                            name=value,
                            hoverinfo='text',
                            text=value,
                        )
                    ] + data_filtered,
                    layout=dict(
                        mapbox=dict(
                            layers=[],
                            accesstoken=mapbox_access_token,
                            style=mapbox_style,
                            center=dict(
                                lat=list_of_locations[value]['lat'],
                                lon=list_of_locations[value]['lon']
                            ),
                            pitch=0,
                            zoom=13,
                        ),
                        showlegend=True,
                        margin=dict(t=top, b=bottom, l=left, r=right),
                        height=600,
                        autosize=True,
                        paper_bgcolor = background, plot_bgcolor = background,
                        legend = dict(font = dict(family = font_family, size = legend_size, color = legend_color))
                        ))

    return updated

#### 4.2. Events
@app.callback(
    Output('heatmap','figure'),
    [Input('dates_dropdown','value')]
)
def update_graph(selected_date):

    def get_dict(heatmap_data, title):
        return_dict = {
        'data': [go.Heatmap(
            x=heatmap_data['event_borough'],
            y=heatmap_data['event_type'],
            z=heatmap_data['event_count'],
            xgap= 0.05,
            ygap = 0.05,
            name = 'first legend group',
            colorscale=custom_colorscale,
            colorbar = dict(title = 'No. of events',titlefont = dict(family = font_family, size = axis_title_size, color = legend_color), tickfont = dict(family = font_family,
                                size = legend_size, color = legend_color))
                )
            ],

        'layout': go.Layout(margin = dict(r=200,l=275),
                title = dict(text = title, font = dict(family = font_family, size = axis_title_size, color = legend_color), x = 0.5, y = 0.9),
                xaxis = dict(title = dict(text =  'Borough',
                                font = dict(family = font_family,
                                size = axis_title_size, color = legend_color)),
                            tickfont = dict(family = font_family,
                                size = legend_size, color = legend_color)
                            ),
                yaxis = dict(title = dict(text =  'Event Type', standoff=20,
                                font = dict(family = font_family,
                                size = axis_title_size, color = legend_color)),
                            tickfont = dict(family = font_family,
                                size = legend_size, color = legend_color)
                            ),
                paper_bgcolor = background, plot_bgcolor = background
            )
        }
        return return_dict


    if selected_date == 'Next Four Weeks':
        heatmap_data = my_events[my_events['dates_dt'].isin(next_four_weeks)][['event_borough','event_type','event_count']]
        heatmap_data = pd.merge(heatmap_data, gap_fill, on=['event_borough', 'event_type'],how='outer').fillna(0)
        maxsale = heatmap_data[heatmap_data['event_count']==heatmap_data['event_count'].max()]
        maxsale = maxsale.reset_index()
        title = 'Number and Type of Upcoming Events for the Next Four Weeks'
        return_dict = get_dict(heatmap_data, title)
        return return_dict

    elif selected_date == 'Next Three Weeks':
        heatmap_data = my_events[my_events['dates_dt'].isin(next_three_weeks)][['event_borough','event_type','event_count']]
        heatmap_data = pd.merge(heatmap_data, gap_fill, on=['event_borough', 'event_type'],how='outer').fillna(0)
        maxsale = heatmap_data[heatmap_data['event_count']==heatmap_data['event_count'].max()]
        maxsale = maxsale.reset_index()
        title = 'Number and Type of Upcoming Events for the Next Three Weeks'
        return_dict = get_dict(heatmap_data, title)
        return return_dict


    elif selected_date == 'Next Two Weeks':
        heatmap_data = my_events[my_events['dates_dt'].isin(next_two_weeks)][['event_borough','event_type','event_count']]
        heatmap_data = pd.merge(heatmap_data, gap_fill, on=['event_borough', 'event_type'],how='outer').fillna(0)
        maxsale = heatmap_data[heatmap_data['event_count']==heatmap_data['event_count'].max()]
        maxsale = maxsale.reset_index()
        title = 'Number and Type of Upcoming Events for the Next Two Weeks'
        return_dict = get_dict(heatmap_data, title)
        return return_dict

    elif selected_date == 'Next Week':
        heatmap_data = my_events[my_events['dates_dt'].isin(next_week)][['event_borough','event_type','event_count']]
        heatmap_data = pd.merge(heatmap_data, gap_fill, on=['event_borough', 'event_type'],how='outer').fillna(0)
        maxsale = heatmap_data[heatmap_data['event_count']==heatmap_data['event_count'].max()]
        maxsale = maxsale.reset_index()
        title = 'Number and Type of Upcoming Events for the Next Week'
        return_dict = get_dict(heatmap_data, title)
        return return_dict

    else:
        heatmap_data = my_events.loc[my_events['dates_dt'] == selected_date][['event_borough','event_type','event_count']]
        heatmap_data = pd.merge(heatmap_data, gap_fill, on=['event_borough', 'event_type'],how='outer').fillna(0)
        maxsale = heatmap_data[heatmap_data['event_count']==heatmap_data['event_count'].max()]
        maxsale = maxsale.reset_index()
        title = 'Number and Type of Upcoming Events for '+str(selected_date)
        return_dict = get_dict(heatmap_data, title)
        return return_dict

#### 4.3. Accidents
@app.callback(
    Output('accidents-bars', 'figure'),
    [Input('accidents-buttons', 'value')])
def update_accidents_bar(selected_button):

    traces = []
    if selected_button == 0:
        traces.append(
        go.Bar(
            x=by_hour.index,
            y=by_hour.persons_injured,
            name='All persons injured',
            textposition='auto',
            marker = {'color' : '#66FCF1'}
        ))
        title = 'Number of People Injured by Time of Day'

    elif selected_button == 1:
        traces.append(
        go.Bar(
            x=by_hour.index,
            y=by_hour.pedestrians_injured,
            name='Pedestrians injured',
            textposition='auto',
            marker = {'color' : '#CB2D6F'}
        ))
        title = 'Number of Pedestrians Injured by Time of Day'

    elif selected_button == 2:
        traces.append(
        go.Bar(
            x=by_hour.index,
            y=by_hour.cyclists_injured,
            name='Cyclists injured',
            marker = {'color' : '#CCCCCC'}
        ))
        title = 'Number of Cyclists Injured by Time of Day'

    elif selected_button == 3:
        traces.append(
        go.Bar(
            x=by_hour.index,
            y=by_hour.motorists_injured,
            name='Motorists injured',
            marker = {'color' : '#8860D0'}
        ))
        title = 'Number of Motorists Injured by Time of Day'

    #dictionary to return updated graph
    dict_return = {
    'data': traces,
    'layout': {'title': {'text': title,
                               'font': {'family': font_family, 'color': graph_title_color},
                               'x': 0.5, 'y': 0.9},
                    'margin': {'pad': 20},
                    'paper_bgcolor': background,
                    'plot_bgcolor': background,
                     'xaxis': {'showgrid': False, 'tickfont': {'family': font_family, 'color': legend_color}},
                     'yaxis': {'tickfont': {'family': font_family, 'color': legend_color}},
                     'legend' : {'x': 1, 'y': 1, 'font': dict(family = font_family, size = legend_size, color = legend_color)}
                     }
                }

    return dict_return

@app.callback(
    Output('accidents-bubbles', 'figure'),
    [Input('accidents-buttons', 'value')])
def update_accidents_bubbles(selected_button):

    traces = []
    if selected_button == 0:
        traces.append(
        go.Scatter(
            x=by_borough.index,
            y=by_borough.persons_injured,
            name='All persons injured',
            mode= 'markers',
            marker = {'size': np.array(by_borough.persons_injured),
                      'color': borough_colors, 'line': {'color': borough_colors, 'width': 1}}
            )
        )
        title = 'Number of People Injured by Borough'

    elif selected_button == 1:
        traces.append(
        go.Scatter(
            x=by_borough.index,
            y=by_borough.pedestrians_injured,
            name='Pedestrians injured',
            mode= 'markers',
            marker = {'size': np.array(by_borough.pedestrians_injured)*2,
                      'color' : borough_colors,  'line': {'color': borough_colors, 'width': 1}}
        ))
        title = 'Number of Pedestrians Injured by Borough'

    elif selected_button == 2:
        traces.append(
        go.Scatter(
            x=by_borough.index,
            y=by_borough.cyclists_injured,
            name='Cyclists injured',
            mode= 'markers',
            marker = {'size': np.array(by_borough.cyclists_injured)*12,
                      'color' : borough_colors, 'line': {'color': borough_colors, 'width': 1}}
        ))
        title = 'Number of Cyclists Injured by Borough'

    elif selected_button == 3:
        traces.append(
        go.Scatter(
            x=by_borough.index,
            y=by_borough.motorists_injured,
            name='Motorists injured',
            mode= 'markers',
            marker = {'size': np.array(by_borough.motorists_injured),
                      'color' : borough_colors, 'line': {'color': borough_colors, 'width': 1}}
        ))
        title = 'Number of Motorists Injured by Borough'

    #dictionary to return updated graph
    dict_return = {
    'data': traces,
    'layout': {'title': {'text': title,
                               'font': {'family': font_family, 'color': graph_title_color},
                               'x': 0.5, 'y': 0.9},
                    'margin': {'pad': 20},
                    'paper_bgcolor': background,
                    'plot_bgcolor': background,
                     'xaxis': {'showgrid': False, 'tickfont': {'family': font_family, 'color': legend_color}},
                     'yaxis': {'tickfont': {'family': font_family, 'color': legend_color}},
                     'legend' : {'x': 1, 'y': 1, 'font': dict(family = font_family, size = legend_size, color = legend_color)}
                     }
                }

    return dict_return

##################### 5. Launching the app #################################

#RUN THE APP!
if __name__ == '__main__':
    app.run_server(debug=True)
