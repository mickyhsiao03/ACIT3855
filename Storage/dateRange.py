from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class DateRange(Base):
    """ Date Range """

    __tablename__ = "date_range"

    id = Column(Integer, primary_key=True)
    investor_ID = Column(String(250), nullable=False)
    day = Column(Integer, nullable=False)
    month = Column(String(15), nullable=False)
    time = Column(String(50), nullable=False)
    year = Column(String(5), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(100), nullable=False)

    

    def __init__(self, investor_ID, day, month, time, year, trace_id):
        """ Initializes a date range """
        self.investor_ID = investor_ID
        self.day = day
        self.month = month
        self.time = time
        self.year = year
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id
        

    def to_dict(self):
        """ Dictionary Representation of a heart rate reading """
        dict = {}
        dict['investor_ID'] = self.investor_ID
        dict['day'] = self.day
        dict['month'] = self.month
        dict['time'] = self.time
        dict['year'] = self.year
        dict['trace_id'] = self.trace_id

        return dict
