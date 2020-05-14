sudo docker stop backend_web_1
docker exec backend_db_1 bash -c "mysql -uroot -pwcx9517530 < /docker-entrypoint-initdb.d/ddl/test_db_clean.sql"
docker exec backend_redis_1 bash -c "cat /data/test_redis_clean.txt | redis-cli -a lyx147"
curl -XPOST localhost:9200/goods_test/_delete_by_query -H "Content-Type:application/json" -d '{"query":{"match_all":{}}}'
export production_test=1
sudo docker-compose up web


