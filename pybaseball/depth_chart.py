from typing import Optional, Literal

import pandas as pd
from bs4 import BeautifulSoup

from . import cache
from .utils import most_recent_season, get_bref_id_from_player_link, ACTIVE_TEAMS_MAPPING, ACTIVE_TEAMS
from .datasources.bref import BRefSession

session = BRefSession()

def get_soup(team: str, type: str) -> BeautifulSoup:
    url = f'https://www.baseball-reference.com/teams/{team}/{ACTIVE_TEAMS_MAPPING[team]}-organization-{type}.shtml'
    s = session.get(url).content
    return BeautifulSoup(s, "lxml")

def get_tables_pitching(soup: BeautifulSoup, min_level: str) -> pd.DataFrame:
    pitching_table_ids = ['Right-HandedStarters', 'Left-HandedStarters', 'Right-HandedRelievers',
                          'Left-HandedRelievers', 'OtherPitcher', 'Closers']

    pass

def get_tables_batting(soup: BeautifulSoup, min_level: str) -> pd.DataFrame:
    data = []

    batting_table_ids = ['Catcher', 'Infielder2BSS3B', 'Outfield', 'FirstBaseDesignatedHitterorPinchHitter', 'Utility']

    for table_id in batting_table_ids:

        # get depth chart table
        table = soup.find(id=table_id)
        headings = [th.get_text() for th in table.find("tr").find_all("th")]

        # remove the Rk header, it's unnecessary
        headings.pop(0)

        # add ID column name and alt url for players that don't have an ID
        headings.append('player_ID')
        headings.append('Alt URL')

        # pull in data rows
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            player_link = row.find('a')
            if not player_link:
                continue
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]

            # find bref ID in player link and add to data
            cols.append(get_bref_id_from_player_link(player_link.get('href')))

            data.append([ele for ele in cols])

    # use headings for column names
    return pd.DataFrame(data, columns=headings)

@cache.df_cache()
def depth_chart_batting(team: str, min_level: Literal['MAJ', 'AAA', 'AA', 'H-A', 'L-A', 'ROK']) -> pd.DataFrame:
    """
    Returns a pandas DataFrame of the position players in the system of the specified team. Players returned will
    play at level specified in min_level or above.

    ARGUMENTS
        team (str): the three letter abbreviation of an active MLB team
        min_level (str): minimum level for players to be returned. For example a min_level of 'AA' means major league
            players, AAA players, and AA players will be returned.
    """

    if not team in ACTIVE_TEAMS:
        raise ValueError(
            "Supplied team must be an active MLB team."
        )

    # retrieve html from baseball reference
    soup = get_soup(team, 'batting')
    df = get_tables_batting(soup, min_level)
    return df

@cache.df_cache()
def depth_chart_pitching(team: str, min_level: Literal['MAJ', 'AAA', 'AA', 'H-A', 'L-A', 'ROK']) -> pd.DataFrame:
    """
    Returns a pandas DataFrame of the pitchers in the system of the specified team. Players returned will
    play at level specified in min_level or above.

    ARGUMENTS
        team (str): the three letter abbreviation of an active MLB team
        min_level (str): minimum level for players to be returned. For example a min_level of 'AA' means major league
            players, AAA players, and AA players will be returned.
    """

    if not team in ACTIVE_TEAMS:
        raise ValueError(
            "Supplied team must be an active MLB team."
        )

    # retrieve html from baseball reference
    soup = get_soup(team, 'pitching')
    df = get_tables_pitching(soup, min_level)
    return df

@cache.df_cache()
def depth_chart(team: str, min_level: Literal['MAJ', 'AAA', 'AA', 'H-A', 'L-A', 'ROK']) -> pd.DataFrame:
    """
    Returns a pandas DataFrame of the players in the system of the specified team. Players returned will
    play at level specified in min_level or above.

    ARGUMENTS
        team (str): the three letter abbreviation of an active MLB team
        min_level (str): minimum level for players to be returned. For example a min_level of 'AA' means major league
            players, AAA players, and AA players will be returned.
    """
    return depth_chart_pitching(team, min_level).concat(depth_chart_batting(team, min_level))
