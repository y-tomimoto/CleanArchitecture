---- drop ----
DROP TABLE IF EXISTS `test_table`;

---- create ----
create table
IF not exists `test_table`
(
 `memo_id`               INT
(20) AUTO_INCREMENT,
 `memo`             VARCHAR
(20) NOT NULL,
 `memo_author`             VARCHAR
(20) NOT NULL,
 `memo_user_agent`             VARCHAR
(500) NOT NULL,
  PRIMARY KEY
(`memo_id`)
);