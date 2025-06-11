# Depth Chart

`depth_chart(team, min_level='MAJ')`

Get a team's current depth chart. `min_level` can be used to limit the results by level. Possible values for `min_level`
Are:
- `'MAJ'`: the major leagues
- `'AAA'`
- `'AA'`
- `'H-A'`: high A
- `'L-A'`: low A
- `'ROK'`: rookie ball

## Arguments
`team:` String. Must be the 3-letter abbreviation for an MLB team used by Baseball Reference.
`min_level:` String. See above for the options. Players at the specified level or above will be returned

## Examples of valid queries

```python
from pybaseball import depth_chart

# get the list of players who have played in the majors this year for the Nationals 
data = depth_chart('WSN')

# get the players who have played AA or above this season for the Orioles
data = depth_chart('BAL', min_level='AA')

```
# Pitching Depth Chart

`depth_chart_pitching(team, min_level='MAJ')`

Get a team's current pitching depth chart. Functions the same as `depth_chart` but retrieves pitchers only.

## Examples of valid queries

```python
from pybaseball import depth_chart_pitching

# get the list of players who have pitched in the majors this year for the Nationals 
data = depth_chart_pitching('WSN')

```

# Batting Depth Chart

`depth_chart_batting(team, min_level='MAJ')`

Get a team's current position player depth chart. Functions the same as `depth_chart` but retrieves batters only.

## Examples of valid queries

```python
from pybaseball import depth_chart_batting

# get the list of non-pitchers who have played in the majors this year for the Orioles 
data = depth_chart_batting('BAL')

```