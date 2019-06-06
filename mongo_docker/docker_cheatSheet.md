# MongoDb in a docker container

For dev purpose we use a docker instance of mongodb to run our database mangement system.

## Commands used

### Create image (when in the mongo_docker folder)

    docker build -t hello_mongo:latest . 

### Create a volume (enable data persistence)

    docker volume create mongo-volume 

### Launch the image

    docker run -p 27017:27017 --mount source=mongo-volume,target=/data/db hello_mongo:latest
