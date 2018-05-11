import pandas as pd
import numpy as np
import metapy
from ast import literal_eval


class Searcher:

    def __init__(self):
        self.movies = None
        self.filtered_movies = None
        self.searched_movies = None

    def read_file(self, file_name):
        self.movies = pd.read_csv(file_name, low_memory=False)

        self.movies['genres'] = self.movies['genres'].fillna('[]').apply(literal_eval).apply(
            lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
        vote_counts = self.movies[self.movies['vote_count'].notnull()]['vote_count'].astype('int')
        vote_averages = self.movies[self.movies['vote_average'].notnull()]['vote_average'].astype('int')
        C = vote_averages.mean()
        m = vote_counts.quantile(0.75)
        self.movies['year'] = pd.to_datetime(self.movies['release_date'], errors='coerce').apply(
            lambda x: str(x).split('-')[0] if x != np.nan else np.nan)
        self.filtered_movies = self.movies[(self.movies['vote_count'] >= m) & (self.movies['vote_count'].notnull()) &
                                      (self.movies['vote_average'].notnull())][
            ['id', 'title', 'year', 'vote_count', 'vote_average', 'genres']]
        self.filtered_movies['vote_count'] = self.filtered_movies['vote_count'].astype('int')
        self.filtered_movies['vote_average'] = self.filtered_movies['vote_average'].astype('int')

        def weighted_rating(x):
            v = x['vote_count']
            R = x['vote_average']
            return (v / (v + m) * R) + (m / (m + v) * C)

        self.filtered_movies['wr'] = self.filtered_movies.apply(weighted_rating, axis=1)

    def search(self, search_query):
        idx = metapy.index.make_inverted_index('config.toml')
        ranker = metapy.index.OkapiBM25()
        query = metapy.index.Document()
        query.content(search_query)
        results = ranker.score(idx, query, 100)
        if len(results) == 0:
            print("Sorry, no movies found. Please try another query.\n")
            return False
        pd.options.mode.chained_assignment = None
        for num, result in enumerate(results):
            row = self.filtered_movies[self.filtered_movies['id'] == str(idx.metadata(result[0]).get("id"))]
            row['score'] = result[1]
            # row.loc[:, 'score'] = result[1]
            if num == 0:
                self.searched_movies = row
            else:
                self.searched_movies = pd.concat([self.searched_movies, row], ignore_index=True)
        return True
        # def comprehensive_score(movies):
        #     w = movies['wr']
        #     s = movies['score']
        #     return 5 * w * s / (4 * w + s)
        # self.searched_movies['cs'] = self.searched_movies.apply(comprehensive_score, axis=1)
        # self.searched_movies = self.searched_movies.sort_values('cs', ascending=False)

    def simple_rank(self):
        print("Hello, you are using the simple ranker.")
        self.searched_movies = self.searched_movies.sort_values('score', ascending=False)
        self.show_results()

    def rank_by_relevance(self):
        print("Hello, you are ranking by relevance.")

        def comprehensive_score(movies):
            w = movies['wr']
            s = movies['score']
            return 5 * w * s / (4 * w + s)

        self.searched_movies['cs'] = self.searched_movies.apply(comprehensive_score, axis=1)
        self.searched_movies = self.searched_movies.sort_values('cs', ascending=False)
        self.show_results()

    def rank_by_rates(self):
        print("Hello, you are ranking by rates.")

        def comprehensive_score(movies):
            w = movies['wr']
            s = movies['score']
            return 5 * w * s / (4 * s + w)

        self.searched_movies['cs'] = self.searched_movies.apply(comprehensive_score, axis=1)
        self.searched_movies = self.searched_movies.sort_values('cs', ascending=False)
        self.show_results()

    def show_results(self):
        print("Please try to remember the ids of the movies you like, which could be used in the recommender.\n")
        print(self.searched_movies[['id','title', 'year', 'genres']].head(20).to_string(index=False))
        print('\n')
        self.searched_movies = None

