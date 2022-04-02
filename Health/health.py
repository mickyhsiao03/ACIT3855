from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime 
from base import Base 
class Health(Base): 
    """ Processing health """ 
 
    __tablename__ = "health" 
 
    id = Column(Integer, primary_key=True) 
    receiver = Column(String, nullable=False) 
    storage = Column(String, nullable=False)
    processing = Column(String, nullable=False) 
    audit = Column(String, nullable=False)
    last_updated = Column(String, nullable=False)
 
    def __init__(self, receiver, storage, processing, audit ,last_updated): 
        """ Initializes a processing health objet """ 
        self.receiver = receiver
        self.storage = storage
        self.processing = processing
        self.audit = audit
        self.last_updated = last_updated 
 
    def to_dict(self): 
        """ Dictionary Representation of health """ 
        dict = {} 
        dict['receiver'] = self.receiver
        dict['storage'] = self.storage
        dict['processing'] = self.processing
        dict['audit'] = self.audit
        dict['last_updated'] = self.last_updated
 
        return dict
