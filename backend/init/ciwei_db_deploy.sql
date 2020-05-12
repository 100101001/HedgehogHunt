SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS `ciwei_db_test`;
USE `ciwei_db_test`;
SELECT @table_count:=count(TABLE_NAME) FROM information_schema.TABLES WHERE TABLE_SCHEMA='ciwei_db_test';
IF @table_count < 1 THEN
  source ddl/create_tables.sql
END IF

CREATE DATABASE IF NOT EXISTS `ciwei_db`;
USE `ciwei_db`;
SELECT @table_count:=count(TABLE_NAME) FROM information_schema.TABLES WHERE TABLE_SCHEMA='ciwei_db';
IF @table_count < 1 THEN
  source ddl/create_tables.sql
END IF