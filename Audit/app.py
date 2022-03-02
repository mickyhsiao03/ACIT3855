import connexion
from connexion import NoContent
import json
from datetime import date, datetime
import os
import os.path
from os import path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml
import logging
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from flask_cors import CORS, cross_origin

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

def get_stock_number_Q(index): 
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
 
    # Here we reset the offset on start so that we retrieve 
    # messages at the beginning of the message queue.  
    # To prevent the for loop from blocking, we set the timeout to 
    # 100ms. There is a risk that this loop never stops if the 
    # index is large and messages are constantly being received! 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,  
                                         consumer_timeout_ms=1000) 
 
    logger.info("Retrieving stock info at index %d" % index) 
    try: 
        stockList = []

        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 
            if msg['type'] == 'stockNumber':
                stockList.append(msg)
            
        logger.info('returned payload with trace_id: %s' % (stockList[index]['payload']['trace_id']))
   
            # Find the event at the index you want and  
            # return code 200 
            # i.e., return event, 200 
        return stockList[index], 200
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find BP at index %d" % index) 
    return { "message": "Not Found"}, 404

def get_date_range_Q(index): 
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
 
    # Here we reset the offset on start so that we retrieve 
    # messages at the beginning of the message queue.  
    # To prevent the for loop from blocking, we set the timeout to 
    # 100ms. There is a risk that this loop never stops if the 
    # index is large and messages are constantly being received! 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,  
                                         consumer_timeout_ms=1000) 
 
    logger.info("Retrieving date range at index %d" % index) 
    try: 
        dateList =[]
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 
            if msg['type'] == 'dateRange':
                dateList.append(msg)
        logger.info('returned payload with trace_id: %s' % (dateList[index]['payload']['trace_id']))
            # Find the event at the index you want and  
            # return code 200 
            # i.e., return event, 200 
        return dateList[index], 200
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find BP at index %d" % index) 
    return { "message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app) 
app.app.config['CORS_HEADERS'] = 'Content-Type' 
app.add_api("auditAPI.yaml", strict_validation=True, validate_responses=True)
if __name__ == "__main__":
        app.run(port=8200)