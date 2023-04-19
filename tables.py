from flask_login import UserMixin
from sqlalchemy import (
    create_engine,
    Table,
    
    Column,
    Integer,
    String,
    Date,
    Time,
    Boolean,
    ForeignKey,
)

from sqlalchemy.ext.declarative import declarative_base


Base=declarative_base()

# Possibly any problem i might have with autoincrementing
# https://stackoverflow.com/questions/20848300/unable-to-create-autoincrementing-primary-key-with-flask-sqlalchemy



class Users(UserMixin ,Base):
    __tablename__="users"

    userId=Column("userId",Integer, primary_key=True)
    pref_name=Column("pref_name",String(36),)
    # profile_pic=Column("pref_name",String(36))
    email=Column("email",String(36),unique=True)
    password=Column("password",String(256))
    type=Column("type",String(36))
    badgesComplete=Column("badgesComplete",Integer)
    numAdded=Column("numAdded",Integer)
    numCompleted=Column("numCompleted",Integer)
    minTimeGap=Column("minTimeGap", Integer)
    dayStart=Column("dayStart",Time)
    dayEnd=Column("dayEnd",Time)

    def __init__(self,pref_name,email,password,type,badgesComplete,numAdded,numCompleted,minTimeGap,dayStart,dayEnd):
        
        self.pref_name=pref_name
        self.email=email
        self.password=password
        self.type=type
        self.badgesComplete=badgesComplete
        self.numAdded=numAdded
        self.numCompleted=numCompleted
        self.minTimeGap=minTimeGap
        self.dayStart=dayStart
        self.dayEnd=dayEnd

    def get_id(self):
        return str(self.userId)


class Events(Base):
    __tablename__="events"

    eventId=Column("eventId",Integer,primary_key=True)
    userId=Column("userId",Integer, ForeignKey('users.userId'))
    eventName=Column("eventName",String(36))
    dateId=Column("dateId",Integer, ForeignKey("dates.dateId"))
    startTime=Column("startTime",Time)
    endTime=Column("endTime",Time)
    
    def __init__(self,userId,eventName,dateId,startTime,endTime):
        self.userId=userId
        self.eventName=eventName
        self.dateId=dateId
        self.startTime=startTime
        self.endTime=endTime

   
class Dates(Base):
    __tablename__="dates"
    dateId=Column("dateId", Integer, primary_key=True)
    day=Column("day",String(36))
    month=Column("month",String(36))
    year=Column("year",String(36))
    date=Column("date",Date)
    def __init__(self,day,month,year,date):
        self.day=day
        self.month=month
        self.year=year
        self.date=date      

# class UnavailableTimes(Base):
#     __tablename__="unavailableTimes"

#     eventId=Column("eventId",Integer,primary_key=True)
#     userId=Column("userId",Integer)
#     eventName=Column("eventName",String(36))
#     dateId=Column("dateId",Integer)
#     startTime=Column("startTime",Time)
#     endTime=Column("endTime",Time)
    
#     def __init__(self,userId,eventName,dateId,startTime,endTime):
#         self.userId=userId
#         self.eventName=eventName
#         self.dateId=dateId
#         self.startTime=startTime
#         self.endTime=endTime


class Assignments(Base):
    __tablename__="assignments"
    assignmentId=Column("assignmentId",Integer,primary_key=True)
    userId=Column("userId",Integer, ForeignKey('users.userId'))
    assignmentName=Column("assignmentName",String(36))
    assignmentCourse=Column("assignmentCourse",String(36))
    assignmentType=Column("assignmentType",String(36))
    dueDate=Column("dueDate",Date)
    dueTime=Column("dueTime",Time)
    completed=Column('complete',Boolean)

    def __init__(self,userId,assignmentName,assignmentType, assignmentCourse, dueDate,dueTime):
        self.userId=userId
        self.assignmentName=assignmentName
        self.assignmentType=assignmentType
        self.assignmentCourse=assignmentCourse
        self.dueDate=dueDate
        self.dueTime=dueTime    
        self.completed=False

class Courses(Base):
    __tablename__="courses"
    courseId=Column("courseId",Integer,primary_key=True)
    userId=Column("userId",Integer, ForeignKey('users.userId'))
    courseName=Column("courseName",String(36))
    def __init__(self,userId,courseName):
        self.userId=userId
        self.courseName=courseName



class AssignmentIntervals(Base):
    __tablename__="assignmentIntervals"
    assignmentId=Column("assignmentId",Integer, ForeignKey('assignments.assignmentId'))
    userId=Column("userId",Integer, ForeignKey('users.userId'))
    sessionNum=Column("sessionNum",Integer,primary_key=True)
    dateId=Column("dateId",Integer, ForeignKey("dates.dateId"))
    startTime=Column("startTime",Time)
    endTime=Column("endTime",Time)
    def __init__(self,assignmentId, userId,dateId,startTime,endTime):
        self.assignmentId=assignmentId
        self.userId=userId
        self.dateId=dateId
        self.startTime=startTime
        self.endTime=endTime

class AssignmentTasks(Base):
    __tablename__="assignmentTasks"
    taskId=Column("taskId",Integer,primary_key=True)
    assignmentId=Column("assignmentId",Integer, ForeignKey('assignments.assignmentId'))
    taskName=Column("taskName",String(36))
    def __init__(self,assignmentId,taskName):
        self.assignmentId=assignmentId
        self.taskName=taskName

    

class UserBadges(Base):
    __tablename__="userBadges"
    userBadgeId=Column("userBadgeId", Integer, primary_key=True)
    userId=Column("userId",Integer, ForeignKey("users.userId"))
    dateReceived=Column("dateReceived",Date)
    badgeId=Column("badgeId",Integer, ForeignKey("badges.badgeId"))

    def __init__(self, dateReceived,badgeId):

        self.dateReceived=dateReceived
        self.badgeId=badgeId

class Badges(Base):
    __tablename__="badges"
    badgeId=Column("badgeId",Integer, primary_key=True)
    badgeName=Column("badgeName",String(36), unique=True)
    def __init__(self, badgeName):
        self.badgeName=badgeName


# Base.metadata.create_all(bind=engine)
