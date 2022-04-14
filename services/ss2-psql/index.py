#!/usr/bin/python
import psycopg2
from config import config
import json
import datetime, time
import schedule

def get_last_ts():
    """Retrives a timestamp of the last observed notification."""

    print("Obtaining last timestamp ...")
    try:
        with open('lastts.txt', 'r') as f:
            lastts = f.read()
        print("Reading it from file ...")
    except Error:
        lastts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print("No timestamp found, setting to current timestamp ({})...".format(lastts))
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
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL fetch new')
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
        print(error)
    finally:

        if conn is not None:
            conn.close()
            print('Database connection closed.')

    return obj

def job():
    """Job for the scheduler, retrieving new notifications."""

    lastts = get_last_ts()
    obj = get_last_notifications(lastts)

    # PUT NAIADES FIWARE code here
    print(obj)

if __name__ == '__main__':
    # scheduling each second (change to a more reasonable duration)
    # in production
    schedule.every(1).seconds.do(job)

    # infinite loop
    while True:
        schedule.run_pending()
        time.sleep(1)