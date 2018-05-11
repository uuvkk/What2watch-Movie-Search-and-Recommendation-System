from searcher import Searcher
from recommender import Recommender
from DatCreator import *


class What2watch:

    def __init__(self):
        print("Hello, welcome to use What2watch movie search and recommendation system.\n")
        print("Next, please select you want to use the search engine or the recommender.\n")
        self.searcher = Searcher()
        self.recommender = Recommender()

    def use_searcher(self):
        print("Welcome to use the searcher, the search results will be based on movie titles and popularity.\n")
        print("Loading files...\n")
        self.searcher.read_file('data/movies_metadata.csv')
        dat_creator(self.searcher.filtered_movies['title'], 'movies_titles/movies_titles.dat')
        metadata_creator([self.searcher.filtered_movies['id'].tolist(), self.searcher.filtered_movies['title'].tolist()],
                         'movies_titles/metadata.dat')
        while True:
            print('Now, please input your query, then press Enter.')
            print('''If you want to quit, please input "_quit". Any other inputs would all be regarded as queries.\n''')
            query = input("Your query: ")
            if query == '_quit':
                break
            if not self.searcher.search(query):
                continue
            print('Search finished! We have three methods of ranking results. How would you like your results shown?')

            def select_rank_method():
                while True:
                    print('You can enter number 1, 2, or 3.')
                    print('Entering 1, the results will be shown simply based on ranker scores.')
                    print('Entering 2, the results will be ranked more by relevance.')
                    print('Entering 3, the results will be ranked more by rates.')
                    print('''You could also input "_quit" to quit the searcher''')
                    rank_method = input('Your instruction: ')
                    if rank_method in ['1', '2', '3', "_quit"]:
                        return rank_method;
                    else:
                        print('Your input is not 1, 2, or 3. Please try again')

            rank_method = select_rank_method()
            if rank_method == '_quit':
                break;
            elif rank_method == '1':
                self.searcher.simple_rank()
            elif rank_method == '2':
                self.searcher.rank_by_relevance()
            else:
                self.searcher.rank_by_rates()

    def use_recommender(self):
        print("Welcome to use the recommender, the recommendation results will be based on movie description.\n")
        print("Loading files...\n")
        self.recommender.read_file('data/movies_metadata.csv')
        metadata_creator([self.recommender.filtered_movies['id'].tolist(), self.recommender.filtered_movies['description'].tolist()],
                         'movies_descriptions/metadata.dat')
        files_creator(self.recommender.filtered_movies['id'].tolist(), self.recommender.filtered_movies['description'].tolist(),
                      'movies_descriptions/')
        while True:
            print('Now, please input the ids for the movies you like, separated by spaces, then press Enter.\n')
            print('If you do not know the ids of the movies that interest you, you can use the searcher to find them.\n')
            print('''If you want to quit the recommender, please input "_quit".\n''')
            ids = input("Ths ids of movies: ").split()
            if ids == ['_quit']:
                    break
            try:
                showed_ids = [int(movie_id) for movie_id in ids]
            except ValueError:
                print("\nWrong input format, please try again and make sure to input ids.\n")
                continue
            print('You typed movie ids: ' + str(showed_ids) + '.')
            try:
                results_found = self.recommender.recommend(ids)
            except KeyError:
                print("\nSomething is wrong with you input, or some movie id does not exist, please try again.\n")
                continue
            if not results_found:
                continue
            else:
                print('Recommendation finished!\n')
                self.recommender.show_results()

    def entrance(self):
        while True:
            print('If you want to use the searcher, enter 1. If you want to use the recommender, enter 2.')
            print('''If you want to quit, please input "_quit".\n''')

            def select():
                while True:
                    instruction = input('Your instruction: ')
                    if instruction in ['1', '2', "_quit"]:
                        return instruction;
                    else:
                        print('Your input is not 1 or 2. Please try again')

            instruction = select()
            if instruction == '_quit':
                break;
            elif instruction == '1':
                self.use_searcher()
            else:
                self.use_recommender()
