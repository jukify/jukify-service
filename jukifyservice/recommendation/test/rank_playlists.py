import argparse
import logging
import pandas

def calculate_playlist_rank(input):
  data = pandas.read_table(input,
                           usecols=[0, 1],
                           names=['music', 'score'])
  mean_score = data['score'].mean()
  print("Score for %s: %s%%" %(input, mean_score * 100))

def calculate_ranks(groups_input):
  groups = pandas.read_table(groups_input, names=['groupname', 'user'], usecols=[0, 1])
  listed_groups = groups.groupby('groupname')['user'].apply(list)
  for group in list(listed_groups.index):
    playlist_input = "%s-recommendations.tsv" % group
    calculate_playlist_rank(playlist_input)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates similar musics"
                                     " or generates personalized recommendations for each user",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--groups_input', type=str,
                        help='groups to be ranked', required=True)
              
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    calculate_ranks(args.groups_input)