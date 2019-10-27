# -*- coding: utf-8 -*-
"""
Used plenty of plotly but ...
This is my 1st attempt at using Dash
Creates Interactive Scatter plot based Enron email data
"""
import os
import pickle
import datetime as dt
import itertools as it
import pandas as pd
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from tqdm import tqdm
from summarize_enron import (combined_list_count,
                             u_sorted_out_df,
                             read_input_csv)

def convert_datetime(utime):
  """ converts unix timestamp to datetime format"""
  return dt.datetime.fromtimestamp(utime/1000.).date()


pkl_file = r"./email_df.pkl"
exists = os.path.isfile(pkl_file)
if exists:
  with open(pkl_file, 'rb') as fp:
    email_df = pickle.load(fp)
else:
  print("Pkl FileNotFound - so the text will be processed. This may take time")
  # grabs input file & turn it into pandas df
  inputfile = './enron-event-history-all.csv'
  tqdm.pandas(desc="email load progress bar")
  email_df = read_input_csv(inputfile)
  # save this file for graph processing
  with open(pkl_file, "wb") as fw:
    pickle.dump(email_df, fw)

merged_df = pd.DataFrame(list(it.chain.from_iterable(email_df.send_rec_pair)),
                         columns=['time', 'sender', 'recipient'])

merged_df['date'] = merged_df.time.apply(convert_datetime)
# find unique persons & one can restrict people here
top_persons = merged_df.sender.value_counts()[:12].index.tolist()

# setting up times range & init values
min_date = convert_datetime(merged_df.time.min())
max_date = convert_datetime(merged_df.time.max())
beg_date = min_date
end_date = max_date

# time slices by restricting merged_df[merged_df.time <= utime]
out_df = u_sorted_out_df(
  combined_list_count(merged_df[(merged_df.date >= beg_date) \
                                & (merged_df.date <= end_date)],\
                                top_persons), sort=False)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

values_x = top_persons
values_y = {'sends': out_df.sent,
            'recieved': out_df.recieved}
values_y = pd.DataFrame(values_y)

app.layout = html.Div(children=[
  html.H1(children='Enron email Frequency in Dash'),
  html.Div(children='''Top 12 people w/  Slider for Dates & TimeSeries. '''),
  # Here's Interactive dropdown
  html.Label('Dropdown'),
  dcc.Dropdown(
    id='yaxis',
    options=[
      {'label': 'send Frequency', 'value': 'sends'},
      {'label': 'Recieved Frequency', 'value': 'recieved'},
    ],
    value='sends'
  ),

  html.Label("Dates emailed from 1998-05 to {}".format(end_date), id='time-range-label'),
    dcc.RangeSlider(
      id='year_slider',
      min=1998,
      max=2002,
      value=[1998, 2002],
    ),

  dcc.Graph(
    id='scatter',
    figure={
      'data':  [go.Scatter(x=values_x, \
                           y=values_y['sends'], \
                           mode='markers')],

      'layout': go.Layout(title="Scatter Plot of {} {} {}".format('sends',
                                                                  beg_date,
                                                                  end_date),
                          xaxis={'title':  'Names'},
                          yaxis={'title':  'Freq of {}'.format('sends')},)
        })])

@app.callback(
  output=Output('scatter', 'figure'),
  inputs=[
    Input('yaxis', 'value'),
    Input('year_slider', 'value'),
  ]
)

def update_graphics(yaxis, year_range):
  """
  this function is called by app.callback to update the graph values
  1: if yaxis chages to either: sender / recieved
  2: if the date range changes by the RangeSlider
  """
  end_date = dt.datetime(year_range[1], 12, 31).date()
  out_df = u_sorted_out_df(combined_list_count(merged_df[(merged_df.date >= beg_date)
                                                         & (merged_df.date <= end_date)],
                                               top_persons), sort=False)
  values_y = {'sends': out_df.sent,
              'recieved': out_df.recieved}
  values_y = pd.DataFrame(values_y)
  return {
    # [yaxis]
    'data':[go.Scatter(x=values_x,
                       y=values_y[yaxis],
                       mode='markers',)],
    'layout': go.Layout(title="Scatter Plot of {} {} {}".format(yaxis,
                                                                beg_date,
                                                                end_date),
                        xaxis={'title':  'Names'},
                        yaxis={'title':  'Freq of {}'.format(yaxis)},)
  }

if __name__ == '__main__':
  app.run_server(debug=True)
