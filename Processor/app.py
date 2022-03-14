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
from stats import Stats as Stats
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin

with open('./app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine("sqlite:///%s" % (app_config["datastore"]["filename"]))
Base.metadata.bind = DB_ENGINE 
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def populate():
    logger.info('periodic processing started.')
    session = DB_SESSION() 

    readings = session.query(Stats)
    read_list = [] 
 
    for reading in readings: 
        read_list.append(reading.to_dict()) 
    
    current_timestamp = datetime.strptime(str(datetime.now()),"%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S.%f") 

    if len(read_list) == 0:
        timestamp = current_timestamp

    else:
        timestamp = datetime.strptime(read_list[len(read_list)-1]['last_updated'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S.%f")


    #get data from storage service
    headers = {"content-type": "application/json"}
    stock_response = requests.get(app_config['eventstore']['url']+timestamp+"&end_timestamp="+current_timestamp, headers=headers)
    dRange_response = requests.get(app_config['eventstore2']['url']+timestamp+"&end_timestamp="+current_timestamp, headers=headers)

    if stock_response.status_code != 200:
        logger.debug('Did not get response from stockNumber')
    if dRange_response.status_code != 200:
        logger.debug('Did not get response from dateRange')

    stock_received = stock_response.json()
    dRange_received = dRange_response.json()

    logger.info('received %d stockNumber response' % (len(stock_received)))
    logger.info('received %d dateRange response' % (len(dRange_received)))

    if not stock_received and not dRange_received:
        readings = session.query(Stats)
        read_list = [] 
    
        for reading in readings: 
            read_list.append(reading.to_dict())

        if len(read_list) == 0:
            results_list= Stats(0, 0, 0, "", "", current_timestamp)
            session.add(results_list) 
            session.commit() 
            session.close()
            logger.debug('nothing added, last_updated updated, ending periodic processing')
        else:
            latest = read_list[len(read_list)-1]

            results_list= Stats(latest['num_stock'], 
                        latest['num_dRange'], 
                        latest['top_stock_price'], 
                        latest['top_stock_number'], 
                        latest['top_stock_name'], 
                        current_timestamp) 
            session.add(results_list) 
            session.commit() 
            session.close()
            logger.debug('nothing added, last_updated updated, ending periodic processing')
        return NoContent, 200

    else:
        #get number of events
        num_stock = len(stock_received)
        num_dRange = len(dRange_received)

        #get top stock price, stock number, name
        top_stock_price = []

        if num_stock == 0:
            for i in dRange_received:
                logger.debug('dateRange response processed, trace_id: %s' % (i['trace_id']))

            readings = session.query(Stats)
            read_list = [] 
        
            for reading in readings: 
                read_list.append(reading.to_dict())

            latest = read_list[len(read_list)-1]
            
            #input into SQLite
            results_list= Stats(latest['num_stock']+num_stock, 
                        latest['num_dRange']+num_dRange, 
                        latest['top_stock_price'], 
                        latest['top_stock_number'], 
                        latest['top_stock_name'], 
                        current_timestamp) 
            session.add(results_list)  
            session.commit() 
            session.close()
            
            logger.debug('updated this period: number of stockNumber response: %d, number of dateRange response: %d, top stock price: %d, stock name: %s, stock number: %s' 
            % (num_stock, num_dRange, latest['top_stock_price'], latest['top_stock_name'], latest['top_stock_number']))
            logger.debug('periodic processing ended')
            return NoContent, 200

        else:
            for i in stock_received:
                top_stock_price.append(i['stock_Price'])
                logger.debug('stockNumber response processed, trace_id: %s' % (i['trace_id']))
                for price in top_stock_price:
                    if price == i['stock_Price']:
                        top_stock_name = i['stock_Name']
                        top_stock_number = i['stock_Number']
            top_stock_price.sort(reverse=True)

            for i in dRange_received:
                logger.debug('dateRange response processed, trace_id: %s' % (i['trace_id']))

            readings = session.query(Stats)
            read_list = [] 
        
            for reading in readings: 
                read_list.append(reading.to_dict())

            latest = read_list[len(read_list)-1]
            
            #input into SQLite
            results_list= Stats(latest['num_stock']+num_stock, 
                        latest['num_dRange']+num_dRange, 
                        top_stock_price[0], 
                        top_stock_number, 
                        top_stock_name, 
                        current_timestamp) 
            session.add(results_list)  
            session.commit() 
            session.close()
            
            logger.debug('updated this period: number of stockNumber response: %d, number of dateRange response: %d, top stock price: %d, stock name: %s, stock number: %s' 
            % (num_stock, num_dRange, top_stock_price[0], top_stock_name, top_stock_number))
            logger.debug('periodic processing ended')

    return NoContent, 200

def get_stats():
    logger.info('get stats started')

    session = DB_SESSION() 

    readings = session.query(Stats)
    read_list = [] 

    if not readings:
        return NoContent, 404

    for reading in readings: 
        read_list.append(reading.to_dict())


    latest = read_list[len(read_list)-1]
 
    pydict = {'num_stock': latest['num_stock'], 'num_dRange': latest['num_dRange'],
    'top_stock_price': latest['top_stock_price'], 'stock_name': latest['top_stock_name'], 'stock_number': latest['top_stock_number']
    }

    logger.debug(pydict)
    logger.info('get stats completed')
        
 
    session.close() 
    return pydict, 200

def init_scheduler(): 
    sched = BackgroundScheduler(daemon=True) 
    sched.add_job(populate,    
                  'interval', 
                  seconds=app_config['scheduler']['period_sec']) 
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app) 
app.app.config['CORS_HEADERS'] = 'Content-Type' 
app.add_api("acit3855micky-Stock_Prices-1.0.0-resolved.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
        init_scheduler()
        app.run(port=8100)
