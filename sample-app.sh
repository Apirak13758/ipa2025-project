#!/bin/bash

# Setup
rm -rf tempdir
mkdir -p tempdir/templates tempdir/static

# Copy files
cp app.py tempdir/
cp requirements.txt tempdir/
[ -d templates ] && cp -r templates/* tempdir/templates/
[ -d static ] && cp -r static/* tempdir/static/

# Create Dockerfile
cat <<EOF > tempdir/Dockerfile
FROM python:3.10-slim
WORKDIR /home/myapp
COPY requirements.txt .
COPY ./static ./static/
COPY ./templates ./templates/
COPY app.py .
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python3", "app.py"]
EOF

# Build and run
cd tempdir || exit
docker build -t app .
docker network create app-net
docker run -d -p 27017:27017 --network app-net -v mongo-data:/data/db --name mongo mongo:6
docker run -t -d -p 8080:8080 --network app-net --memory=1g --name web app
docker ps -a
