docker build -t fyc-api .

##run app in docker
docker run --rm -p 8000:8000 fyc-api:latest
