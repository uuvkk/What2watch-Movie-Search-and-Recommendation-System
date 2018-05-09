# What2watch-Movie-Search-and-Recommendation-System
[Jiazheng Li](https://github.com/uuvkk) (jl46), [Keren Wang](URL) (wkeren2) and [Yunwen Zhu](URL) (yunwenz2)

## Dataset
Open source data from Kaggle, you can download the dataset [here](https://www.kaggle.com/rounakbanik/the-movies-dataset). It contains information like title, year, description, producer and actors of more than 45,000 movies, and 26 million ratings from 270,000 users for the 45,000 movies. 

## Libraries and Techniques Used in thie Project
MeTApy for searching and ranking, text mining

Pandas for processing the data files

PyQt5 for creating GUI for users

## Main Classes and Functions
### Dat File Creator
To use MeTApy library, we must use MeTA-readable file: dat file. We write our own creators to create dat file from our dataset. We also create metadata file for further searching purposes.
```python
def dat_creator(iter_data, path):
    f = open(path, 'w')
    for item in iter_data:
        f.write(str(item))
        f.write('\n')
    f.close()
```
