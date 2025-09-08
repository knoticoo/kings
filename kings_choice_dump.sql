PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE players (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	is_current_mvp BOOLEAN NOT NULL, 
	mvp_count INTEGER NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, is_excluded BOOLEAN DEFAULT 0 NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE TABLE alliances (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	is_current_winner BOOLEAN NOT NULL, 
	win_count INTEGER NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE TABLE events (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	description TEXT, 
	event_date DATETIME NOT NULL, 
	has_mvp BOOLEAN NOT NULL, 
	has_winner BOOLEAN NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS "mvp_assignments" (
    id INTEGER NOT NULL, 
    player_id INTEGER NOT NULL, 
    event_id INTEGER NOT NULL, 
    assigned_at DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(player_id) REFERENCES players (id), 
    FOREIGN KEY(event_id) REFERENCES events (id)
);
CREATE TABLE IF NOT EXISTS "winner_assignments" (
    id INTEGER NOT NULL, 
    alliance_id INTEGER NOT NULL, 
    event_id INTEGER NOT NULL, 
    assigned_at DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(alliance_id) REFERENCES alliances (id), 
    FOREIGN KEY(event_id) REFERENCES events (id)
);
COMMIT;
