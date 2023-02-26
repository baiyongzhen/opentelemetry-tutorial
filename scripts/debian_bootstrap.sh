#!/bin/bash

set -e

# Install Docker
curl -fsSL get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker vagrant

# Install Docker Compose
sudo  curl -SL https://github.com/docker/compose/releases/download/v2.14.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose


# Install OpenJDK
sudo apt-get -y install openjdk-11-jdk

# Install pip
sudo apt-get -y install python-pip
sudo apt-get -y install python3-pip

# Disable firewall
sudo ufw disable