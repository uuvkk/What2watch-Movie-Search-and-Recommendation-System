# What2watch-Movie-Search-and-Recommendation-System
[Jiazheng Li](https://github.com/uuvkk) (jl46), School of Information Sciences, University of Illinois Urbana-Champaign

[Keren Wang](URL) (wkeren2), College of Liberal Arts & Science, University of Illinois Urbana-Champaign

[Yunwen Zhu](URL) (yunwenz2), College of Liberal Arts & Science, University of Illinois Urbana-Champaign

> To execute, download the [data files](https://www.kaggle.com/rounakbanik/the-movies-dataset) into "data" folder, and then run run_me.py.

## Dataset
Open source data from Kaggle, you can download the dataset [here](https://www.kaggle.com/rounakbanik/the-movies-dataset). It contains information like title, year, description, producer and actors of more than 45,000 movies, and 26 million ratings from 270,000 users for the 45,000 movies. 

## Libraries and Techniques Used in thie Project
MeTApy for searching and ranking, text mining

Pandas for processing the data files

## Main Classes and Functions
### Dat File Creator
To use MeTApy library, we must use MeTA-readable file: dat file. I write my own creator to create dat file from the dataset. The file would be as the documents to creat index and conduct further searching by MeTA. 
```python
def dat_creator(iter_data, path):
    f = open(path, 'w')
    for item in iter_data:
        f.write(str(item))
        f.write('\n')
    f.close()
```
I also create metadata file for further searching purposes, more information about the corpus could be stored in the metadata file. After getting search results from MeTA rankers, we would be able to extract more information from the metadata file.
```python
def metadata_creator(iter_data_columns, path):
    f = open(path, 'w')
    for row_num in range(len(iter_data_columns[0])):
        row = ''
        for column in iter_data_columns:
            row += str(column[row_num])
            row += '\t'
        f.write(row)
        f.write('\n')
    f.close()
```
### Searcher
After generating MeTApy-readable dat files, I also create the line.toml because each line in the dat file is regarded as a corpus, and include the files in config.toml file, which will be loaded in the searcher. I use unigram model and the default filter chain.
```
prefix = '.'
stop-words = "stopwords.txt"
dataset = "movies_titles"
corpus = "line.toml"
index = "titles-idx"

[[analyzers]]
method = "ngram-word"
ngram = 1
filter = "default-unigram-chain"
```
#### Simple Search
In the search part, I only use the titles of the movies as the corpus. So each title is regarded as a document in the model. I use BM25 ranker in MeTA using default parameters, to rank the search result. In the simple search, I only consider the score given by the ranker, i.e. the more similar the title of a movie to the query, the higher rank it has. However, sometimes the ranker just give us some movies that are not popular at all, and we do not even know where to watch this movies.

#### IMDB Ranking
To solve the problem of retrieving unknown movies. I introduce the IMDB ranking function, to measure the rate of movie. I will filter the movies with very small numbers of votes because they are so unknown that only a few of people have watched them. I use some code from the [project](https://www.kaggle.com/rounakbanik/movie-recommender-systems) finished by [Rounak Banik](https://www.kaggle.com/rounakbanik) as a reference in my project, including the parts of extracting the genres of movies and calculating the IMDB score for a movie. The definition of [IMDB ranking](https://en.wikipedia.org/wiki/IMDb#Rankings) is as following:
<div><img src="images/imdb_ranking.jpeg" height="200"/></div>
The parameter settings are used for finding the top 250 movies. In my project, I want to filter more than 30,000 movies and leave those worth watching. I set the threshold as 50: the movies with at least 50 votes are left for further searching and recommendation. And we would have about 25% of the 45,000 movies left. I then add the weighted rates calculated to each row of movies for further ranking with the scores given by the MeTA rankers.

#### F-measure Based Comprehensive Score for Search Results
Now, we have two metrics to measure a movie retrieving result: BM25 ranking score and the IMDB weighted rate. I want to create a comprehensive measure for searching results. Here I introduce the concept of F-measure used in evaluating searching rankers, combing the two ranking metrics.

<a href="https://www.codecogs.com/eqnedit.php?latex=cs&space;(ComprehensiveScore)&space;=&space;\frac{(1&space;&plus;&space;\beta&space;^{2})&space;\times&space;(score&space;\times&space;wr)}{\beta&space;^{2}&space;\times&space;score&space;&plus;&space;wr&space;}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?cs&space;(ComprehensiveScore)&space;=&space;\frac{(1&space;&plus;&space;\beta&space;^{2})&space;\times&space;(score&space;\times&space;wr)}{\beta&space;^{2}&space;\times&space;score&space;&plus;&space;wr&space;}" title="cs (ComprehensiveScore) = \frac{(1 + \beta ^{2}) \times (score \times wr)}{\beta ^{2} \times score + wr }" /></a>

where *score* is the ranking score calculated by MeTA rankers, and *wr* is the IMDB weighted rate explained in the previous part, and *β* is a parameter to adjust the tradeoff between the two metrics.

#### Rank by Relevance
If you think the relevance of result to your query is more important, use the "rank by relevance" searcher, where the *β* parameter is set as 0.5, which means the importance of searching score is twice as the importance of IMDB weighted rate. And this searcher would give you the ranking emphasizing more on relevance.

#### Rank by Rates
If you think the popularity and overall rate of a movie is more important, use the "rank by rates" searcher, where the *β* parameter is set as 2, which means the importance of IMDB weighted rate is twice as the importance of searching score. And this searcher would give you the ranking emphasizing more on overall rate.

### Recommender
In my recommender part, instead of using lines in a file as corpus, I use files in a folder as corpus. This is because when processing some long documents, there may be some carriage returns in a corpus. Using lines as corpus may cause errors. In setting the file.toml file, I use the ids of movies as their classes. So the ranker will directly give me the ids of retrieved movies without needing metadata file. However I still put the ids and titles information in metadata file for convenience. The setting of file.toml is as followings.
```
type = "file-corpus"
list = "descriptions"
metadata = [{name = "id", type = "string"}, {name = "title", type = "string"}]
```
#### Courpus File and Class List File Creator
Initially I do not have the corpus files. I write my own file creator to extract the sigle files as corpus from a massive csv file. In this process, I also finish the class list file for MeTA to recognize classes for corpus.
```python
def files_creator(iter_names, iter_files, path):
    f = open(path + 'descriptions-full-corpus.txt','w')
    for row_num in range(len(iter_names)):
        name_id = iter_names[row_num]
        row = name_id + ' ' + name_id + '.txt'
        f.write(row)
        f.write('\n')
        corpus_f = open(path + name_id + '.txt', 'w')
        corpus_f.write(iter_files[row_num])
        corpus_f.close()
    f.close()
```

#### Content Based Recommendation
In my recommender, I use the descriptions of movies to find similar movie to recommend. Actually, this is still a process of information retrieval, where I use the descriptions of the movies that a user likes as the query. From the searching part, a user can get the ids of movies that he likes from search results. In the recommendation part, the system could get the descriptions of the movies to compose a query given to the recommender. And the recommender could use the generated inverted index by MeTA to find similar movies based on descriptions. The ranker used here is still BM25 with default parameters.

From the specific dataset used in this project, I use the combination of the overview and tagline of a movie as its description. For those movies without any overview nor tagline from the dataset, I simply use its title as its decription.

#### Comprehensive Recommendation Ranking
To improve the ranking of recommendation results, I also introduce the F-measure discussed in the previous parts. The *β* parameter is set as 1: relevance and rate are the same important. And when the query is very long, BM25 tend to give you higher ranking scores. At this time relevance would count more.
