file=data/ratings.csv
dir=data/

# set up
if [ -d "$dir" ]; then
  echo "data dir exists"
else
  mkdir data/
fi

if [ -f "$file" ]; then
  echo "$file  exists"
  rm -rf data/ratings.csv
  echo "deleted current version of the data/ratings.csv"
fi

# scrape the ratings dataset
cd match_predict_crawler
scrapy crawl fifa_ratings -o ../data/ratings.csv
echo "FIFA ratings (FIFA20 - FIFA06) has been scraped and saved in data/ratings.csv"

