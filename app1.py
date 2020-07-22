import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

external_stylesheets = ['https://codepen.io/mainaminor/pen/wvaOEmY.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, 
  meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Global Electricity Generation Mix</title>
        <meta property="og:title" content="Global Electricity Generation Mix">
        <meta property="og:image" content="assets/screenshot.png">
        <meta name="description" property="og:description" content="An interactive mini-dashboard built and deployed by me in Python, giving a summary of electricity generation mix by fuel and country.">
        <meta name="author" content="Anthony S N Maina">
        {%favicon%}
        {%css%}
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

server = app.server

##############################
####### DATA TABLES ##########
##############################

master_elec=pd.read_csv("data/master_elec.csv")
df_dep=pd.read_csv("data/elec_dep.csv")
df_dom=pd.read_csv("data/dominant_source.csv")
df_growth=pd.read_csv("data/df_growth.csv")
df=pd.read_json("data/IntElecGen.json")

metrics=[
      {'label': 'Dominant power source for electricity generation', 'value': 'dominant'},
      {'label': 'Total net electricity generation', 'value': "lastValue"},
      {'label': 'Electricity generation per capita', 'value': "kWh PP"},  
  ]

ren=["Hydroelectricity", "Wind", "Biomass and waste", "Solar", "Geothermal", "Tide and wave"]

metrics_max=[
      {'label': 'Fossil fuels', 'value': 'Fossil fuels'},
      {'label': 'Nuclear', 'value': 'Nuclear'},
      {'label': 'Renewables (all)', 'value': 'Renewable'},  
      {'label': 'Renewables: Hydroelectricity', 'value': 'Hydroelectricity'},
      {'label': 'Renewables: Biomass and waste', 'value': 'Biomass and waste'},  
      {'label': 'Renewables: Geothermal', 'value': 'Geothermal'},
      {'label': "Renewables: Solar","value":"Solar"},
      {'label': "Renewables: Wind","value":"Wind"},
      {'label': 'Total generation', 'value': "Total Electricity net generation"}
]

colors=pd.DataFrame({'value': ['Total Electricity net generation', 'Fossil fuels','Nuclear', 'Renewable','Hydroelectricity', 'Wind','Biomass and waste', 'Solar',  'Geothermal', 'Tide and wave'],
       "color": ['#636EFA','rgb(102,102,102)','#EF553B','#00CC96','#1F77B4', 'rgb(102, 197, 204)', 'rgb(248, 156, 116)', 'rgb(246, 207, 113)', 'rgb(220, 176, 242)', 'rgb(135, 197, 95)']
      })

cats=['Solar electricity net generation',
 'Nuclear electricity net generation',
 'Tide and wave electricity net generation',
 'Renewable electricity net generation',
 'Hydroelectricity net generation',
 'Electricity net generation',
 'Non-hydro renewable electricity net generation',
 'Hydroelectric pumped storage electricity net generation',
 'Solar, tide, wave, fuel cell electricity net generation',
 'Wind electricity net generation',
 'Geothermal electricity net generation',
 'Fossil fuels electricity net generation',
 'Biomass and waste electricity net generation']

cat=[]
label=[]
country=[]

for i in df["name"]:
    if 'Solar, tide, wave, fuel cell electricity net generation' in i:
        cat.append('Solar, tide, wave, fuel cell electricity net generation')
    else:
        for c in cats:
            if c == i.split(",")[0]:
                cat.append(c)


for c in cat:
    if c=="Electricity net generation":
        label.append("Total Electricity net generation")
    elif c=="Hydroelectricity net generation":
        label.append("Hydroelectricity")
    else:
        label.append(c.split(" electricity net generation")[0])
        

for n in df["name"]:
    if 'Solar, tide, wave, fuel cell electricity net generation' in n:
        country.append(n.split(', ')[4])
    else:
        country.append(n.split(", ")[1])

df["country"]=country
df["label"]=label

countries = []
for tic in master_elec["country"].drop_duplicates().sort_values():
  countries.append({'label':tic, 'value':tic})


################################
###### LAYOUT COLORS ###########
################################

boxcolor="#F5F5F5"
background="#FFFFFF"
headercolor="#3d3d5c"
titlecolor="#3d3d5c"

################################
###### CHART LAYOUTS ###########
################################


#WORLD & US MAPS
l_map=go.Layout(
    height=400,
    margin={"r":0,"t":0,"l":0,"b":0},
    geo={
    'visible': True, 
    'resolution':50, 
    'showcountries':True, 
    'countrycolor':"grey",
    'showsubunits':True, 
    'subunitcolor':"White",
    'showframe':False,
    'coastlinecolor':"slategrey",
    'countrycolor':'white',
    }
)


#WORLD BARS
l_bar_w=go.Layout(
  height=324,
  #width=90,
  margin={"r":20,"t":60,"l":40,"b":20},
  #template="plotly_white",
  plot_bgcolor=boxcolor,
  paper_bgcolor=boxcolor,
  yaxis={"tickfont":{"size":12},"gridwidth":2, "gridcolor":background},
  xaxis={"tickfont":{"size":12}},
  legend={'orientation':'h','x':0.1, 'y':-0.2,'font':{'size':12}, 'itemclick': 'toggleothers'},
  dragmode=False
  )

#SIMPLE BARS
l_bar_s=go.Layout(
  height=200,
  margin={"r":10,"t":10,"l":10,"b":20},
  #template="plotly_white",
  plot_bgcolor=boxcolor,
  paper_bgcolor=boxcolor,
  yaxis={"tickfont":{"size":10}},
  xaxis={"tickfont":{"size":10},"gridwidth":2,"gridcolor":background},
  font={"size":10},
  legend={'x':0.02, 'y':0.96, 'font':{'size':10}, 'itemclick': 'toggleothers'},
  dragmode=False
  )

#HIDE MODEBAR
conf = {'displayModeBar': False}



###############################
######## CHARTS ###############
###############################

def make_fig_1a():
  df=df_dom
  df=df.merge(df_dep, how="left", left_on=["country", "dominant_source"], right_on=["country", "label"])
  df["percent_dep"]=round(100*df["dependence"],0).astype("int")
  df.drop(df[df["dependence"]==0].index.values, inplace=True)
  df["text"]=df["country"]+"<br>"+df["dominant_source"]+ " ("+df["percent_dep"].astype("str")+"%"+" dependent"+")"
  fig = go.Figure(data=go.Choropleth(
      locations = df['iso'],
      z = df['score'],
      text = df['text'],
      hoverinfo= 'text',
      showscale = False,
      colorscale=[[0, colors["color"][3]], [0.5, colors["color"][2]], [1.0, colors["color"][1]]],
      marker_line_width=0.5,
      marker_line_color='white',
  ))
  fig.update_layout({"geo": {"projection_type": "natural earth", "lataxis_range": [-60,85]}})
  fig.update_layout(l_map)
  return fig

def make_fig_1(value):
  table=master_elec
  metric="Total Electricity net generation"
  if value=="lastValue":
    mult=0.5
    name="Total generation"
    unit="bln kWh"
  else:
    mult=20
    name="Per capita generation"
    unit="thousand kWh PP"


  df=table[table["label"]==metric]
  df["text"]= df["country"] +'<br>' + name + ": "+'<br>' + round(df[value],2).astype('str')+" "+unit

  d = go.Figure(go.Scattergeo(
      lon=df["long"],
      lat=df["lat"],
      text = df['text'],
      hoverinfo = 'text',
      marker=dict(
          size= mult*df[value],
          line_width=0.5,
          sizemode='area',
          color="#636EFA"
      )))
  fig1=go.Figure(data=d)
  fig1.update_layout(l_map)
  fig1.update_geos(projection_type="natural earth", lataxis_showgrid=False, lonaxis_showgrid=False,lataxis_range=[-60,85])
  return fig1



def make_fig_3(d, label, metric, clip_pos):
    if clip_pos==1:
        fig = go.Figure(go.Bar(y=d[d["label"]==label].sort_values(by=metric, ascending=True)["country"][-11:-1],
                              x=d[d["label"]==label].sort_values(by=metric,ascending=True)[metric][-11:-1],
                             orientation='h',
                             marker_color=colors["color"][colors["value"]==label].values[0]
                            )
                     )
    else:
        fig = go.Figure(go.Bar(y=d[d["label"]==label].sort_values(by=metric, ascending=True)["country"][-10:],
                              x=d[d["label"]==label].sort_values(by=metric,ascending=True)[metric][-10:],
                             orientation='h',
                             marker_color=colors["color"][colors["value"]==label].values[0]
                            )
                     )
    fig.update_layout(l_bar_s)
    return fig

def make_fig_2(geo):
    k=df["data"][df["country"]==geo]

    x=[]
    y=[]
    name="Fossil fuels"
    for i in range(len(k[df["label"]==name].iloc[0])):
        x.append(pd.to_datetime(k[df["label"]==name].iloc[0][i]["date"], unit="ms"))
        y.append(k[df["label"]==name].iloc[0][i]["value"])
        y=[0 if x =="(s)" else x for x in y]
        y=[0 if x =="NA" else x for x in y]

    x2=[]
    y2=[]
    name2="Nuclear"
    for i in range(len(k[df["label"]==name2].iloc[0])):
        x2.append(pd.to_datetime(k[df["label"]==name2].iloc[0][i]["date"], unit="ms"))
        y2.append(k[df["label"]==name2].iloc[0][i]["value"])
        y2=[0 if x =="(s)" else x for x in y2]
        y2=[0 if x =="NA" else x for x in y2]

    x3=[]
    y3=[]
    name3="Renewable"
    for i in range(len(k[df["label"]==name3].iloc[0])):
        x3.append(pd.to_datetime(k[df["label"]==name3].iloc[0][i]["date"], unit="ms"))
        y3.append(k[df["label"]==name3].iloc[0][i]["value"])
        y3=[0 if x =="(s)" else x for x in y3]
        y3=[0 if x =="NA" else x for x in y3]

    fig = go.Figure()
    fig.add_trace(go.Bar(
      x=x[:-1], 
      y=y[:-1],
      hoverinfo='name+y',
      name=name,
      marker_color=colors["color"][colors["value"]==name].values[0]
    ))
    fig.add_trace(go.Bar(
      x=x2[:-1], 
      y=y2[:-1],
      hoverinfo='name+y',
      name=name2,
      marker_color=colors["color"][colors["value"]==name2].values[0]
    ))
    fig.add_trace(go.Bar(
      x=x3[:-1], 
      y=y3[:-1],
      hoverinfo='name+y',
      name=name3,
      marker_color=colors["color"][colors["value"]==name3].values[0]
    ))

    fig.update_layout(barmode='stack')
    fig.update_layout(l_bar_w)
    return fig


def make_fig_2b(geo):
    k=df["data"][df["country"]==geo]

    x=[]
    y=[]
    name="Hydroelectricity"
    for i in range(len(k[df["label"]==name].iloc[0])):
        x.append(pd.to_datetime(k[df["label"]==name].iloc[0][i]["date"], unit="ms"))
        y.append(k[df["label"]==name].iloc[0][i]["value"])
        y=[0 if x =="(s)" else x for x in y]
        y=[0 if x =="NA" else x for x in y]

    x2=[]
    y2=[]
    name2="Wind"
    for i in range(len(k[df["label"]==name2].iloc[0])):
        x2.append(pd.to_datetime(k[df["label"]==name2].iloc[0][i]["date"], unit="ms"))
        y2.append(k[df["label"]==name2].iloc[0][i]["value"])
        y2=[0 if x =="(s)" else x for x in y2]
        y2=[0 if x =="NA" else x for x in y2]

    x3=[]
    y3=[]
    name3="Biomass and waste"
    for i in range(len(k[df["label"]==name3].iloc[0])):
        x3.append(pd.to_datetime(k[df["label"]==name3].iloc[0][i]["date"], unit="ms"))
        y3.append(k[df["label"]==name3].iloc[0][i]["value"])
        y3=[0 if x =="(s)" else x for x in y3]
        y3=[0 if x =="NA" else x for x in y3]
    
    x4=[]
    y4=[]
    name4="Solar"
    for i in range(len(k[df["label"]==name4].iloc[0])):
        x4.append(pd.to_datetime(k[df["label"]==name4].iloc[0][i]["date"], unit="ms"))
        y4.append(k[df["label"]==name4].iloc[0][i]["value"])
        y4=[0 if x =="(s)" else x for x in y4]
        y4=[0 if x =="NA" else x for x in y4]
    
    x5=[]
    y5=[]
    name5="Geothermal"
    for i in range(len(k[df["label"]==name5].iloc[0])):
        x5.append(pd.to_datetime(k[df["label"]==name5].iloc[0][i]["date"], unit="ms"))
        y5.append(k[df["label"]==name5].iloc[0][i]["value"])
        y5=[0 if x =="(s)" else x for x in y5]
        y5=[0 if x =="NA" else x for x in y5]
    
    x6=[]
    y6=[]
    name6="Tide and wave"
    for i in range(len(k[df["label"]==name6].iloc[0])):
        x6.append(pd.to_datetime(k[df["label"]==name6].iloc[0][i]["date"], unit="ms"))
        y6.append(k[df["label"]==name6].iloc[0][i]["value"])
        y6=[0 if x =="(s)" else x for x in y6]
        y6=[0 if x =="NA" else x for x in y6]
        

    fig = go.Figure()
    fig.add_trace(go.Bar(
      x=x[:-1], 
      y=y[:-1],
      hoverinfo='name+y',
      name=name,
      marker_color=colors["color"][colors["value"]==name].values[0]
    ))
    fig.add_trace(go.Bar(
      x=x2[:-1], 
      y=y2[:-1],
      hoverinfo='name+y',
      name=name2,
      marker_color=colors["color"][colors["value"]==name2].values[0]
    ))
    fig.add_trace(go.Bar(
      x=x3[:-1], 
      y=y3[:-1],
      hoverinfo='name+y',
      name=name3,
      marker_color=colors["color"][colors["value"]==name3].values[0]
    ))
    
    fig.add_trace(go.Bar(
      x=x4[:-1], 
      y=y4[:-1],
      hoverinfo='name+y',
      name=name4,
      marker_color=colors["color"][colors["value"]==name4].values[0]
    ))
    
    fig.add_trace(go.Bar(
      x=x5[:-1], 
      y=y5[:-1],
      hoverinfo='name+y',
      name=name5,
      marker_color=colors["color"][colors["value"]==name5].values[0]
    ))
    
    fig.add_trace(go.Bar(
      x=x6[:-1], 
      y=y6[:-1],
      hoverinfo='name+y',
      name=name6,
      marker_color=colors["color"][colors["value"]==name6].values[0]
    ))

    fig.update_layout(barmode='stack'),
    fig.update_layout(l_bar_w),
    fig.update_layout(legend={'orientation':'h','x':0.05, 'y':-0.2,'font':{'size':12}})
    return fig



################################################
#### APP LAYOUT  ###############################
################################################

app.layout = html.Div([

  html.Div([#header
    html.Div([
      html.H3("Global Electricity Generation Mix", style={"color": headercolor, "marginBottom": "0.2%"}),
      html.P('Data source: U.S. Energy Information Administration',style={'font-size': '1rem','color':'#696969',"marginBottom": "0%"}),
      ],
    className='row',
    style={'paddingTop':'0%', 'text-align':'center', "margin":"1%"}
    ),
  html.Div([#body
    html.Div([#left six columns
      html.Div([#left side top half
        html.H5("Worldwide, as of 2017", style={"color": titlecolor, "marginBottom": "2%"}),
        html.Div([
          dcc.Dropdown(
            id='metric-select-ww',
            options = metrics,
            value = metrics[0]["value"],
            multi = False
            )
          ],
          style={"marginBottom":"2%"}
          ),
        dcc.Graph(
          id="world_map",
          figure=make_fig_1a(),
          config=conf
          )
        ],
        style={'background-color':boxcolor,'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','padding':'1%', 'marginBottom':'2%'},
        className='row'
        ),
      html.Div([#left side bottom half
        html.Div([#left side bottom half four columns
          html.P(id="abs_title", children="Top 10 total, by fuel type", style={"color": titlecolor}),
          html.Div([
            dcc.Dropdown(
              id='metric-select-abs',
              options = metrics_max,
              value = metrics_max[0]["value"],
              multi = False
              ),
            ],
            style={'marginBottom':'4%','font-size': '1.2rem'}
            ),
          dcc.Graph(
            id="top_10_abs",
            figure=make_fig_3(master_elec, metrics_max[0]["value"], "lastValue",1),
            config=conf
            )
          ],
          style={'background-color':boxcolor,'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','padding':'1%', 'marginBottom':'2%'},
          className="four columns flex-display"
          ),
        html.Div([#left side bottom half four columns
          html.P(id="capita_title", children="Top 10 per capita, by fuel type", style={"color": titlecolor}),
          html.Div([
            dcc.Dropdown(
              id='metric-select-cap',
              options = metrics_max,
              value = metrics_max[0]["value"],
              multi = False
              ),
            ],
            style={'marginBottom':'4%','font-size': '1.2rem'}
            ),
          dcc.Graph(
            id="top_10_ren",
            figure=make_fig_3(master_elec, metrics_max[0]["value"], "kWh PP",0),
            config=conf
            )
          ],
          style={'background-color':boxcolor,'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','padding':'1%', 'marginBottom':'2%'},
          className="four columns flex-display"
          ),
        html.Div([#left side bottom half four columns
          html.P(id="dep_title", children= "Top 10 dependence, by power source", style={"color": titlecolor}),
          html.Div([
            dcc.Dropdown(
              id='metric-select-dep',
              options = metrics_max[:-1],
              value = metrics_max[0]["value"],
              multi = False
              ),
            ],
            style={'marginBottom':'4%','font-size': '1.2rem'}
            ),
          dcc.Graph(
            id="top_10_dep",
            figure=make_fig_3(df_dep, metrics_max[0]["value"], "dependence",0),
            config=conf
            )
          ],
          style={'background-color':boxcolor,'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','padding':'1%', 'marginBottom':'2%'},
          className="four columns flex-display"
          )
        ],
        className='row'
        ),
      ],
      className='six columns flex-display'
      ),
    html.Div([#right six columns
      html.Div([#headers
        html.H5("By country, as of 2017", style={"color": titlecolor, "marginBottom": "2%"}),
        html.Div([
          dcc.Dropdown(
            id='country-select',
            options = countries,
            value = "World",
            multi = False
            ),
          ],
          style={"marginBottom": "2%"}
          ),
        ],
        className="row"
        ),
      html.Div([#row for top chart
        html.Div([
          dcc.Graph(
            id="trend-all",
            figure=make_fig_2("World"),
            config=conf
            )
          ],
          className="eight columns flex-display"
          ),
        html.Div([
          html.Ul([
            html.Li(id="li1", style={"font-size": "1.5rem"}),
            html.Li(id="li2", style={"font-size": "1.5rem"}),
            html.Li(id="li3", style={"font-size": "1.5rem"})
            ], 
            style={"list-style-position": "outside", "marginLeft":"10%", "vertical-align":"middle"},
            ),
          ],
          className='four columns flex-display',
          style={"paddingLeft":"0%","paddingRight":"2%","marginTop":"5%"}
          ),
        ],
        className='row flex-display',
        #style={"display": "flex"}
        ),
      html.Div([
        html.Hr()
        ]),
      html.Div([#right bottom row
        html.Div([
          dcc.Graph(
            id="trend-ren",
            figure=make_fig_2b("World"),
            config=conf
            )
          ], 
          className="eight columns flex-display",
          style={"margin": "auto"}
          ),
        html.Div([
            html.Ul([
              html.Li(id="li21", style={"font-size": "1.5rem"}),
              html.Li(id="li22", style={"font-size": "1.5rem"}),
              html.Li(id="li23", style={"font-size": "1.5rem"})
              ], 
              style={"list-style-position": "outside", "marginLeft":"10%", "vertical-align":"middle"},
              ),
            ],
            className='four columns flex-display',
            style={"paddingLeft":"0%","paddingRight":"2%","marginTop": "5%"}
            )
        ],
        className='row flex-display',
        #style={"display": "flex"}
        ),
      ],
      style={'background-color':boxcolor, 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','padding':'1%', 'marginBottom':'1%'},
      className='six columns flex-display'
      )
    ],
    style={'padding':'0', "marginBottom":"0"},
    className="row"
    ),
  html.Div([#footer
    html.A("Built by Anthony S N Maina", href='https://www.linkedin.com/in/anthonymaina/', target="_blank", style={'font-size': '1rem',"marginBottom": "0%"})
    ],
    className='row',
    style={ 'text-align':'center'}
    ),
    ], 
    style={'marginLeft':'1%','marginRight':'1%', "marginTop":"0", "paddingTop":"0"}),

],
style={'backgroundColor': background, 'margin':0}
)


################################################
#### APP CALLBACKS  ############################
################################################

@app.callback(
  Output('world_map', 'figure'),
  [Input('metric-select-ww', 'value')])
def update_chart(selection):
  if selection=='dominant':
    df=df_dom
    df=df.merge(df_dep, how="left", left_on=["country", "dominant_source"], right_on=["country", "label"])
    df["percent_dep"]=round(100*df["dependence"],0).astype("int")
    df.drop(df[df["dependence"]==0].index.values, inplace=True)
    df["text"]=df["country"]+"<br>"+df["dominant_source"]+ " ("+df["percent_dep"].astype("str")+"%"+" dependent"+")"
    fig = go.Figure(data=go.Choropleth(
        locations = df['iso'],
        z = df['score'],
        text = df['text'],
        hoverinfo= 'text',
        showscale = False,
        colorscale=[[0, colors["color"][3]], [0.5, colors["color"][2]], [1.0, colors["color"][1]]],
        marker_line_width=0.5,
        marker_line_color='white',
    ))
    fig.update_layout({"geo": {"projection_type": "natural earth", "lataxis_range": [-60,85]}})
    fig.update_layout(l_map)
  else:
    fig=make_fig_1(selection)
  return fig

#callback for top n abs
@app.callback(
  Output('top_10_abs', 'figure'),
  [Input('metric-select-abs', 'value')])
def update_chart(metric):
  fig= make_fig_3(master_elec, metric, "lastValue",1)
  fig.update_layout(xaxis_title= "billion kWh")
  return fig

@app.callback(
  Output('abs_title', 'children'),
  [Input('metric-select-abs', 'value')])
def update_title(metric):
  if metric=="Total Electricity net generation":
    title="Top 10 total (net) generation"
  else:
    title="Top 10 total, by power source"
  return title

@app.callback(
  Output('top_10_ren', 'figure'),
  [Input('metric-select-cap', 'value')])
def update_chart(metric):
  fig= make_fig_3(master_elec, metric, "kWh PP",0)
  fig.update_layout(xaxis_title= "thousand kWh PP")
  return fig

@app.callback(
  Output('capita_title', 'children'),
  [Input('metric-select-abs', 'value')])
def update_title(metric):
  if metric=="Total Electricity net generation":
    title="Top 10 total (net) generation"
  else:
    title="Top 10 per capita, by power source"
  return title

@app.callback(
  Output('top_10_dep', 'figure'),
  [Input('metric-select-dep', 'value')])
def update_chart(metric):
  fig= make_fig_3(df_dep, metric, "dependence",0)
  fig.update_layout(xaxis_title= "fraction of total generation")
  return fig

@app.callback(
  Output('trend-all', 'figure'),
  [Input('country-select', 'value')])
def update_chart(country):
  fig= make_fig_2(country)
  fig.update_layout(yaxis_title= "billion kWh")
  fig.update_layout(title="Total electricity generation: "+country)
  return fig

@app.callback(
  Output('trend-ren', 'figure'),
  [Input('country-select', 'value')])
def update_chart(country):
  fig= make_fig_2b(country)
  fig.update_layout(yaxis_title= "billion kWh")
  fig.update_layout(title="Renewables in electricity generation: "+country)
  return fig


@app.callback(
  Output('li1', 'children'),
  [Input('country-select', 'value')])
def update_chart(country):
  return "{} billion kWh (net) electricity generated in 2017.".format(f'{master_elec["lastValue"][master_elec["country"]==country][master_elec["label"]=="Total Electricity net generation"].values[0]:,}')

@app.callback(
  Output('li2', 'children'),
  [Input('country-select', 'value')])
def update_chart(country):
  if df_dom["dominant_source"][df_dom["country"]==country].values[0]=='Nuclear':
    statement="Nuclear power is the dominant power source for electricity generation."
  elif df_dom["dominant_source"][df_dom["country"]==country].values[0]=='Fossil fuels':
    statement= "Fossil fuels are the dominant power source for electricity generation."
  else:
    statement="Renewables are the dominant power source for electricity generation."
  return statement

@app.callback(
  Output('li3', 'children'),
  [Input('country-select', 'value')])
def update_chart(country):
  return "Renewables constitute {}% of the power base used for electricity generation.".format(round(100*df_dep["dependence"][df_dep["label"]=="Renewable"][df_dep["country"]==country].values[0],1))

@app.callback(
  Output('li21', 'children'),
  [Input('country-select', 'value')])
def update_chart(country):
  if df_dep["dependence"][df_dep["label"]=="Renewable"][df_dep["country"]==country].values[0]==0:
    statement="Zero renewables in electricity generation mix as of 2017."
  else:
    statement="{} billion kWh electricity generated from renewable sources.".format(f'{round(master_elec[master_elec["country"]==country][master_elec["label"]=="Renewable"]["lastValue"].values[0],2):,}')
  return statement

@app.callback(
  Output('li22', 'children'),
  [Input('country-select', 'value')])
def update_chart(country):
  if country=="World":
    statement="{} is the dominant renewable power source.".format(master_elec[master_elec["country"]==country][master_elec["label"].isin(ren)].sort_values(by="lastValue")["label"].iloc[-1])
  elif df_dep["dependence"][df_dep["label"]=="Renewable"][df_dep["country"]==country].values[0]==0:
    statement=""
  else:
    subset=master_elec[master_elec["label"]=="Renewable"]
    rank=int(subset.rank(method="max", ascending=False)["lastValue"].loc[subset[subset["country"]==country].index.values[0]]-1)
    statement="Ranked number {} globally for total quantity of renewable power generated.".format(rank)
  return statement

@app.callback(
  Output('li23', 'children'),
  [Input('country-select', 'value')])
def update_chart(country):
  if country=="World":
    statement="{} is the fastest growing renewable power source, followed by {}.".format(df_growth[df_growth["country"]==country].sort_values(by="growth")["label"].iloc[-1],df_growth[df_growth["country"]==country].sort_values(by="growth")["label"].iloc[-2])
  elif df_dep["dependence"][df_dep["label"]=="Renewable"][df_dep["country"]==country].values[0]==0:
    statement=""
  else:
    statement="{} is the dominant renewable power source.".format(df_dep[df_dep["country"]==country][df_dep["label"].isin(ren)].sort_values(by="dependence")["label"].iloc[-1])
  return statement


if __name__ == '__main__':
  app.run_server()