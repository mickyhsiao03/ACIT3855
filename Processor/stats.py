from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime 
from base import Base 
class Stats(Base): 
    """ Processing Statistics """ 
 
    __tablename__ = "stats" 
 
    id = Column(Integer, primary_key=True) 
    num_stock = Column(Integer, nullable=True) 
    num_dRange = Column(Integer, nullable=True) 
    top_stock_price = Column(Integer, nullable=False) 
    top_stock_number = Column(String, nullable=False) 
    top_stock_name = Column(String, nullable=False)
    last_updated = Column(String, nullable=False)
 
    def __init__(self, num_stock, num_dRange, top_stock_price, top_stock_number, top_stock_name ,last_updated): 
        """ Initializes a processing statistics objet """ 
        self.num_stock = num_stock 
        self.num_dRange = num_dRange
        self.top_stock_price = top_stock_price
        self.top_stock_number = top_stock_number
        self.top_stock_name = top_stock_name
        self.last_updated = last_updated 
 
    def to_dict(self): 
        """ Dictionary Representation of a statistics """ 
        dict = {} 
        dict['num_stock'] = self.num_stock
        dict['num_dRange'] = self.num_dRange
        dict['top_stock_price'] = self.top_stock_price
        dict['top_stock_number'] = self.top_stock_number
        dict['top_stock_name'] = self.top_stock_name
        dict['last_updated'] = self.last_updated
 
        return dict
