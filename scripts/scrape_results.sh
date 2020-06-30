results_file=data/results.json
dir=data/

# set up
if [ -d "$dir" ]; then
  echo "data dir exists"
else
  mkdir data/
fi

if [ -f "$results_file" ]; then
  echo "$results_file  exists"
  rm -rf $results_file
  echo "deleted current version of the data/ratings.csv"
fi

# scrape the ratings dataset
cd match_predict_crawler
python FootballResultsCrawler.py
echo "The Match Results from the 2004/2005 have been collected and saved in data/results.json"