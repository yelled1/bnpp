import sys
import pandas as pd
import pandas.util.testing as pt
import numpy as np
import numpy.testing as npt
import itertools
import time
import pickle
import timeit
import hashlib 
import getopt
""" 
import in_file_name from enron-event-history-all & grab in_column_names 
to produce a sorted (by sent) csv file: person, sent, recieved 
"""
def read_input_csv(ifile):
  " read input_csv_file "
  in_column_names = ['time', 'msgId', 'sender', 'recipients'] #, 'topic', 'msg_mode']
  df = pd.read_csv(ifile, names=in_column_names, usecols=range(len(in_column_names)))
  return df.fillna("")

def split_recipients(row, ):
  "splits multiple recipients into pairs of list of [[sender & recipient], ...]"
  return [[row.time, row.sender, recipient] for recipient in row.recipients.split('|')]

def sender_recipient_counts(name, sender_count_d, recipient_count_d):
  """ returns: name, sender_#, recipient_# """
  return name, sender_count_d.get(name,0), recipient_count_d.get(name,0)


def main(argv):
  #inputfile, outputfile = './enron-event-history-all.csv', './enron-email-count.csv'
  inputfile, outputfile = '', ''
  try:
    opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
  except getopt.GetoptError:
    print('python summarize-enron.py -i <inputfile> -o <outputfile>')
    #python summarize-enron.py -i ./enron-event-history-all.csv -o ./enron-email-count.csv
    sys.exit(2)
  for opt, arg in opts: 
    if opt == '-h': 
      print('summarize-enron.py -i <inputfile> -o <outputfile>')
      sys.exit()
    elif opt in ("-i", "--ifile"):
      inputfile = arg
    elif opt in ("-o", "--ofile"):
      outputfile = arg 
  print('Input file is "', inputfile)
  print('Output file is "', outputfile)


  # grabs input file & turn it into pandas df
  email_df = read_input_csv(inputfile)
  # add column that contains list of recipients
  email_df['send_rec_pair'] = email_df.apply(split_recipients, axis=1)

  # merge the list into a flattened df
  merged_l = list(itertools.chain.from_iterable(email_df.send_rec_pair))
  merged_df = pd.DataFrame(merged_l, columns=['time', 'sender', 'recipient'])

  # find unique names by combining unique senders & recipients 
  unique_senders = merged_df.sender.unique().tolist()
  unique_recipient = merged_df.recipient.unique().tolist()
  uniques_names = set(unique_senders + unique_recipient)

  # use value_counts to get send & recipient count series to get 
  # combined list_count
  sender_num_dict = merged_df.sender.value_counts().to_dict()
  recipient_num_dict = merged_df.recipient.value_counts().to_dict()
  list_counts = [sender_recipient_counts(name,
                                         sender_num_dict,
                                         recipient_num_dict)
                 for name in uniques_names]

  # convert to list to df, sort, & output to csv
  out_column_name = ['person', 'sent', 'received']
  out_df = pd.DataFrame(list_counts, columns=out_column_name)
  out_df = out_df.sort_values(by='sent', ascending=False)
  out_df.to_csv(outputfile, index=False, sep='\t')

if __name__ == "__main__":
  main(sys.argv[1:])
