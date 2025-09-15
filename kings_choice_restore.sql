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
INSERT INTO players VALUES(1,'Julija',0,2,'2025-08-27 22:51:03.181883','2025-09-15 05:58:15.688819',0);
INSERT INTO players VALUES(2,'Torradan',0,1,'2025-08-28 09:09:56.386472','2025-09-15 05:58:15.688819',0);
INSERT INTO players VALUES(3,'Szlachcic Kubus',0,1,'2025-08-28 09:10:24.971167','2025-09-15 05:58:15.688819',0);
INSERT INTO players VALUES(4,'Kinga',0,2,'2025-08-28 09:10:33.218890','2025-09-15 05:58:15.688819',0);
INSERT INTO players VALUES(9,'Mika',0,1,'2025-08-28 09:11:32.583256','2025-09-15 05:58:15.688819',0);
INSERT INTO players VALUES(10,'Noble Clara',0,1,'2025-08-28 09:11:45.503156','2025-09-15 05:58:15.688819',0);
INSERT INTO players VALUES(12,'Nicolai',0,1,'2025-08-28 09:12:01.285281','2025-09-15 05:58:15.688819',0);
INSERT INTO players VALUES(13,'Yadinijas Arja',0,1,'2025-08-28 09:12:22.652382','2025-09-15 05:58:15.688819',0);
INSERT INTO players VALUES(14,'Millie',0,1,'2025-08-28 09:12:30.325563','2025-09-15 05:58:15.688819',0);
INSERT INTO players VALUES(17,'Charles',0,1,'2025-08-28 09:12:52.292978','2025-09-15 20:18:12.088551',1);
INSERT INTO players VALUES(18,'Knotico',0,1,'2025-08-29 21:40:15.330106','2025-09-15 05:58:15.688819',0);
INSERT INTO players VALUES(19,'Diane',0,1,'2025-09-08 20:10:01.418086','2025-09-15 05:58:15.688819',0);
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
INSERT INTO alliances VALUES(1,'AGE',1,1,'2025-08-28 09:06:17.930387','2025-09-15 07:35:18.909981');
INSERT INTO alliances VALUES(4,'SOR',0,0,'2025-08-28 09:15:30.143619','2025-09-15 07:35:18.907060');
INSERT INTO alliances VALUES(5,'LAS',0,0,'2025-09-04 08:44:54.698021','2025-09-15 07:35:18.907060');
INSERT INTO alliances VALUES(6,'LHD',0,1,'2025-09-04 08:45:03.940411','2025-09-15 07:35:18.907060');
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
INSERT INTO events VALUES(1,'Нежить',NULL,'2025-08-28 12:12:00.000000',1,0,'2025-08-28 09:13:04.223710');
INSERT INTO events VALUES(2,'Нежить меж-сервер',NULL,'2025-08-28 12:13:00.000000',1,0,'2025-08-28 09:13:16.532454');
INSERT INTO events VALUES(3,'Шахматы',NULL,'2025-08-28 12:13:00.000000',1,1,'2025-08-28 09:13:25.198395');
INSERT INTO events VALUES(4,'Шахматы меж-сервер',NULL,'2025-08-28 12:13:00.000000',1,1,'2025-08-28 09:13:35.629318');
INSERT INTO events VALUES(5,'Неизведанные воды',NULL,'2025-08-28 12:13:00.000000',1,0,'2025-08-28 09:13:55.220715');
INSERT INTO events VALUES(6,'Рост Опыта Альянса',NULL,'2025-08-29 11:29:00.000000',1,0,'2025-08-29 08:31:00.905116');
INSERT INTO events VALUES(7,'Рост Альянса',NULL,'2025-08-30 00:41:00.000000',1,0,'2025-08-29 21:41:49.320890');
INSERT INTO events VALUES(8,'Таинственный убийца',NULL,'2025-08-31 01:21:00.000000',1,0,'2025-08-30 22:21:37.496704');
INSERT INTO events VALUES(9,'Таинственный убийца меж-сервер',NULL,'2025-08-31 21:23:00.000000',1,0,'2025-08-31 18:23:21.414541');
INSERT INTO events VALUES(10,'Рост очков Альянс Арены',NULL,'2025-09-04 11:43:00.000000',0,1,'2025-09-04 08:44:06.756083');
INSERT INTO events VALUES(11,'Рост очков Альянс Арены',NULL,'2025-09-04 11:47:00.000000',1,0,'2025-09-04 08:47:55.801449');
INSERT INTO events VALUES(12,'Королевская Шахта',NULL,'2025-09-05 21:40:00.000000',1,0,'2025-09-05 18:40:14.571867');
INSERT INTO events VALUES(13,'Аллая Леди',NULL,'2025-09-11 19:40:00.000000',1,0,'2025-09-11 16:40:58.841523');
INSERT INTO events VALUES(15,'Алая ведьма межсерверный',NULL,'2025-09-13 23:36:00.000000',1,0,'2025-09-13 20:36:39.501079');
INSERT INTO events VALUES(16,'Покер',NULL,'2025-09-15 08:54:00.000000',1,0,'2025-09-15 05:54:43.531536');
INSERT INTO events VALUES(17,'Нежити',NULL,'2025-09-15 08:57:00.000000',1,1,'2025-09-15 05:57:36.079511');
CREATE TABLE mvp_assignments (
	id INTEGER NOT NULL, 
	player_id INTEGER NOT NULL, 
	event_id INTEGER NOT NULL, 
	assigned_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(player_id) REFERENCES players (id), 
	FOREIGN KEY(event_id) REFERENCES events (id)
);
INSERT INTO mvp_assignments VALUES(1,2,5,'2025-08-28 09:14:14.752409');
INSERT INTO mvp_assignments VALUES(2,3,1,'2025-08-28 09:14:30.959323');
INSERT INTO mvp_assignments VALUES(3,4,2,'2025-08-28 09:14:46.590984');
INSERT INTO mvp_assignments VALUES(4,10,3,'2025-08-28 09:16:59.598195');
INSERT INTO mvp_assignments VALUES(5,12,7,'2025-08-29 21:42:02.502535');
INSERT INTO mvp_assignments VALUES(6,1,8,'2025-08-30 22:21:49.613313');
INSERT INTO mvp_assignments VALUES(8,18,11,'2025-09-04 12:08:06.881845');
INSERT INTO mvp_assignments VALUES(9,14,12,'2025-09-05 18:40:31.901409');
INSERT INTO mvp_assignments VALUES(10,19,8,'2025-09-08 20:10:11.961555');
INSERT INTO mvp_assignments VALUES(11,9,13,'2025-09-11 16:41:14.014289');
INSERT INTO mvp_assignments VALUES(12,13,4,'2025-09-11 16:41:26.926164');
INSERT INTO mvp_assignments VALUES(13,4,15,'2025-09-13 20:41:50.644174');
INSERT INTO mvp_assignments VALUES(14,1,16,'2025-09-15 05:55:16.484982');
INSERT INTO mvp_assignments VALUES(15,17,17,'2025-09-15 05:58:15.693076');
CREATE TABLE winner_assignments (
	id INTEGER NOT NULL, 
	alliance_id INTEGER NOT NULL, 
	event_id INTEGER NOT NULL, 
	assigned_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(alliance_id) REFERENCES alliances (id), 
	FOREIGN KEY(event_id) REFERENCES events (id)
);
INSERT INTO winner_assignments VALUES(1,6,10,'2025-09-04 08:45:12.594587');
INSERT INTO winner_assignments VALUES(2,1,17,'2025-09-15 07:35:18.911723');
CREATE TABLE guide_categories (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	slug VARCHAR(100) NOT NULL, 
	description TEXT, 
	icon VARCHAR(50), 
	sort_order INTEGER, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	UNIQUE (slug)
);
INSERT INTO guide_categories VALUES(1,'Knights','knights','Comprehensive guides for all types of knights including tier lists, builds, and strategies.','bi-shield-fill',1,1,'2025-09-08 17:47:13.112247','2025-09-08 17:47:13.112250');
INSERT INTO guide_categories VALUES(2,'Events','events','Event guides and strategies for Alliance Arena, Twilight Castle, and other game events.','bi-calendar-event-fill',2,1,'2025-09-08 17:47:13.113153','2025-09-08 17:47:13.113155');
INSERT INTO guide_categories VALUES(3,'Alliance','alliance','Alliance management, strategies, and coordination guides.','bi-people-fill',3,1,'2025-09-08 17:47:13.113621','2025-09-08 17:47:13.113622');
INSERT INTO guide_categories VALUES(4,'Resources','resources','Resource management, farming guides, and optimization tips.','bi-gem',4,1,'2025-09-08 17:47:13.113984','2025-09-08 17:47:13.113985');
CREATE TABLE guides (
	id INTEGER NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	slug VARCHAR(200) NOT NULL, 
	content TEXT NOT NULL, 
	excerpt TEXT, 
	category_id INTEGER NOT NULL, 
	featured_image VARCHAR(500), 
	is_published BOOLEAN NOT NULL, 
	is_featured BOOLEAN NOT NULL, 
	view_count INTEGER NOT NULL, 
	sort_order INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (slug), 
	FOREIGN KEY(category_id) REFERENCES guide_categories (id)
);
INSERT INTO guides VALUES(1,'Strength Knight Tier List','strength-knights',replace('<h1><strong>STRENGTH KNIGHT TIER LIST</strong></h1>\n\n<p>Typically, most Knights that have an Aura will rank high on any Tier List of the Best King''s Choice Knights and this one is no different. However, it is also worth noting that many of the top Knights only become available to players after a few months in the game as certain unlock items, such as Crowns, begin to drop from Events. Therefore, in the early game, you will likely see yourself developing Knights in this list from ranks S. This is perfectly viable as many of these, especially the Arthurian Legends, will continue to be viable as you move forward.</p>\n\n<p>In the Tier List below, we rank the Best Strength Knights in King''s Choice from best to worst. EX+ represents the very best strength Knights, whilst F represents the absolute worst, and these will never be worth your time!</p>\n\n<h2><strong>EX+</strong></h2>\n<ul>\n<li>Joan of Arc</li>\n</ul>\n\n<h2><strong>EX</strong></h2>\n<ul>\n<li>Queen Elizabeth</li>\n</ul>\n\n<h2><strong>SSS</strong></h2>\n<ul>\n<li>Frederick Barbarossa</li>\n<li>Charlemagne</li>\n<li>Richard I</li>\n<li>William I</li>\n<li>El Cid</li>\n<li>Igor</li>\n<li>Roland</li>\n<li>Siegfried</li>\n<li>Vlad Dracula</li>\n</ul>\n\n<h2><strong>S</strong></h2>\n<ul>\n<li>Guinevere</li>\n<li>Lancelot</li>\n<li>Mordred</li>\n<li>Gawain</li>\n<li>King Arthur</li>\n<li>Leonardo da Vinci</li>\n<li>Queen Christina</li>\n</ul>\n\n<h2><strong>A</strong></h2>\n<ul>\n<li>Thomas Aquinas</li>\n<li>Aristotle</li>\n<li>Homer</li>\n<li>Nicolaus Copernicus</li>\n</ul>\n\n<h2><strong>B</strong></h2>\n<ul>\n<li>William Shakespeare</li>\n<li>Madame de Pompadour</li>\n<li>Jacques</li>\n<li>Geoffrey Plantagenet</li>\n<li>Robin Hood</li>\n<li>Edward</li>\n<li>Francis Drake</li>\n</ul>\n\n<h2><strong>C</strong></h2>\n<ul>\n<li>Ferdinand Magellan</li>\n<li>Galileo Galilei</li>\n<li>Bertrand du Guesclin</li>\n<li>Ambrose</li>\n<li>Charles Martel</li>\n<li>Sundiata Keita</li>\n</ul>\n\n<h2><strong>F</strong></h2>\n<ul>\n<li>Duke of York</li>\n<li>Rose</li>\n<li>Bradamante</li>\n<li>Hypatia</li>\n<li>Merlin</li>\n<li>Michelangelo</li>\n<li>Earl of Warwick</li>\n<li>Talbot</li>\n<li>Roger Bacon</li>\n<li>Old Hunter</li>\n<li>Greg</li>\n<li>Thomas Cromwell</li>\n<li>Golyat</li>\n<li>Dante Alighieri</li>\n<li>Charles Brandon</li>\n<li>Simon de Montfort</li>\n<li>John Blanke</li>\n<li>Harpagon</li>\n<li>Marco Polo</li>\n<li>Terrence</li>\n<li>Johannes Gutenberg</li>\n<li>Artemisia Gentileschi</li>\n<li>Moremi Ajasoro</li>\n<li>Roger</li>\n<li>William Tell</li>\n<li>Raphael</li>\n<li>Andreas Vesalius</li>\n<li>Thomas Boleyn</li>\n<li>Andrew</li>\n<li>Bontemps</li>\n</ul>','\n',char(10)),'Complete tier list ranking all Strength Knights from EX+ to F tier, with detailed explanations of each knight''s viability.',1,NULL,1,1,3,0,'2025-09-08 17:47:13.119122','2025-09-08 17:49:49.432039');
INSERT INTO guides VALUES(2,'Intellect Knight Tier List','intellect-knights',replace('<h1><strong>INTELLECT KNIGHT TIER LIST</strong></h1>\n\n<p>Intellect Knights are crucial for your kingdom''s development and research capabilities. This tier list ranks all Intellect Knights based on their effectiveness in various game modes and their overall utility.</p>\n\n<h2><strong>EX+</strong></h2>\n<ul>\n<li>Leonardo da Vinci</li>\n</ul>\n\n<h2><strong>EX</strong></h2>\n<ul>\n<li>Nicolaus Copernicus</li>\n<li>Galileo Galilei</li>\n</ul>\n\n<h2><strong>SSS</strong></h2>\n<ul>\n<li>Thomas Aquinas</li>\n<li>Aristotle</li>\n<li>Homer</li>\n<li>Roger Bacon</li>\n</ul>\n\n<h2><strong>S</strong></h2>\n<ul>\n<li>William Shakespeare</li>\n<li>Dante Alighieri</li>\n<li>Johannes Gutenberg</li>\n<li>Raphael</li>\n</ul>\n\n<h2><strong>A</strong></h2>\n<ul>\n<li>Michelangelo</li>\n<li>Andreas Vesalius</li>\n<li>Artemisia Gentileschi</li>\n<li>Moremi Ajasoro</li>\n</ul>\n\n<h2><strong>B</strong></h2>\n<ul>\n<li>Hypatia</li>\n<li>Marco Polo</li>\n<li>William Tell</li>\n</ul>\n\n<h2><strong>C</strong></h2>\n<ul>\n<li>Merlin</li>\n<li>Thomas Cromwell</li>\n<li>Thomas Boleyn</li>\n</ul>\n\n<h2><strong>F</strong></h2>\n<ul>\n<li>All other Intellect Knights not listed above</li>\n</ul>','\n',char(10)),'Comprehensive tier list for all Intellect Knights, ranking them based on research capabilities and kingdom development.',1,NULL,1,1,1,0,'2025-09-08 17:47:13.119896','2025-09-08 20:07:47.095079');
INSERT INTO guides VALUES(3,'Alliance Arena Guide','alliance-arena',replace('<h1><strong>ALLIANCE ARENA GUIDE</strong></h1>\n\n<p>Alliance Arena is one of the most competitive events in King''s Choice. This guide will help you understand the mechanics and develop winning strategies.</p>\n\n<h2><strong>Event Overview</strong></h2>\n<p>Alliance Arena is a PvP event where alliances compete against each other for rewards and glory. The event typically lasts for several days and features multiple rounds of competition.</p>\n\n<h2><strong>Key Mechanics</strong></h2>\n<ul>\n<li><strong>Matchmaking:</strong> Alliances are matched based on their power and previous performance</li>\n<li><strong>Battle System:</strong> Each alliance can deploy multiple knights in strategic formations</li>\n<li><strong>Rewards:</strong> Based on final ranking and individual performance</li>\n</ul>\n\n<h2><strong>Strategy Tips</strong></h2>\n<ol>\n<li><strong>Formation Planning:</strong> Arrange your strongest knights in optimal positions</li>\n<li><strong>Resource Management:</strong> Save resources for key battles</li>\n<li><strong>Communication:</strong> Coordinate with alliance members for maximum effectiveness</li>\n<li><strong>Timing:</strong> Know when to attack and when to defend</li>\n</ol>\n\n<h2><strong>Recommended Knights</strong></h2>\n<p>Focus on developing these knights for Alliance Arena:</p>\n<ul>\n<li>Joan of Arc (EX+)</li>\n<li>Queen Elizabeth (EX)</li>\n<li>Frederick Barbarossa (SSS)</li>\n<li>Charlemagne (SSS)</li>\n</ul>','\n',char(10)),'Complete guide to Alliance Arena including mechanics, strategies, and recommended knights for competitive play.',2,NULL,1,0,0,0,'2025-09-08 17:47:13.120411','2025-09-08 17:47:13.120412');
INSERT INTO guides VALUES(4,'Twilight Castle Guide','twilight-castle',replace('<h1><strong>TWILIGHT CASTLE GUIDE</strong></h1>\n\n<p>Twilight Castle is a challenging PvE event that requires careful planning and strong knights. This guide covers everything you need to know.</p>\n\n<h2><strong>Event Structure</strong></h2>\n<p>Twilight Castle consists of multiple floors, each with increasing difficulty. Players must clear each floor to progress to the next level.</p>\n\n<h2><strong>Floor Mechanics</strong></h2>\n<ul>\n<li><strong>Boss Battles:</strong> Each floor has a powerful boss with unique abilities</li>\n<li><strong>Resource Requirements:</strong> Different floors require different types of resources</li>\n<li><strong>Time Limits:</strong> Some floors have time restrictions</li>\n</ul>\n\n<h2><strong>Preparation Tips</strong></h2>\n<ol>\n<li><strong>Level Up Knights:</strong> Ensure your main knights are at maximum level</li>\n<li><strong>Equipment:</strong> Upgrade weapons and armor for better stats</li>\n<li><strong>Formations:</strong> Experiment with different knight combinations</li>\n<li><strong>Resources:</strong> Stock up on healing items and buffs</li>\n</ol>\n\n<h2><strong>Recommended Team Compositions</strong></h2>\n<p>For different floor types:</p>\n<ul>\n<li><strong>Physical Floors:</strong> Focus on Strength and Leadership knights</li>\n<li><strong>Magic Floors:</strong> Include Intellect knights for magical damage</li>\n<li><strong>Balanced Floors:</strong> Mix of all knight types</li>\n</ul>','\n',char(10)),'Detailed guide to Twilight Castle event including floor mechanics, preparation tips, and recommended team compositions.',2,NULL,1,0,0,0,'2025-09-08 17:47:13.120784','2025-09-08 17:47:13.120785');
CREATE TABLE blacklist (
	id INTEGER NOT NULL, 
	alliance_name VARCHAR(100), 
	player_name VARCHAR(100), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO blacklist VALUES(1,'ESP',NULL,'2025-09-08 20:29:13.869201','2025-09-08 20:29:13.869205');
INSERT INTO blacklist VALUES(2,'FRA',NULL,'2025-09-08 20:29:21.113027','2025-09-08 20:29:21.113033');
INSERT INTO blacklist VALUES(3,'POL',NULL,'2025-09-08 20:29:26.427206','2025-09-08 20:29:26.427210');
COMMIT;