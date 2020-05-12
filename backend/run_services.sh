# 数据库初始化文件
sudo chmod -R 777 ./init
# redis conf和log文件
mkdir -p redis/conf
cp ciwei/config/server/redis.conf redis/conf
mkdir -p redis/log
touch redis/log/redis-server.log
sudo chmod -R 777 redis
# es 的日志文件
mkdir -p es/log
sudo chmod -R 777 es
# 啟動服務
sudo docker-compose up



