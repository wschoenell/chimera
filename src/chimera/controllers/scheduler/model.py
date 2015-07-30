from chimera.core.constants import DEFAULT_PROGRAM_DATABASE

from sqlalchemy import (Column, String, Integer, DateTime, Boolean, ForeignKey,
                        Float, PickleType, MetaData, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relation, backref

engine = create_engine('sqlite:///%s' % DEFAULT_PROGRAM_DATABASE, echo=False)
metaData = MetaData()
metaData.bind = engine

Session = sessionmaker(bind=engine)
Base = declarative_base(metadata=metaData)

import datetime as dt

class Targets(Base):
    __tablename__ = "targets"

    id     = Column(Integer, primary_key=True)
    name   = Column(String, default="Program") 
    type   = Column(String, default=None) 
    lastObservation = Column(DateTime, default=None)
    observed  = Column(Boolean, default=False)
    scheduled  = Column(Boolean, default=False)
    targetRa = Column(Float, default=0.0)
    targetDec = Column(Float, default=0.0)
    targetEpoch = Column(Float, default=2000.)
    targetMag = Column(Float, default=0.0)
    magFilter = Column(String, default=None)

    def __str__ (self):
        if self.observed:
            return "#%d %s [type: %s] #LastObverved@: %s" % (self.id, self.name, self.type,
                                                        self.lastObservation)
        else:
            return "#%d %s [type: %s] #NeverObserved" % (self.id, self.name, self.type)

class Program(Base):
    __tablename__ = "program"

    id     = Column(Integer, primary_key=True)
    tid    = Column(Integer, ForeignKey('targets.id'))
    name   = Column(String, ForeignKey("targets.name"))
    pi     = Column(String, default="Anonymous Investigator")

    priority = Column(Integer, default=0)

    createdAt = Column(DateTime, default=dt.datetime.today())
    finished  = Column(Boolean, default=False)
    slewAt = Column(Float, default=0.0)
    exposeAt = Column(Float, default=0.0)
    
    actions   = relation("Action", backref=backref("program", order_by="Action.id"),
                         cascade="all, delete, delete-orphan")

    def __str__ (self):
        return "#%d %s pi:%s #actions: %d" % (self.id, self.name,
                                              self.pi, len(self.actions))

class Action(Base):

    id         = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey("program.id"))
    action_type = Column('type', String(100))


    __tablename__ = "action"
    __mapper_args__ = {'polymorphic_on': action_type}
    
class AutoFocus(Action):
    __tablename__ = "action_focus"
    __mapper_args__ = {'polymorphic_identity': 'AutoFocus'}

    id     = Column(Integer, ForeignKey('action.id'), primary_key=True)
    start   = Column(Integer, default=None)
    end     = Column(Integer, default=None)
    step    = Column(Integer, default=None)
    filter  = Column(String, default=None)
    exptime = Column(Float, default=1.0)
    binning = Column(String, default=None)
    window  = Column(String, default=None)

    def __str__ (self):
        return "autofocus: exptime=%s. Optionals: start=%s end=%s step=%s" % (self.exptime, self.end, self.step,
                                                                              self.start)
    
class PointVerify(Action):
    __tablename__ = "action_pv"
    __mapper_args__ = {'polymorphic_identity': 'PointVerify'}

    id     = Column(Integer, ForeignKey('action.id'), primary_key=True)
    here   = Column(Boolean, default=None)
    choose = Column(Boolean, default=None) 

    def __str__ (self):
        if self.choose is True:
            return "pointing verification: system defined field"
        elif self.here is True:
            return "pointing verification: current field"

class Point(Action):
    __tablename__ = "action_point"
    __mapper_args__ = {'polymorphic_identity': 'Point'}

    id          = Column(Integer, ForeignKey('action.id'), primary_key=True)
    targetRaDec = Column(PickleType, default=None)
    targetAltAz = Column(PickleType, default=None)
    targetName  = Column(String, default=None)

    def __str__ (self):
        if self.targetRaDec is not None:
            return "point: (ra,dec) %s" % self.targetRaDec
        elif self.targetAltAz is not None:
            return "point: (alt,az) %s" % self.targetAltAz
        elif self.targetName is not None:
            return "point: (object) %s" % self.targetName
    
class Expose(Action):
    __tablename__ = "action_expose"
    __mapper_args__ = {'polymorphic_identity': 'Expose'}

    id         = Column(Integer, ForeignKey('action.id'), primary_key=True)
    filter     = Column(String, default=None)
    frames     = Column(Integer, default=1)
    
    exptime    = Column(Integer, default=5)

    binning    = Column(Integer, default=None)
    window     = Column(Float, default=None)

    shutter    = Column(String, default="OPEN")
    
    imageType  = Column(String, default="")    
    filename   = Column(String, default="$DATE-$TIME")
    objectName = Column(String, default="")

    def __str__ (self):
        return "expose: exptime=%d frames=%d type=%s" % (self.exptime, self.frames, self.imageType)

###
    
#metaData.drop_all(engine)
metaData.create_all(engine)

