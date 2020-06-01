# Spider for scraping players per team
# first and second division + erdevise Fifa 20 - Fifa 05
import scrapy


class FifaRatingsCrawler(scrapy.Spider):
    name = "fifa_ratings"
    fifa_index = "https://www.fifaindex.com/teams/fifa"
    leagues_specific = "/?league=10&league=13&league=14&league=16&league=17&league=19&league=20&league=31&league=32&league=53&league=54&order=desc"
    fifa_version_to_year_dict = {
        '20': '2019/2020',
        '19': '2018/2019',
        '18': '2017/2018',
        '17': '2016/2017',
        '16': '2015/2017',
        '15': '2014/2015',
        '14': '2013/2014',
        '13': '2012/2013',
        '12': '2011/2012',
        '11': '2010/2011',
        '10': '2009/2010',
        '09': '2008/2009',
        '08': '2007/2008',
        '07': '2006/2007',
        '06': '2005/2006',
        '05': '2004/2005',
    }
    player_id = 0
    main_league_dict = None

    def get_team_links(self):
        team_page_urls = []
        list_of_fifas = []
        for fifa in range(20, 4, -1):
            if fifa/10 >= 1:
                team_page_urls.append(self.fifa_index + str(fifa) + self.leagues_specific)
                list_of_fifas.append(str(fifa))
            else:
                team_page_urls.append(self.fifa_index + '0' + str(fifa) + self.leagues_specific)
                list_of_fifas.append('0' + str(fifa))
        return team_page_urls, list_of_fifas

    # four possible position groupings: GK, DF, MD, FW
    # position grouping is used to determine where in the final position matrix the player goes
    def get_player_position_group(self, player_position):
        if player_position == 'GK':
            return player_position
        elif 'B' in player_position or player_position == 'SW':  # LWB, CB, RB, RWB and SW
            return 'DF'
        elif 'M' in player_position:  # CM, CDM, LCAM, LAM, RAM, CAM, LM, RM, LWM, RWM
            return 'MD'
        else:
            return 'FW'  # ST, CF, RS, LS

    def get_league_ids_dict(self, response):
        league_id_dict = {}
        options = response.css('select[id*=id_league] option')
        for option in options:
            league_id = option.css('::attr(value)').get().strip()
            league_name = option.css('::text').get().strip()
            league_id_dict[league_id] = league_name
        return league_id_dict

    # league names across the fifas may not match, but the id key always matches regardless of the game year
    def get_league_name_from_main_dict(self, current_league_dict, league_name):
        keys = list(current_league_dict.keys())
        values = list(current_league_dict.values())
        league_id_from_current_dict = keys[values.index(league_name)]
        return self.main_league_dict[league_id_from_current_dict]

    def start_requests(self):
        # number of years back from FIFA20 can be set here
        urls, fifa_version = self.get_team_links()
        for index, url in enumerate(urls):
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=dict(fifa_version=fifa_version[index]))

    def parse(self, response, fifa_version):
        # get all id for the leagues in the game -> allows league to be added to final data frame
        current_league_dict = self.get_league_ids_dict(response)
        if self.main_league_dict is None:
            # keep a global id to league name dict
            self.main_league_dict = current_league_dict

        self.log('the fifa version is {}'.format(fifa_version))
        team_rows = response.css('table.table-teams tbody tr td[data-title*=Name] a')
        yield from response.follow_all(team_rows, callback=self.parse_players, cb_kwargs=dict(fifa_version=fifa_version,
                                                                                              league_dict=current_league_dict))

        # parse to the next team page and recall this same function will only be a single instance of this button
        next_teams_page = response.css('li.ml-auto a::attr(href)').get()
        if next_teams_page is not None:
            yield response.follow(next_teams_page, callback=self.parse, cb_kwargs=dict(fifa_version=fifa_version))
        else:
            self.log('There Are No More Team Pages to Scrape')

    def parse_players(self, response, fifa_version, league_dict):
        season = self.fifa_version_to_year_dict[fifa_version]
        self.log('FIFA version: {} Football Season: {}'
                 .format(fifa_version, season))
        current_team = response.css('h1::text').get()
        current_team_league = response.css('div.pl-3 h2 a.link-league::text').get().strip()
        current_players_table = response.css('table.table-players')[0]  # current players table
        players = current_players_table.css('tbody tr')

        for player in players:
            self.player_id = self.player_id + 1
            player_name = player.css('td[data-title=Name] a::text').get()
            player_overall_potential = player.css('td[data-title*=OVR] span::text').getall()
            player_number = player.css('td[data-title*=Kit]::text').get()
            player_nationality = player.css('td[data-title*=Nationality] a::attr(title)').get()
            player_age = player.css('td[data-title*=Age]::text').get()
            player_position = player.css('td[data-title*=Position] span::text').get()
            # if player is not in the starting line-up take the first preferred position (clean dataset)
            if player_position == 'Sub' or player_position == 'Res':
                preferred_positions = player.css('td[data-title*=Preferred] a span::text').getall()
                player_position = preferred_positions[0]
            yield {
                'id': str(self.player_id),
                'name': player_name.strip(),
                'age': int(player_age.strip()),
                'position': player_position.strip(),
                'nationality': player_nationality.strip(),
                'overall': int(player_overall_potential[0].strip()),
                'potential': int(player_overall_potential[1].strip()),
                'number': int(player_number.strip()),
                'team': current_team.strip(),
                'league': self.get_league_name_from_main_dict(current_league_dict=league_dict,
                                                              league_name=current_team_league),
                'season': season.strip(),
                'position_group': self.get_player_position_group(player_position.strip()),
            }