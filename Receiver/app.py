import connexion
from connexion import NoContent
import json
from datetime import datetime
import os
import os.path
from os import path
import requests
import yaml
import logging
import logging.config
import uuid
from pykafka import KafkaClient
from time import sleep

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

retry_count = 0
""" Process event messages """ 
hostname = "%s:%d" % (app_config["events"]["hostname"],   
                        app_config["events"]["port"]) 

while retry_count < app_config["kafka_connect"]["retry_count"]:
    try:
        logger.info('trying to connect, attemp: %d' % (retry_count))
        client = KafkaClient(hosts=hostname) 
    except:
        logger.info('attempt %d failed, retry in 5 seoncds' % (retry_count))
        retry_count += 1
        sleep(app_config["kafka_connect"]["sleep_time"])
    else:
        break

logger.info('connected to kafka')

def getStockNum(body):
    transID = str(uuid.uuid4())
    body['trace_id'] = transID
    
    content = "Received event: post stockNumber request with a trace id of: " + transID

    logger.info(content)

      
    # client = KafkaClient(hosts='%s:%s' % (app_config['events']['hostname'], app_config['events']['port'])) 
    topic = client.topics[str.encode(app_config['events']['topic'])] 
    producer = topic.get_sync_producer() 
    
    msg = { "type": "stockNumber",  
            "datetime" :    
            datetime.now().strftime( 
                "%Y-%m-%dT%H:%M:%S"),  
            "payload": body } 
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8'))

    logger.info('Returned event: post stockNumber response: ' + transID + ' with status code: 201') 

    
    return NoContent, 201

def getTimeFrame(body):  
    transID = str(uuid.uuid4())
    body['trace_id'] = transID
    content = "Received event: post dateRange request with a trace id of: " + transID

    logger.info(content)

      
    # client = KafkaClient(hosts='%s:%s' % (app_config['events']['hostname'], app_config['events']['port'])) 
    topic = client.topics[str.encode(app_config['events']['topic'])] 
    producer = topic.get_sync_producer() 
    
    msg = { "type": "dateRange",  
            "datetime" :    
            datetime.now().strftime( 
                "%Y-%m-%dT%H:%M:%S"),  
            "payload": body } 
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8'))
    logger.info('Returned event: post dateRange response: ' + transID + ' with status code: 201') 

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("acit3855micky-Stock_Prices-1.0.0-resolved.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
        app.run(port=8080)