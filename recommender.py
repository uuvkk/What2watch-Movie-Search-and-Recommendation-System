import pandas as pd
import numpy as np
import metapy
from ast import literal_eval


class Recommender():

    def __init__(self):
        self.movies = None
        self.filtered_movies = None
        self.recommended_movies = None

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
            ['id', 'title', 'year', 'vote_count', 'vote_average', 'popularity', 'genres', 'overview', 'tagline']]
        self.filtered_movies['vote_count'] = self.filtered_movies['vote_count'].astype('int')
        self.filtered_movies['vote_average'] = self.filtered_movies['vote_average'].astype('int')

        def weighted_rating(x):
            v = x['vote_count']
            R = x['vote_average']
            return (v / (v + m) * R) + (m / (m + v) * C)

        self.filtered_movies['wr'] = self.filtered_movies.apply(weighted_rating, axis=1)
        self.filtered_movies['tagline'] = self.filtered_movies['tagline'].fillna('')
        self.filtered_movies['description'] = self.filtered_movies['overview'] + ' ' + self.filtered_movies['tagline']
        self.filtered_movies['description'] = self.filtered_movies['description'].fillna(self.filtered_movies['title'])

    def recommend(self, ids):
        ids = list([str(movie_id) for movie_id in ids])
        idx = metapy.index.make_inverted_index('config2.toml')
        ranker = metapy.index.OkapiBM25()
        query = metapy.index.Document()
        query.content(self.get_query(ids))
        results = ranker.score(idx, query, 100)
        if len(results) == 0:
            print("Sorry, no movies found. This is because all the ids you input don't exist. "
                  "Please check your input and try again.\n")
            return False
        pd.options.mode.chained_assignment = None
        for num, result in enumerate(results):
            if str(idx.metadata(result[0]).get("id")) in ids:
                continue
            row = self.filtered_movies[self.filtered_movies['id'] == str(idx.metadata(result[0]).get("id"))]
            row['score'] = result[1]
            if num == 0:
                self.recommended_movies = row
            else:
                self.recommended_movies = pd.concat([self.recommended_movies, row], ignore_index=True)
        return True

        def comprehensive_score(movies):
            w = movies['wr']
            s = movies['score']
            return 2 * w * s / (w + s)

        self.self.recommended_movies['cs'] = self.recommended_movies.apply(comprehensive_score, axis=1)
        self.recommended_movies = self.recommended_movies.sort_values('cs', ascending=False)

    def get_query(self, ids):
        recommend_query = ''
        for movie_id in ids:
            row = self.filtered_movies[self.filtered_movies['id'] == movie_id]
            if row.empty:
                continue
            recommend_query += row['description'].to_string(index = False)
        return recommend_query

    def show_results(self):
        print("The followings are recommendations for you. Hope you like them.\n")
        print(self.recommended_movies[['id', 'title', 'year', 'genres']].head(20).to_string(index=False))
        print('\n')
        self.recommended_movies = None
