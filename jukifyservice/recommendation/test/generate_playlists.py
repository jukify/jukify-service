import argparse
import logging
import pandas
import json
import requests

JUKIFY_SERVICE_URL = 'http://api.jukify.us'

def create_playlist(playlist_input, group_id, user_id):
  data = pandas.read_table(playlist_input, usecols=[0], names=['music'])
  tracks = list(data['music'])
  body = json.dumps({ 'user_id': user_id, 'tracks': tracks })
  endpoint = JUKIFY_SERVICE_URL + "/group/%s/playlist" % group_id
  headers = { 'Content-Type': 'application/json' }
  requests.post(endpoint, data=body) 

def create_playlists(groups_input, user_id='fmachado091'):
  groups = pandas.read_table(groups_input, names=['groupname', 'user'], usecols=[0, 1])
  listed_groups = groups.groupby('groupname')['user'].apply(list)
  for group in list(listed_groups.index):
    playlist_input = "%s-recommendations.tsv" % group
    create_playlist(playlist_input, group, user_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creates playlists given input files",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--groups_input', type=str,
                        help='groups for the playlists', required=True)

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    create_playlists(args.groups_input)