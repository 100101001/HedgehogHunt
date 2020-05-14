CREATE DATABASE IF NOT EXISTS `ciwei_db_test`;
USE `ciwei_db_test`;
source /docker-entrypoint-initdb.d/ddl/create_tables.sql;
UPDATE `product` SET price=price/1000 WHERE id<14;
UPDATE `product` SET price=0.02 WHERE id=15;
