import argparse
import logging
import time
import pandas

def read_rec_data(filename, users):
  """ Reads in the user recommendations, and a filtered pandas DataFrame """
  start = time.time()
  logging.debug("reading data from %s", filename)
  data = pandas.read_table(filename,
                           usecols=[0, 1, 2],
                           names=['user', 'music', 'score'])
  logging.debug("read data file in %s", time.time() - start)
  return data[data['user'].isin(users)]

def recommend_to_group(input, groupname, users, size):
  group_data = read_rec_data(input, users)
  avgs = group_data.groupby(['music'])['score'].mean()
  playlist = list(avgs.nlargest(15).index)
  output_filename = "%s-recommendations.tsv" % groupname
  with open(output_filename, "w") as o:
    for musicid in playlist:
        o.write("%s\t%s\n" % (musicid, avgs[musicid] * 1000))

def recommend_to_groups(groups_input, rec_input, size):
  groups = pandas.read_table(groups_input, names=['groupname', 'user'], usecols=[0, 1])
  listed_groups = groups.groupby('groupname')['user'].apply(list)
  for group in list(listed_groups.index):
    recommend_to_group(rec_input, group, listed_groups[group], size)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates a playlist recommended to a group of users",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--rec_input', type=str,
                        help='recommendations dataset file', required=True)
    parser.add_argument('--groups_input', type=str, default=10,
                        help="file with group information")
    parser.add_argument('--size', type=int, default=10,
                        help="size of playlist to be generated")
              

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    recommend_to_groups(args.groups_input, args.rec_input, args.size)