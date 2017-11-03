''' Largely base on example given in the implicit repo
'''

from __future__ import print_function

import argparse
import logging
import time

import numpy
import pandas
from scipy.sparse import coo_matrix

from implicit.als import AlternatingLeastSquares
from implicit.approximate_als import (AnnoyAlternatingLeastSquares, NMSLibAlternatingLeastSquares,
                                      FaissAlternatingLeastSquares)
from implicit.nearest_neighbours import (BM25Recommender, CosineRecommender,
                                         TFIDFRecommender, bm25_weight)


# maps command line model argument to class name
MODELS = {"als":  AlternatingLeastSquares,
          "nmslib_als": NMSLibAlternatingLeastSquares,
          "annoy_als": AnnoyAlternatingLeastSquares,
          "faiss_als": FaissAlternatingLeastSquares,
          "tfidf": TFIDFRecommender,
          "cosine": CosineRecommender,
          "bm25": BM25Recommender}


def get_model(model_name):
    model_class = MODELS.get(model_name)
    if not model_class:
        raise ValueError("Unknown Model '%s'" % model_name)

    # some default params
    if issubclass(model_class, AlternatingLeastSquares):
        params = {'factors': 50, 'dtype': numpy.float32}
    elif model_name == "bm25":
        params = {'K1': 100, 'B': 0.5}
    else:
        params = {}

    return model_class(**params)


def read_data(filename):
    """ Reads in the dataset, and returns a tuple of a pandas dataframe
    and a sparse matrix of music/user/playcount """
    # read in triples of user/music/playcount from the input dataset
    # get a model based off the input params
    start = time.time()
    logging.debug("reading data from %s", filename)
    data = pandas.read_table(filename,
                             usecols=[0, 2, 3],
                             names=['user', 'music', 'plays'],
                             na_filter=False)

    # map each music and user to a unique numeric value
    data['user'] = data['user'].astype("category")
    data['music'] = data['music'].astype("category")

    # create a sparse matrix of all the users/plays
    plays = coo_matrix((data['plays'].astype(numpy.float32),
                       (data['music'].cat.codes.copy(),
                        data['user'].cat.codes.copy())))

    logging.debug("read data file in %s", time.time() - start)
    return data, plays


def calculate_similar_musics(input_filename, output_filename, model_name="als"):
    """ generates a list of similar musics by utiliizing the 'similar_items'
    api of the models """
    df, plays = read_data(input_filename)

    # create a model from the input data
    model = get_model(model_name)

    # if we're training an ALS based model, weight input by bm25
    if issubclass(model.__class__, AlternatingLeastSquares):
        # lets weight these models by bm25weight.
        logging.debug("weighting matrix by bm25_weight")
        plays = bm25_weight(plays, K1=100, B=0.8)

        # also disable building approximate recommend index
        model.approximate_recommend = False

    logging.debug("training model %s", model_name)
    start = time.time()
    model.fit(plays)
    logging.debug("trained model '%s' in %0.2fs", model_name, time.time() - start)

    # write out similar musics by popularity
    musics = dict(enumerate(df['music'].cat.categories))
    start = time.time()
    logging.debug("calculating top musics")
    user_count = df.groupby('music').size()
    to_generate = sorted(list(musics), key=lambda x: -user_count[x])

    # write out as a TSV of musicid, othermusicid, score
    with open(output_filename, "w") as o:
        for musicid in to_generate:
            music = musics[musicid]
            for other, score in model.similar_items(musicid, 11):
                o.write("%s\t%s\t%s\n" % (music, musics[other], score))

    logging.debug("generated similar musics in %0.2fs",  time.time() - start)


def calculate_recommendations(input_filename, output_filename, model_name="als"):
    """ Generates music recommendations for each user in the dataset """
    # train the model based off input params
    df, plays = read_data(input_filename)

    # create a model from the input data
    model = get_model(model_name)

    # if we're training an ALS based model, weight input for by bm25
    if issubclass(model.__class__, AlternatingLeastSquares):
        # lets weight these models by bm25weight.
        logging.debug("weighting matrix by bm25_weight")
        plays = bm25_weight(plays, K1=100, B=0.8)

        # also disable building approximate recommend index
        model.approximate_similar_items = False

    logging.debug("training model %s", model_name)
    start = time.time()
    model.fit(plays)
    logging.debug("trained model '%s' in %0.2fs", model_name, time.time() - start)

    # generate recommendations for each user and write out to a file
    musics = dict(enumerate(df['music'].cat.categories))
    logging.debug("Generating recommendations")
    start = time.time()
    user_plays = plays.T.tocsr()
    with open(output_filename, "w") as o:
        for userid, username in enumerate(df['user'].cat.categories):
            for musicid, score in model.recommend(userid, user_plays):
                o.write("%s\t%s\t%s\n" % (username, musics[musicid], score))
    logging.debug("generated recommendations in %0.2fs",  time.time() - start)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates similar musics"
                                     " or generates personalized recommendations for each user",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input', type=str,
                        dest='inputfile', help='dataset file', required=True)
    parser.add_argument('--output', type=str, default='similar-musics.tsv',
                        dest='outputfile', help='output file name')
    parser.add_argument('--model', type=str, default='als',
                        dest='model', help='model to calculate (%s)' % "/".join(MODELS.keys()))
    parser.add_argument('--recommend',
                        help='Recommend items for each user rather than calculate similar_items',
                        action="store_true")
    parser.add_argument('--param', action='append',
                        help="Parameters to pass to the model, formatted as 'KEY=VALUE")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    if args.recommend:
        calculate_recommendations(args.inputfile, args.outputfile, model_name=args.model)
    else:
        calculate_similar_musics(args.inputfile, args.outputfile, model_name=args.model)