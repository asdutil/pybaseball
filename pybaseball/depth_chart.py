from enum import Enum

import pandas as pd
from bs4 import BeautifulSoup

from . import cache
from .utils import most_recent_season, get_bref_id_from_player_link, ACTIVE_TEAMS_MAPPING, ACTIVE_TEAMS, get_bref_table
from .datasources.bref import BRefSession

class Level(Enum):
    MAJ = 1, 'MAJ'
    AAA = 2, 'AAA'
    AA = 3, 'AA'
    HIGH_A = 4, 'H-A'
    LOW_A = 5, 'L-A'
    ROK = 6, 'ROK'

LEVEL_HEADING = 'Lev'

# ids of tables used on bref
BATTING_TABLE_IDS = ['Catcher', 'Infielder2BSS3B', 'Outfield', 'FirstBaseDesignatedHitterorPinchHitter', 'Utility']
PITCHING_TABLE_IDS = ['Right-HandedStarters', 'Left-HandedStarters', 'Right-HandedRelievers',
                          'Left-HandedRelievers', 'OtherPitcher', 'Closers']

session = BRefSession()

def get_soup(team: str, player_type: str) -> BeautifulSoup:
    url = (f'https://www.baseball-reference.com/teams/{team}/{ACTIVE_TEAMS_MAPPING[team]}-'
           f'organization-{player_type}.shtml')
    s = session.get(url).content
    return BeautifulSoup(s, "lxml")

def process_tables(soup: BeautifulSoup, table_ids: [str], min_level: Level = Level.MAJ) -> pd.DataFrame:
    data = []

    headings = []

    # index of level column
    lev_index = 0

    for table_id in table_ids:

        # get depth chart table
        table = get_bref_table(table_id, soup)

        # headings are always the same, only need to set them once
        if not headings:
            headings = [th.get_text() for th in table.find("tr").find_all("th")]

            # remove the Rk header, it's unnecessary
            headings.pop(0)

            # add ID column name and alt url for players that don't have an ID
            headings.append('player_ID')
            headings.append('Alt URL')

            lev_index = headings.index(LEVEL_HEADING)

        # pull in data rows
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            player_link = row.find('a')
            if not player_link:
                continue
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]

            print(cols)

            # skip if level is not in requested range
            player_level = Level[cols[lev_index]]
            print(player_link)
            if player_level.value > min_level.value:
                continue

            # find bref ID in player link and add to data
            cols.append(get_bref_id_from_player_link(player_link.get('href')))

            data.append(cols)

    # use headings for column names
    return pd.DataFrame(data, columns=headings)

@cache.df_cache()
def depth_chart_batting(team: str, min_level: Level = Level.MAJ) -> pd.DataFrame:
    """
    Returns a pandas DataFrame of the position players in the system of the specified team. Players returned will
    play at level specified in min_level or above.

    ARGUMENTS
        team (str): the three letter abbreviation of an active MLB team
        min_level (str): minimum level for players to be returned. For example a min_level of 'AA' means major league
            players, AAA players, and AA players will be returned. Default is MAJ, or majors only.
    """

    if not team in ACTIVE_TEAMS:
        raise ValueError(
            "Supplied team must be an active MLB team."
        )

    # retrieve html from baseball reference
    soup = get_soup(team, 'batting')
    df = process_tables(soup, BATTING_TABLE_IDS, min_level)
    return df

@cache.df_cache()
def depth_chart_pitching(team: str, min_level: Level = Level.MAJ) -> pd.DataFrame:
    """
    Returns a pandas DataFrame of the pitchers in the system of the specified team. Players returned will
    play at level specified in min_level or above.

    ARGUMENTS
        team (str): the three letter abbreviation of an active MLB team
        min_level (str): minimum level for players to be returned. For example a min_level of 'AA' means major league
            players, AAA players, and AA players will be returned. Default is MAJ, or majors only.
    """

    if not team in ACTIVE_TEAMS:
        raise ValueError(
            "Supplied team must be an active MLB team."
        )

    # retrieve html from baseball reference
    soup = get_soup(team, 'pitching')
    df = process_tables(soup, PITCHING_TABLE_IDS, min_level)
    return df

@cache.df_cache()
def depth_chart(team: str, min_level: Level = Level.MAJ) -> pd.DataFrame:
    """
    Returns a pandas DataFrame of the players in the system of the specified team. Players returned will
    play at level specified in min_level or above.

    ARGUMENTS
        team (str): the three letter abbreviation of an active MLB team
        min_level (str): minimum level for players to be returned. For example a min_level of 'AA' means major league
            players, AAA players, and AA players will be returned. Default is MAJ, or majors only.
    """
    return depth_chart_pitching(team, min_level).concat(depth_chart_batting(team, min_level))
