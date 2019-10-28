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
import numpy as np
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
  return dt.datetime.fromtimestamp(utime/1000.)

def convert_pdTime(utime, tz='US/Eastern'):
  """ converts unix timestamp to pd.Timestamp format"""
  return pd.Timestamp(utime/1000., unit='s', tz=tz)

def specific_person_ts_count(in_df, p_name, send_rec='sender'):
  """ get either send or recieved count as times series """
  in_df = in_df[(in_df[send_rec] == p_name)]
  in_df['Date'] = pd.to_datetime(in_df.time.apply(convert_pdTime)) - pd.to_timedelta(7, unit='d')
  return in_df.groupby(pd.Grouper(key='Date', freq='W-MON'))
  #return grp[send_rec].count().reset_index().sort_values('Date')

def u_pickle_origin_csv(inputfile='./enron-event-history-all.csv',
                        pkl_file=r"./email_df.pkl"):
  """
  Grabs either pickled csv or processes a new one & picke/return it
  """
  exists = os.path.isfile(pkl_file)
  if exists:
    with open(pkl_file, 'rb') as fp:
      email_df = pickle.load(fp)
  else:
    print("Pkl FileNotFound - so the text will be processed. This may take time")
    # grabs input file & turn it into pandas df
    tqdm.pandas(desc="email load progress bar")
    email_df = read_input_csv(inputfile)
    # save this file for graph processing
    with open(pkl_file, "wb") as fw:
      pickle.dump(email_df, fw)
  df = pd.DataFrame(list(it.chain.from_iterable(email_df.send_rec_pair)), \
                    columns=['time', 'sender', 'recipient'])
  df['date'] = df.time.apply(convert_datetime)
  return df

# grab pickled csv or process csv
merged_df = u_pickle_origin_csv()

# find unique persons & one can restrict people here: currently set to 12
N_PEOPLE = 12
top_persons = merged_df.sender.value_counts()[:N_PEOPLE].index.tolist()

# setting up times range & init values
beg_date = convert_datetime(merged_df.time.min())
end_date = convert_datetime(merged_df.time.max())

# Let's just process one person to put into lower 2nd graph
person_0 = top_persons[0]
email_side = 'sender'
ts_grp = specific_person_ts_count(merged_df, person_0, email_side)
ts_df = ts_grp.agg({'sender': 'count', 'recipient': pd.Series.nunique}).reset_index().sort_values('Date')
ts_df.columns = ['Date', 'sent_freq', 'uniq_recv']

# time slices by restricting merged_df[merged_df.time <= utime]
out_df = u_sorted_out_df(
  combined_list_count(merged_df[(merged_df.date >= beg_date) \
                              & (merged_df.date <= end_date)],\
                                 top_persons), sort=False)
values_x = top_persons
values_y = {'sends': out_df.sent, 'recieved': out_df.recieved}
values_y = pd.DataFrame(values_y)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
  children=[
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
                             mode='markers',
                             marker=dict(size=[20] * len(values_x))
                            )],
        'layout': go.Layout(title="Scatter Plot of {} {} {}".format('sends',
                                                                    beg_date,
                                                                    end_date),
                            xaxis={'title': 'Names'},
                            yaxis={'title': 'Freq of {}'.format('sends')},)
      }
    ),

    dcc.Graph(
      id='bar',
      figure={
        'data':  [go.Bar(name='FreqSent', x=ts_df.Date, y=ts_df.sent_freq,),
                  go.Bar(name='UniqSendrs', x=ts_df.Date, y=ts_df.uniq_recv,), ],
        'layout': go.Layout(title="Scatter Plot: {} of {}".format('sends', top_persons[0]),
                            xaxis={'title': top_persons[0]},
                            yaxis={'title': 'Freq of {}'.format('sends')},),
      },
    ),
  ], style={'rowCount':2}
)


@app.callback(
  [
    Output('scatter', 'figure'),
    Output('bar', 'figure')
  ],
  [
    Input('yaxis', 'value'),
    Input('year_slider', 'value'),
    Input('scatter', 'clickData')
  ]
)
def update_graphics(yaxis, year_range, clickData):
  """
  this function is called by app.callback to update the graph values
  1: if yaxis chages to either: sender / recieved
  2: if the date range changes by the RangeSlider
  """

  n_beg_date = dt.datetime(year_range[0], 1, 1)
  n_end_date = dt.datetime(year_range[1], 12, 31)
  n_out_df = u_sorted_out_df(combined_list_count(
    merged_df[(merged_df.date >= n_beg_date) & (merged_df.date <= n_end_date)],
    top_persons), sort=False)
  n_values_y = {'sends': n_out_df.sent,
                'recieved': n_out_df.recieved}
  n_values_y = pd.DataFrame(n_values_y)

  if clickData is not None:
    person_n = clickData['points'][0]['x']
    print(person_n)

    # Let's just process one person to put into lower 2nd graph
    eml_side = 'sender'
    grp = specific_person_ts_count(merged_df, person_n, eml_side)
    ts_df = grp.agg({'sender': 'count', 'recipient': pd.Series.nunique}).reset_index().sort_values('Date')
    ts_df.columns = ['Date', 'sent_freq', 'uniq_recv']

  return [{
    'data':[go.Scatter(x=values_x,
                       y=n_values_y[yaxis],
                       mode='markers',
                       marker=dict(
                         size=[25] * len(values_x)
                       )
                      )],
    'layout': go.Layout(title="Scatter Plot of {} {} {}".format(yaxis,
                                                                n_beg_date,
                                                                n_end_date),
                        xaxis={'title':  'Names'},
                        yaxis={'title':  'Freq of {}'.format(yaxis)},)},
          {
            'data':  [go.Bar(name='FreqSent', x=ts_df.Date, y=ts_df.sent_freq,),
                      go.Bar(name='UniqSendrs', x=ts_df.Date, y=ts_df.uniq_recv,), ],
            'layout': go.Layout(title="Scatter Plot: {} of {}".format('sends',
                                                                      person_n,),
                                xaxis={'title': person_n},
                                yaxis={'title': 'Freq {}'.format(yaxis)},),},
  ]


if __name__ == '__main__':
  app.run_server(debug=True)
