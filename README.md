# StreamStory2 - PostgreSQL connector

## Deploy

Buiild the docker file with:

```docker build -t e3ailab/uploader_ss2_psql_atena .```

 Push to DockerHub with `docker push`. After that, deploy on a target machine (Atena) with `docker run -d --network=streamstory_streamstory e3ailab/uploader_ss2_psql_atena`.

## Setup

You can check `lastts.txt` that it containts the last timestamp of a notification in the DB (can be changed manually in order to load new notifications).

Run the script with `python index.py`. The script will run a scheduler, which will check new notifications in PostgreSQL every second. You can adjust the timer to a more reasonable interval (1 minute) for production in `index.py` line 98.

## Results

The procedure will return an array of JSON objects (like depicted below).

```json
[
    {
        'id': 1,
        'user_id': 12,
        'model_id': 83,
        'title': 'Test alert',
        'content': 'Test content of the alert',
        'time': 1649931489368.622
    }
]
```

These JSON objects should be converted into alerts and sent to NAIADES platform via FIWARE.


# Obsolete

## Old development environment - OBSOLETE

Running the docker component on Atena (code is located at `/mnt/data/projects/naiades/ss2-psql`):
```
sudo docker run -it --rm -v /mnt/data/projects/naiades/ss2-psql/services:/home/app --network=streamstory_streamstory python:3.9 /bin/bash
```

This will open the docker in the streamstory network (so that PosgreSQL will be accessible to the scripts).