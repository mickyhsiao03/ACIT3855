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
import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from health import Health as Health
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin


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



DB_ENGINE = create_engine("sqlite:///%s" % (app_config["datastore"]["filename"]))
Base.metadata.bind = DB_ENGINE 
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def create_tables():
    conn = sqlite3.connect('/data/health.sqlite') 
    
    c = conn.cursor() 
    c.execute(''' 
            CREATE TABLE IF NOT EXISTS health 
            (id INTEGER PRIMARY KEY ASC,  
            receiver VARCHAR(50) NOT NULL, 
            storage VARCHAR(50) NOT NULL, 
            processing VARCHAR(50) NOT NULL, 
            audit VARCHAR(50) NOT NULL, 
            last_updated VARCHAR(100) NOT NULL) 
            ''') 
    
    conn.commit() 
    conn.close()

if path.exists(app_config["datastore"]["filename"]):
    create_tables()
    print('created db')

def populate():
    logger.info('periodic health check started.')
    session = DB_SESSION() 

    readings = session.query(Health)
    read_list = [] 
 
    for reading in readings: 
        read_list.append(reading.to_dict()) 
    
    current_timestamp = datetime.strptime(str(datetime.now()),"%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S.%f") 

    # if len(read_list) == 0:
    #     timestamp = current_timestamp

    # else:
    #     timestamp = datetime.strptime(read_list[len(read_list)-1]['last_updated'], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S.%f")


    #get data from storage service
    headers = {"content-type": "application/json"}
    receiver_response = requests.get(app_config['receiverHealth']['url'], headers=headers, timeout=5)
    storage_response = requests.get(app_config['storageHealth']['url'], headers=headers, timeout=5)
    processing_response = requests.get(app_config['processingHealth']['url'], headers=headers, timeout=5)
    audit_response = requests.get(app_config['auditHealth']['url'], headers=headers, timeout=5)


    if receiver_response.status_code == 200:
        receiver_status = 'Running'
        logger.debug('Receiver running')
    else:
        receiver_status = 'Down'
        logger.debug('Receiver down')

    if storage_response.status_code == 200:
        storage_status = 'Running'
        logger.debug('Storage running')
    else:
        storage_status = 'Down'
        logger.debug('Storage Down')

    if processing_response.status_code == 200:
        processing_status = 'Running'
        logger.debug('Processing running')
    else:
        processing_status = 'Down'
        logger.debug('Processing down')
        
    if audit_response.status_code == 200:
        audit_status = 'Running'
        logger.debug('Audit running')
    else:
        audit_status = 'Down'
        logger.debug('Audit down')


    
    #input into SQLite
    results_list= Health(receiver_status, 
                storage_status, 
                processing_status, 
                audit_status, 
                current_timestamp) 
    session.add(results_list)  
    session.commit() 
    session.close()
    
    logger.debug('updated this period: receiver status: %s, storage status: %s, processing status: %s, audit status: %s' 
    % (receiver_status, storage_status, processing_response, audit_status))
    logger.debug('periodic health check ended')

    return NoContent, 200

def get_health():
    logger.info('get health status started')

    session = DB_SESSION() 

    readings = session.query(Health)
    read_list = [] 

    if not readings:
        return NoContent, 404

    for reading in readings: 
        read_list.append(reading.to_dict())


    latest = read_list[len(read_list)-1]
 
    pydict = {'receiver': latest['receiver'], 'storage': latest['storage'],
    'processing': latest['processing'], 'audit': latest['audit'], 'last_updated': latest['last_updated']
    }

    logger.debug(pydict)
    logger.info('get health completed')
        
 
    session.close() 
    return pydict, 200

def init_scheduler(): 
    sched = BackgroundScheduler(daemon=True) 
    sched.add_job(populate,    
                  'interval', 
                  seconds=app_config['scheduler']['period_sec']) 
    sched.start()

def health():
    logger.info('Processing service is running')

    return NoContent, 200

app = connexion.FlaskApp(__name__, specification_dir='')

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] == "test":
    CORS(app.app) 
    app.app.config['CORS_HEADERS'] = 'Content-Type' 
    

app.add_api("healthApi.yml", base_path="/health", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
        init_scheduler()
        app.run(port=8300)
