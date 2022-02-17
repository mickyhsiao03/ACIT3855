from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class StockNumber(Base):
    """ Stock Number """

    __tablename__ = "stock_number"

    id = Column(Integer, primary_key=True)
    investor_ID = Column(String(250), nullable=False)
    price_Date = Column(String(100), nullable=False)
    stock_Name = Column(String(50), nullable=False)
    stock_Number = Column(String(10), nullable=False)
    stock_Price = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(100), nullable=False)
    

    def __init__(self, investor_ID, price_Date, stock_Name, stock_Number, stock_Price, trace_id):
        """ Initializes a stock number detail """
        self.investor_ID = investor_ID
        self.price_Date = price_Date
        self.stock_Name = stock_Name
        self.stock_Number = stock_Number
        self.stock_Price = stock_Price
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id
        
    def to_dict(self):
        """ Dictionary Representation of a stock number detail"""
        dict = {}
        dict['id'] = self.id
        dict['investor_ID'] = self.investor_ID
        dict['price_Date'] = self.price_Date
        dict['stock_Name'] = self.stock_Name
        dict['stock_Number'] = self.stock_Number
        dict['stock_Price'] = self.stock_Price
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
