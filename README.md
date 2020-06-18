This repository is created for the development of a football result predictor using FIFA Football Ratings and Machine Learning. 

The project is inspired by this Medium Article https://towardsdatascience.com/predicting-premier-league-odds-from-ea-player-bfdb52597392 where the gambling odds of a football match is predicted using the FIFA overall ratings of the starting eleven of both teams. This version of the project will be used to determine whether the match will end in a Win or Loss for the HOME team or end in a draw, some other small features will also be added to the project.

The initial (first part) of the final dataset used to complete this project involves obtaining the last 16 years of FIFA ratings from fifaindex.com for all players in te first and second division of Europe's top five leagues and the Erdevise, this was achieved using scrapy and produced a dataset that contains around 97,000 rows of player data

Each row of data includes the following data; player name, overall, potential, nationality, position, league and position group.

A data analysis is carried out on the FIFA ratings data set produced and can be found in the notebooks folder.

The FIFA ratings dataset can be obtained locally by cloning this repository and running the following command python create-dataset.py --data ratings

More details will be added to this README as more of the project is being completed. The aim of this project is for it to be an independent end to end Machine Learning project, encompasing all aspcets of machine learning. from data gathering, feature selection, feature engineering, model selection, experimentation all the way to some sort of deployment or the creation of some sort of API from the final model regardless of its accuracy. 
