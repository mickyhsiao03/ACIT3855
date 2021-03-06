import connexion
from connexion import NoContent
import json
from datetime import datetime
import os
import os.path
from os import path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from dateRange import DateRange
from stockNumber import StockNumber
import yaml
import logging
import logging.config
import requests
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from sqlalchemy import and_
from datetime import datetime
from time import sleep

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine('mysql+pymysql://%s:%s@%s:%d/%s' % (app_config['datastore']['user'], app_config['datastore']['password'], app_config['datastore']['hostname'], app_config['datastore']['port'], app_config['datastore']['db']))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger = logging.getLogger('basicLogger')

def store_stock_number(body):
    """ Receives a stock info"""

    session = DB_SESSION()

    sn = StockNumber(body['investor_ID'],
                    body['price_Date'],
                    body['stock_Name'],
                    body['stock_Number'],
                    body['stock_Price'],
                    body['trace_id']
                    )

    session.add(sn)

    session.commit()
    session.close()

    logger.debug('Stored event stockNumber request with a trace id of: %s' % (body['trace_id']))

    return NoContent, 201

def store_date_range(body):
    """ Receives a data range info"""

    session = DB_SESSION()

    dr = DateRange(body['investor_ID'],
                    body['day'],
                    body['month'],
                    body['time'],
                    body['year'],
                    body['trace_id']
                    )

    session.add(dr)

    session.commit()
    session.close()

    logger.debug('Stored event dateRange request with a trace id of: %s' % (body['trace_id']))


    return NoContent, 201



def getStockNum(body):

    store_stock_number(body)

    return NoContent, 201

def getTimeFrame(body):  
    
    store_date_range(body)
    
    return NoContent, 201

def get_stock_number(timestamp, end_timestamp): 
    """ Gets new stock info after the timestamp """ 
 
    session = DB_SESSION() 
 
    timestamp_datetime = timestamp
    
    end_timestamp_datetime = end_timestamp
   
 
    readings = session.query(StockNumber).filter(
        and_(StockNumber.date_created >= timestamp_datetime,
        StockNumber.date_created < end_timestamp_datetime) )
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
        
 
    session.close() 
     
    logger.info("Query for stock number info after %s and before %s returns %d results" %  
                (timestamp, end_timestamp, len(results_list))) 

    
 
    return results_list, 200

def get_date_range(timestamp, end_timestamp): 
    """ Gets new date ranges after the timestamp """ 
 
    session = DB_SESSION() 
 
    timestamp_datetime = timestamp
    
    end_timestamp_datetime = end_timestamp
 
    readings = session.query(DateRange).filter(
        and_(DateRange.date_created >= timestamp_datetime,
        DateRange.date_created < end_timestamp_datetime) ) 
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
 
    session.close() 
     
    logger.info("Query for date ranges after %s and before %s returns %d results" %  
                (timestamp, end_timestamp, len(results_list))) 

 
    return results_list, 200



def process_messages(): 
    retry_count = 0
    """ Process event messages """ 
    hostname = "%s:%d" % (app_config["events"]["hostname"],   
                          app_config["events"]["port"]) 

    while retry_count < app_config["kafka_connect"]["retry_count"]:
        try:
            logger.info('trying to connect, attemp: %d' % (retry_count))
            print(hostname)
            client = KafkaClient(hosts=hostname) 
        except:
            logger.info('attempt %d failed, retry in 5 seoncds' % (retry_count))
            retry_count += 1
            sleep(app_config["kafka_connect"]["sleep_time"])
        else:
            break
    
    logger.info('connected to kafka')

    topic = client.topics[str.encode(app_config["events"]["topic"])] 
     
    # Create a consume on a consumer group, that only reads new messages  
    # (uncommitted messages) when the service re-starts (i.e., it doesn't  
    # read all the old messages from the history in the message queue). 
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', 
                                         reset_offset_on_start=False, 
                                         auto_offset_reset=OffsetType.LATEST) 
 
    # This is blocking - it will wait for a new message 
    for msg in consumer: 
        msg_str = msg.value.decode('utf-8') 
        msg = json.loads(msg_str) 
        logger.info("Message: %s" % msg) 
 
        payload = msg["payload"] 
 
        if msg["type"] == "stockNumber": # Change this to your event type 
            # Store the event1 (i.e., the payload) to the DB 
            store_stock_number(payload)
            logger.info('payload stored. msg type: %s, trace id: %s' % (msg['type'], payload['trace_id']))
        elif msg["type"] == "dateRange": # Change this to your event type 
            # Store the event2 (i.e., the payload) to the DB 
            store_date_range(payload)
            logger.info('payload stored. msg type: %s, trace_id: %s' % (msg['type'], payload['trace_id']))
        # Commit the new message as being read 
        consumer.commit_offsets()


def health():
    logger.info('Storage service is running')

    return NoContent, 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("acit3855micky-Stock_Prices-1.0.0-resolved.yaml", base_path="/storage", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages) 
    t1.setDaemon(True) 
    t1.start()
    app.run(port=8090)