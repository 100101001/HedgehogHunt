SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS `ciwei_db_test`;
USE `ciwei_db_test`;
source /docker-entrypoint-initdb.d/ddl/create_tables.sql;

CREATE DATABASE IF NOT EXISTS `ciwei_db`;
USE `ciwei_db`;
source /docker-entrypoint-initdb.d/ddl/create_tables.sql;
