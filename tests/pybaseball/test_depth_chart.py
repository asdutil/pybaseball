from typing import Callable

import pytest

from pybaseball import depth_chart

@pytest.fixture(name="sample_batting_html")
def _sample_batting_html(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('depth_chart_batting.html')

@pytest.fixture(name="sample_pitching_html")
def _sample_pitching_html(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('depth_chart_pitching.html')

def test_active_roster(response_get_monkeypatch: Callable, sample_batting_html: str, sample_pitching_html: str):
    response_get_monkeypatch(sample_batting_html)
    response_get_monkeypatch(sample_pitching_html)

    # ensure error is raised if bad team is given
    with pytest.raises(ValueError) as ex_info:
        depth_chart('FAKE')
    assert str(ex_info.value) == "Supplied team must be an active MLB team."

    # ensure error is raised if bad level is given
    with pytest.raises(ValueError) as ex_info:
        depth_chart('WSN', min_level='fake')
    assert str(ex_info.value) == "Invalid value of 'fake'. Values must be a valid member of the enum: Level"

    depth_chart_result = depth_chart('WSN')

    # there should be people on the 26-man roster returned
    assert not depth_chart_result[depth_chart_result['status'] == '26-man'].empty

    # make sure IL is populated
    assert active_roster_result[active_roster_result["Name"] == "Cade Cavalli"]["IL"].values[0] == "15-day"

    # make sure a player who hasn't played in the majors has Alt URL set correctly
    assert active_roster_result[active_roster_result["Name"] == "Andry Lara"]["Alt URL"].values[0]