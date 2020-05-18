# mecs
Massive Event Correlation System

## How to set up the non-Docker system:
Prerequisites: RabbitMQ, python3, python3-pip NPM

Clone the repository:
```
git clone https://github.com/ciprianprohozescu/mecs/
```

Start up the RabbitMQ broker
```
rabbitmq-server
```
Alternatively if you have docker installed, there is a temporary dockerised setup:
```
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

Install python packages by navigating to the mecs folder and typing
```
pip3 install -r requirements.txt
```

To set up the web client, run ```npm install``` in the *web-mecs* directory.

Go to this [link](https://ucndk-my.sharepoint.com/:f:/g/personal/1074220_ucn_dk/EvqMEWsenkZBrtd3PlsOXmkBMmqUWVRY7QTJH3zVtSmqsg?e=kjyRQv) to download test data files.
The files correspond accordingly:
* kibanaEvents.py   - errors_last_15_minutes.csv
* fakeEvents.py     - fake_data.json
* ringdumpEvents.py - ringdump.json

### Run the non-docker setup
To test the project, you will need at least 1 source, the gateway, and at least one consumer:

Run the gateway:
```
python3 gateway.py
```

Run a source with its corresponding data file in your current working directory:
```
python3 kibanaEvents.py
```
or specify the location of the data file
```
python3 kibanaEvents.py /path/to/csv.csv
```

Finally, you can run one or both of the consumers to test that the system is working correctly

Run the database consumer by navigating to consumers/Database and running
```
python3 webConsumer.py
```

To run the web client, you will need 3 separate services, run these in separate sessions:

```npm run serve``` in the *web-mecs* directory

```python3 webApi.py``` in the *apis* directory

```python3 webConsumer``` in *consumers/WebConsumer*


## Docker and docker swarm
Tested on a Linux environment

### Base setup
Begin by installing docker and adding your desired user to the docker group
Remember to replace commands with your OS equivelants (example will work on most debian based systems)
```
sudo apt-get update
sudo apt install docker.io
sudo apt install docker-compose
sudo gpasswd -a docker-user docker
```

To run a base test of the entire system, navigate to the home folder of the project and run:
```
docker-compose up
```
Verify its working by checking for a generated *sqlite3-database* directory in your cwd, with a sqlite3 database inside
Verify the website is working by connecting to localhost:8080 on the machine

NOTE: if you are running this on a server rather than your own network, you will need to edit the API_ENDPOINT environment variable for the webclient service:
```
API_ENDPOINT: 'http//<IP_OF_YOUR_SERVER>:5000'
```
NOTE: if you are having issues with the rabbitmq setup during this section, it is worth trying to delete cached containers, next time you run the system use:
```
docker-compose up --force-recreate
```

## Docker Swarm 
Docker swarm is relatively simple, however there is a lot of possible devitaion based on preference, use this guide only to test functionality.

Initialise your swarm on a server:
```
docker swarm init
```

### Multi-server setup
Find your join token (for the purposes of this test, we'll just be using a manager token)
```
docker swarm join-token manager
```

Join the swarm cluster on your other server by running the command that was previously outputted

To test your setup, split your docker compose file arbitrarily, for the purposes of testing, avoid overlap.
Identify the name of the network being used in the stack:
```
> docker network list
NETWORK ID          NAME                   DRIVER              SCOPE
565b42b0df92        bridge                 bridge              local
9b28fd3c3ec7        docker_gwbridge        bridge              local
d038bf5f6429        host                   host                local
bjmk52xfv2m0        ingress                overlay             swarm
d71f54cd9268        mecs_rabbitmqnetwork   bridge              local
a5604b421a63        none                   null                local
```
In our case, its called "mecs_rabbitmqnetwork"

Append this to the bottom of the docker compose file in your "other" server, make adjustements for your case
```
networks:
  rabbitmqnetwork:
    external:
      name: mecs_rabbitmqnetwork
```

Run each section with:
```
docker stack deploy --compose-file docker-compose.yml
```

Test by looking for the sqlite database, and checking for the website at the address that the web client service is running

### Scalability
Unfortunately it takes a very high load to overcome the gateway image, for testing purposes we will be switching exclusively to kibana events, and changing the gateway image to a version that takes a full second to process kibana events.

Begin by swapping the gateway image for ```badgateway```

Run the docker watcher script
```
python3 watchers/docker-watcher.py
```

Run the stack as you have been previously

Next scale up the kibanaevents service, the name of the service can will differ based on the name of your stack:
```
docker service scale project_kibanaevents=5
```
Observe that the watcher script is scaling up the gateway service, once it reaches a point at which its no longer rising, scale kibanaevents back to 1
```
docker service scale project_kibanaevents=1
```
The watcher script should eventually come back to a resting point of approximately 1 gateway
