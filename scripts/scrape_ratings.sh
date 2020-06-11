ratings_file=data/ratings.csv
dir=data/

# set up
if [ -d "$dir" ]; then
  echo "data dir exists"
else
  mkdir data/
fi

if [ -f "$ratings_file" ]; then
  echo "$ratings_file  exists"
  rm -rf $ratings_file
  echo "deleted current version of the data/ratings.csv"
fi

# scrape the ratings dataset
cd match_predict_crawler
scrapy crawl fifa_ratings -o ../$ratings_file
echo "FIFA ratings (FIFA20 - FIFA06) has been scraped and saved in data/ratings.csv"

