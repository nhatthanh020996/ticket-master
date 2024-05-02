sudo docker stop $(sudo docker ps -a -q --filter ancestor=prod-webserver) && sudo docker rm $(sudo docker ps -a -q --filter ancestor=prod-webserver)
sudo docker build -t prod-webserver .
sudo docker run -d --name prod-webserver --network dockers_dms-network -p 8000:8000 -v $(pwd)/logs:/code/logs --env-file .env prod-webserver
sudo docker logs -f -n 100 prod-webserver