-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Creates a fresh copy of the tournament database after dropping the current one
\c vagrant
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament


-- Players Table
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name TEXT
);

-- Matches Table
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    winner INTEGER REFERENCES players(id),
    loser INTEGER REFERENCES players(id)
);


-- Standings View
CREATE VIEW standings
AS SELECT players.id as player, name,
(SELECT count(matches.winner) FROM matches
 WHERE players.id = matches.winner) as wins,
(SELECT count(matches.id) FROM matches
 WHERE players.id = matches.winner
 OR players.id = matches.loser) as matches
FROM players
ORDER BY wins DESC, matches DESC;
