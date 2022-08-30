#!/usr/bin/python
import psycopg2
from config import config
import json
import datetime, time
import schedule
import subprocess
import os
import copy
import requests
import logging

# project-based import
from data_models import alert_template
from custom_error import Custom_error


# logging
LOGGER = logging.getLogger("ss2-psql")
logging.basicConfig(
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", level=logging.INFO)

def get_last_ts():
    """Retrives a timestamp of the last observed notification."""

    LOGGER.info("Obtaining last timestamp ...")
    try:
        with open('lastts.txt', 'r') as f:
            lastts = f.read()
        LOGGER.info("Reading it from file ...")
    except Error:
        lastts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        LOGGER.error("No timestamp found, setting to current timestamp ({})...".format(lastts))
    return(lastts)

def write_last_ts(ts):
    """Writes the time of ts (last retrieved notification)"""

    with open('lastts.txt', 'w') as f:
        f.write(ts)

def get_last_notifications(lastts):
    """
    Connect to the PostgreSQL database server and retrieves all the
    notifications since last notification timestamp.
    """

    conn = None

    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        LOGGER.info('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        LOGGER.info('PostgreSQL fetch new')
        cur.execute('SELECT id, user_id, model_id, title, content, time FROM notifications WHERE time > \'{}\''.format(lastts))

        # display the PostgreSQL database server version
        rows = cur.fetchall()

        obj = []

        for row in rows:
            # convert tuple to a list for easier manipulation
            items = list(row)
            # to milliseconds
            items[5] = items[5].timestamp() * 1000
            obj.append({
                "id": items[0],
                "user_id": items[1],
                "model_id": items[2],
                "title": items[3],
                "content": items[4],
                "time": items[5]
            })

            # write last timestamp
            lastts = row[5].strftime("%Y-%m-%d %H:%M:%S.%f")

        # close the communication with the PostgreSQL
        cur.close()
        write_last_ts(lastts)

    except (Exception, psycopg2.DatabaseError) as error:
        LOGGER.error(error)
    finally:

        if conn is not None:
            conn.close()
            LOGGER.info('Database connection closed.')

    return obj

def postToFiware(data_model, entity_id, update):
    """Posts data model to the perscribed entity id"""

    global base_url
    global fiware_headers

    LOGGER.info(data_model)

    params = (
        ("options", "keyValues"),
    )
    if update:
        dm_type = data_model["type"]
        data_model.pop("type")

        # Try sending it to already existing entity (url)
        response = requests.post(base_url + entity_id + "/attrs/" , headers=fiware_headers, params=params, data=json.dumps(data_model) )

        # Otherwise add type and id and create new entity
        if response.status_code > 300:
            data_model["type"] = dm_type
            data_model["id"] = entity_id
            response = requests.post(base_url , headers=fiware_headers, params=params, data=json.dumps(data_model) )

    else:
        data_model["id"] = entity_id
        response = requests.post(base_url , headers=fiware_headers, params=params, data=json.dumps(data_model) )

    if (response.status_code > 300):
        raise Custom_error(f"Error sending to the API. Response stauts code: {response.status_code}")

def create_data_model(obj):
    """Create the data model to post to FIWARE API from the object obtained
    from the postgres."""
    data_model = copy.deepcopy(alert_template)

    # time to datetime
    time_stamp = datetime.datetime.utcfromtimestamp(obj["time"]/1000000)
    data_model["dateIssued"]["value"] = (time_stamp).isoformat() + ".00Z"
    title = obj["title"]
    content = obj["content"]

    data_model["description"]["value"] = f"Title: {title}, Content: {content}"

    # Sign and append signature
    data_model = sign(data_model)

    return data_model

def job():
    """Job for the scheduler, retrieving new notifications."""

    try:
        lastts = get_last_ts()
        objs = get_last_notifications(lastts)
        LOGGER.info("Data retrieved - size: %d", len(objs))
        # get last from the list
        if len(objs) > 0:

            # iterate through received objects
            for objs as obj:
                model_id = obj["model_id"]

                # PUT NAIADES FIWARE code here uzem sm zadnjega
                # Create data model to be sent
                data_model = create_data_model(obj)

                # Construct the entity (Alert) id TODO
                if (model_id in model_id_to_sensor):
                    entity_id = f"urn:ngsi-ld:Alert:RO-Braila-{model_id_to_sensor[model_id]}-state-analysis-tool"

                    # Try sending the FIWARE
                    try:
                        postToFiware(obj, entity_id, True)
                    except Exception as e:
                        LOGGER.error("Exception: %s", str(e))
                else:
                    LOGGER.info("The model is not interesting for the use case - model_id: %d", model_id)

    except Exception as e:
        LOGGER.info("Exception: %s", str(e))


def sign(data_model):
    # Try signing the message with KSI tool (requires execution in
    # the dedicated container)
    try:
        signature = self.encode(data_model)
    except Exception as e:
        LOGGER.info("Signing failed")
        signature = "null"

    # Add signature to the message
    data_model["ksiSignature"] = {
        "metadata": {},
        "type": "Text",
        "value": signature
    }

    return data_model

def encode(output_dict):
    global API_user
    global API_pass
    # Less prints
    debug = False

    # Transforms the JSON string ('dataJSON') to file (json.txt)
    os.system('echo %s > json.txt' %output_dict)
    #Sign the file using your credentials
    os.system(f'ksi sign -i json.txt -o json.txt.ksig -S http://5.53.108.232:8080 --aggr-user {API_user} --aggr-key {API_pass}')

    # get the signature
    with open("json.txt.ksig", "rb") as f:
        encodedZip = base64.b64encode(f.read())
        if debug:
            LOGGER.debug(encodedZip.decode())

    # Checking if the signature is correct
    verification = subprocess.check_output(f'ksi verify -i json.txt.ksig -f json.txt -d --dump G -X http://5.53.108.232:8081 --ext-user {self.API_user} --ext-key {self.API_pass} -P http://verify.guardtime.com/ksi-publications.bin --cnstr E=publications@guardtime.com | grep -xq "    OK: No verification errors." ; echo $?', shell=True)

    # Raise error if it is not correctly signed
    assert int(verification) == True

    return encodedZip

# definition of StreamStory2 models
model_id_to_sensor = {
    204: "211206H360",
    203: "211306H360",
    205: "318505H498"
}

if __name__ == '__main__':
    global base_url
    global fiware_headers
    global API_user
    global API_pass
    #Read FIWARE configuration
    with open("config/config.json") as configuration:
        conf = json.load(configuration)
        base_url = conf["base_url"]
        fiware_headers = conf["headers"]
        API_user = conf["API_user"]
        API_pass = conf["API_pass"]

    # scheduling each second (change to a more reasonable duration)
    # in production
    schedule.every(10).seconds.do(job)

    # infinite loop
    while True:
        schedule.run_pending()
        time.sleep(1)

def test():
    """
    A method only used for testing the uplaod """
    global base_url
    global fiware_headers
    global API_user
    global API_pass
    #Read FIWARE configuration
    with open("config/config.json") as configuration:
        conf = json.load(configuration)
        base_url = conf["base_url"]
        fiware_headers = conf["headers"]
        API_user = conf["API_user"]
        API_pass = conf["API_pass"]

    obj = {
        'id': 1,
        'user_id': 12,
        'model_id': 101,
        'title': 'Test alert',
        'content': 'Test content of the alert',
        'time': 1649931489368.622
    }

    data_model = create_data_model(obj)
    model_id = obj["model_id"]


    # Construct the entity (Alert) id
    entity_id = f"urn:ngsi-ld:Alert:RO-Braila-{model_id_to_sensor[model_id]}-state-analysis-tool"

    postToFiware(data_model, entity_id, True)
