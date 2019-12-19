#################################################################
# 1. Make sure the EC2 instance has the HTTPS and 8050 ports open
# 2. Get this shell script from github
# 3. Run script
# 4. We will use SUDO to run docker in order to avoid loging out
#################################################################

#Install docker to correctly display Dash content
wget https://get.docker.com/
mv index.html getDocker.sh
chmod 744 getDocker.sh
sh getDocker.sh
sudo usermod -aG docker ubuntu
# At this stage we should logout, but we wont so we keep using sudo

#Get docker container
sudo docker pull yabramuvdi/dashboards:latest
sudo docker run -d --name app -p 8050:8050 yabramuvdi/dashboards:latest
