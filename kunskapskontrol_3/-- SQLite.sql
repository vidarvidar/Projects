-- SQLite

SELECT id, period, timestamp, minute, second, location_x, location_y, player, possession_team, shot_outcome, shot_statsbomb_xg
FROM WomensWorldCup2023 WHERE type IS 'Shot'
ORDER BY period, timestamp;

SELECT id, period, timestamp, minute, second, location_x, location_y, player, 
possession_team, pass_type, pass_length, pass_angle, pass_outcome
FROM WomensWorldCup2023 WHERE type IS 'Pass'
ORDER BY period, timestamp;
