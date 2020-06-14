import requests as req
import json as js

from bs4 import BeautifulSoup as BS


class FootballResultCrawler:
    match_id = 0
    nations_of_interest = [
        'England',
        # 'Germany',
        # 'France',
        # 'Italy',
        # 'Spain',
        # 'Netherlands'
    ]
    league_seasons = [f"{year}/{year+1}" for year in range(2004, 2019)]
    json_file = '../data/results.json'
    # dict that will be written to the above file, will contain the desired results objects
    results_dict = {
        "matches": [

        ]
    }

    def __init__(self, home_url):
        self.home_url = home_url
        self.parse_home(home_url)
        self.write_to_json()
        print(f"Number of matches saved {len(self.results_dict['matches'])}")

    def get_parser(self, url):
        page = req.get(url)
        return BS(page.content, 'html.parser')

    def parse_home(self, home_url):
        """
            Get the URLs of the league home page of the nation/leagues of interest
        """
        home_page_parser = self.get_parser(home_url)
        nation_options = home_page_parser.find(id="top_menu_item_2").find(id="special_navi_body").find_all('a')
        nation_copy = self.nations_of_interest
        for nation in nation_options:
            # only get the nations of interest, no extra processing if not necessary
            if len(nation_copy) == 0:
                break
            current_nation = nation.text.strip()
            if current_nation in self.nations_of_interest:
                league_home_url = home_url + nation['href']
                self.parse_league_home_page(league_home_url)
                nation_copy.remove(current_nation)

    def get_second_divsion_href(self, parser):
        """
            Get the url to the second division page of a league using the parser
        """
        second_division_anchor = parser.find('div', {'class':'subnavi'})\
            .find('ul').find_all('li')[2].find('a')
        return second_division_anchor['href']

    def get_archive_links(self, parsers):
        """
            Takes in a list parsers for each league page
            Get the link to the archive page for a given list of leagues, returns a list of urls that contain the archive page url for each league
        """
        def get_href(parser):
            anchor = parser.find('div', {'class': 'sitenavi'}) \
                .find('div', {'class': 'navibox2'})\
                .find('div', {'class': 'data'}).find_all('ul')[1].find_all('li')[2].find('a')
            return anchor['href']

        return [self.home_url + get_href(parser) for parser in parsers]

    def parse_league_home_page(self, league_home_url):
        """
            Parse the league home page for the archive links
            The archive link contains the page that has all the links to the past results for each season of the league
        """
        print(f"Currently Crawling: {league_home_url}")
        league_home_page_parser = self.get_parser(league_home_url)
        second_division_url = self.home_url + self.get_second_divsion_href(league_home_page_parser)
        second_division_parser = self.get_parser(second_division_url)
        archive_urls = self.get_archive_links([league_home_page_parser, second_division_parser])
        for url in archive_urls:
            self.parse_archive_page(self.get_parser(url))

    def parse_archive_page(self, archive_parser):
        """
            :param archive_parser: parser of the archive page of a given league
            Parses an archive page to obtain and process the page that represents the results pages for each season of interest for the given league
        """
        season_rows = archive_parser.find('div', {'class': 'content'})\
            .find('div', {'class': 'portfolio'})\
            .find('div', {'class': 'box'})\
            .find('div', {'class': 'data'}).find('table').find_all('tr')
        season_rows.pop(0)  # remove the table headings row
        added_seasons = []
        for row in season_rows:
            # break when all the season are obtained so, there is no unnecessary processing
            if added_seasons == self.league_seasons:
                break
            row_data = row.find_all('td')
            season = row_data[0].find('b').text
            if season in self.league_seasons:
                season_href = row_data[2].find('a')['href']
                season_url = self.home_url + season_href
                added_seasons.append(season)
                self.parse_archive_results(self.get_parser(season_url), season)

    def parse_archive_results(self, archive_results_parser, season):
        """
            :param season: current season being parsed
            :param archive_results_parser: The parser for the results archive page
            Takes the parser for the archive page and obtains and processes the url for each fixture round for the league
        """
        league_round_options = archive_results_parser.find('div', {'class': 'portfolio'}).find_all('form')[1].find_all('option')
        for fixture_round in league_round_options:
            league_round_url = self.home_url + fixture_round['value']
            league_round_parser = self.get_parser(league_round_url)
            match_round = self.get_fixture_round_from_url(league_round_url)
            self.parse_fixture_page_from_results_page(league_round_parser, season, match_round)

    def get_fixture_round_from_url(self, url):
        url_elements = url.split('/')
        print(f"split elements {url_elements}")
        return url_elements[len(url_elements) - 2]

    def parse_fixture_page_from_results_page(self, league_round_parser, season, match_round):
        """
            :param match_round: The round the match is taking place in
            :param season: The current season being parsed
            :param league_round_parser: The league round parser for the fixture round page of the league
            Takes the fixture round page of the league history and obtains and processes the individual match page urls
        """
        fixture_rows = league_round_parser.find('div', {'class': 'box'}).find_all('tr')
        for row in fixture_rows:
            match_report = row.find_all('td')[5].find('a')
            match_report_url = self.home_url + match_report['href']
            match_report_parser = self.get_parser(match_report_url)
            self.parse_match_report(match_report_parser, season, match_round)

    def get_lineups(self, lineups):
        """
            :param lineups: list of table elements on page that represent the line up of the home and away team
            :return: returns two lists containing the starting eleven of the home and away team respectively
        """
        home_away_lineups = [[], []]
        for index, lineup in enumerate(lineups):
            players = lineup.find_all('tr')[0:11]
            for player in players:
                player_name = player.find_all('td')[1].find('a').text.strip()
                home_away_lineups[index].append(player_name)
        return home_away_lineups[0], home_away_lineups[1]

    def create_match_dict(self, home_team, away_team, home_score, away_score, home_lineup, away_lineup, league_round, league_name, season):
        """
            :param home_team: string representing the name of the home team of the match
            :param away_team: string representing the name of the away team of the match
            :param home_score: string representing the number of goals scored by the home team
            :param away_score: string representing the number of goals scored by the away team
            :param home_lineup: list of strings, of the starting eleven players of the home team
            :param away_lineup: list of strings, of the starting eleven players of the away team
            :param league_round: string that represents the league round the match takes place in
            :param league_name: string that represents the name of the league this match took place in
            :return: A dictionary that contains all the relevant match information that should be eventually stored as a dataset entry
        """

        if home_score > away_score:
            match_winner = home_team
            winner_category = "H"
        elif away_score > home_score:
            match_winner = away_team
            winner_category = "A"
        else:
            match_winner = "draw"
            winner_category = "D"
        self.match_id = self.match_id + 1
        
        return {
            "match_id": self.match_id,
            "league_round": league_round,
            "home_team": home_team,
            "away_team": away_team,
            "home_score": home_score,
            "away_score": away_score,
            "winner": match_winner,
            "winner_category": winner_category,
            "home_eleven": home_lineup,
            "away_eleven": away_lineup,
            "league": league_name,
            "season": season
        }

    def parse_match_report(self, match_report_parser, season, match_round):
        """
        :param match_report_parser: Parser for the match result page for a match in a round in specific league
        :param season: Current season of the match
        :param match_round: The round the match was played in that season
        Creates a JSON object that contains all the relevant information for a given match
        """
        current_league = match_report_parser.find('div', {'class': 'subnavi'}).find('a', {'class': "active"}).text
        score = match_report_parser.find('div', {'class': 'box'}).find('div', {'class': 'resultat'}).text.strip()
        teams_table = match_report_parser.find('div', {'class': 'box'}).find('div', {'class': 'data'}).find('table', {'class': 'standard_tabelle'}).find_all('th')
        lineups = match_report_parser.find('div', {'class': 'box'}).find('div', {'class': 'data'}).find_all('table')[2].find('tr').find_all('td', {'width': '50%'})
        home_lineup, away_lineup = self.get_lineups(lineups)
        home_team = teams_table[0].find('a').text
        away_team = teams_table[2].find('a').text
        scores = score.split(':')
        home_score = scores[0]
        away_score = scores[1]
        match_object = js.dumps(self.create_match_dict(home_team, away_team, home_score, away_score, home_lineup, away_lineup, match_round, current_league, season))
        print(f"Match: {match_object}")
        self.results_dict['matches'].append(match_object)

    def write_to_json(self):
        with open(self.json_file, 'w') as json_file:
            js.dump(self.results_dict, json_file, indent=4)
        print(f"The results data has been written to the location {self.json_file}")


if __name__ == '__main__':
    FootballResultCrawler('https://www.worldfootball.net')
