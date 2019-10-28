"""
import in_file_name from enron-event-history-all & grab in_column_names
to produce a sorted (by sent) csv file: person, sent, recieved
"""
import sys
import itertools as it
import time
import getopt
import pandas as pd
from tqdm import tqdm

def split_recipients(row, ):
  """ splits multiple recipients into pairs of list of
    [[sender & recipient], ..., [sender & recipient]] """
  return [[row.time, row.sender, recipient] for recipient in row.recipients.split('|')]

def read_input_csv(ifile):
  """ read in input_csv_file & return DataFrame. This usually would b inside
      main func, but repase of recipients is time consuming """
  in_column_names = ['time', 'msgId', 'sender', 'recipients'] #, 'topic', 'msg_mode']
  df = pd.read_csv(ifile, names=in_column_names, usecols=range(len(in_column_names)))
  # add column that contains list of recipients
  df = df.fillna("")
  tqdm.pandas(desc="email load progress bar")
  df['send_rec_pair'] = df.progress_apply(split_recipients, axis=1)
  return df

def uniques_persons_set(df):
  " find unique names by combining unique senders & recipients "
  unique_senders = df.sender.unique().tolist()
  unique_recipient = df.recipient.unique().tolist()
  return set(unique_senders + unique_recipient)

def sender_recipient_counts(name, sender_count_d, recipient_count_d):
  """ returns: name, sender_#, recipient_# """
  return name, sender_count_d.get(name, 0), recipient_count_d.get(name, 0)

def combined_list_count(df, unique_people):
  """ uses value_counts to get send & recipient count series 
      to get combined list_count"""
  sender_num_dict = df.sender.value_counts().to_dict()
  recipient_num_dict = df.recipient.value_counts().to_dict()
  return [sender_recipient_counts(name, sender_num_dict, recipient_num_dict) \
          for name in unique_people]

def u_sorted_out_df(list_counts, sort=True):
  """ return final either sorted/unsorted out DataFrame for this project """
  out_column_name = ['person', 'sent', 'recieved']
  df = pd.DataFrame(list_counts, columns=out_column_name)
  if sort:
    return df.sort_values(by='sent', ascending=False)
  return df

def main(argv):
  """
  Main run function to kick off conversion & turn outputfile
  inputfile, outputfile = './enron-event-history-all.csv', './enron-email-count.csv'
  """
  inputfile, outputfile = '', ''
  try:
    opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
  except getopt.GetoptError:
    print('python summarize_enron.py -i <inputfile> -o <outputfile>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('summarize_enron.py -i <inputfile> -o <outputfile>')
      sys.exit()
    elif opt in ("-i", "--ifile"):
      inputfile = arg
    elif opt in ("-o", "--ofile"):
      outputfile = arg
  print('Input file is "', inputfile)
  print('Output file is "', outputfile)

  # grabs input file & turn it into pandas df
  email_df = read_input_csv(inputfile)

  # merge the list into a flattened send_rec_pair in email_df
  merged_df = pd.DataFrame(list(
    it.chain.from_iterable(email_df.send_rec_pair)),
    columns=['time', 'sender', 'recipient'])

  # find unique persons & one can restrict people here
  unique_persons = uniques_persons_set(merged_df)
  # time slices by restricting merged_df[merged_df.time <= utime]
  list_counts = combined_list_count(merged_df, unique_persons)

  # convert to list to df, sort, & output to csv
  out_df = u_sorted_out_df(list_counts)
  out_df.to_csv(outputfile, index=False, sep='\t')

if __name__ == "__main__":
  main(sys.argv[1:])
