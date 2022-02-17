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
import create_database_mysql
import yaml
import logging
import logging.config
import requests

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

DB_ENGINE = create_engine('mysql+pymysql://%s:%s@%s:%d/%s' % (app_config['datastore']['user'], app_config['datastore']['password'], app_config['datastore']['hostname'], app_config['datastore']['port'], app_config['datastore']['db']))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger = logging.getLogger('basicLogger')

logger.info('Connecting to DB. Hostname: %s, Port number: %d' % (app_config['datastore']['hostname'], app_config['datastore']['port']))

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

def get_stock_number(timestamp): 
    """ Gets new stock info after the timestamp """ 
 
    session = DB_SESSION() 
 
    timestamp_datetime = timestamp 
   
 
    readings = session.query(StockNumber).filter(StockNumber.date_created >= timestamp_datetime) 
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
        
 
    session.close() 
     
    logger.info("Query for stock number info after %s returns %d results" %  
                (timestamp, len(results_list))) 

    
 
    return results_list, 200

def get_date_range(timestamp): 
    """ Gets new date ranges after the timestamp """ 
 
    session = DB_SESSION() 
 
    timestamp_datetime = timestamp
   
 
    readings = session.query(DateRange).filter(DateRange.date_created >= timestamp_datetime) 
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
 
    session.close() 
     
    logger.info("Query for date ranges after %s returns %d results" %  
                (timestamp, len(results_list))) 

 
    return results_list, 200



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("acit3855micky-Stock_Prices-1.0.0-resolved.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
        
        app.run(port=8090)