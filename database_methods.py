

from tables import Base
from sqlalchemy import ForeignKeyConstraint, create_engine
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql import asc, desc,func

from tables import (
    Base,
    Users,
    Assignments,
    AssignmentTasks,
    Courses,
    AssignmentIntervals,
    Events,
    Dates,
    Badges,
)



# ----------------------------------------------------------------------
# * UTILITY METHODS

def dangerous_reset_database(engine):
    assert engine is not None
    
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)



def create_table(engine):
    assert engine is not None
    Base.metadata.create_all(engine)

def create_session():
    db_url = "mysql+pymysql://root:kevincas0522@localhost/ScheduApp"
    engine = create_engine(db_url)
    # Session = sessionmaker(bind=engine)
    # return Session(), engine

    # create session and add objects
    # with sessionmaker(bind=engine)() as session:
    #     return session, engine

    # with create_engine(db_url) as engine:
    with sessionmaker(bind=engine)() as session:
        return session, engine



# ----------------------------------------------------------------------
# * QUERY METHODS
def get_user(dbSession, email):
    assert dbSession is not None
    return (
        dbSession.query(Users)
        .filter(Users.email == email)
        .first()
    )

def get_all_users(dbSession):
    assert dbSession is not None
    return (
        dbSession.query(Users)
        .order_by(Users.numAdded.desc())
        .all()
    )

def create_user(dbSession, name, email, password, type, minimumTimeGap, userStartDay, userEndDay):
    assert dbSession is not None
    user=Users(name,email,password,type,0,0,0,minimumTimeGap,userStartDay,userEndDay)

    dbSession.add(user)
    dbSession.commit()

    return user.userId
        




def create_assignment(dbSession,userId,name, type,course,dueDate,dueTime):
    assert dbSession is not None
    assignment = Assignments(userId,name, type,course,dueDate,dueTime)
    dbSession.add(assignment)
    dbSession.commit()

    update_user_added(dbSession,userId)
    return assignment

def get_assignments(dbSession, userId):
    assert dbSession is not None
    return (
        dbSession.query(Assignments)
        .filter(and_(Assignments.userId == userId,Assignments.completed==False))
        .order_by(Assignments.dueDate)
        .all()
    )

def get_assignments_by_method(dbSession,userId, method):
    assert dbSession is not None

    if method=="Course":
        return (
        dbSession.query(Assignments)
        .filter(and_(Assignments.userId == userId,Assignments.completed==False))
        .order_by(Assignments.assignmentCourse)
        .all()
    )
    elif method=="Due Date":
        return (
        dbSession.query(Assignments)
        .filter(and_(Assignments.userId == userId,Assignments.completed==False))
        .order_by(Assignments.dueDate)
        .all()
    )
    elif method=="Name":
        return (
        dbSession.query(Assignments)
        .filter(and_(Assignments.userId == userId,Assignments.completed==False))
        .order_by(Assignments.assignmentName)
        .all()
    )
    elif method=="Tag":
        return (
        dbSession.query(Assignments)
        .filter(and_(Assignments.userId == userId,Assignments.completed==False))
        .order_by(Assignments.assignmentType)
        .all()
    )

    return 

def get_assignment_by_id(dbSession, userId, assignmentId):
    assert dbSession is not None
    
    assignment= dbSession.query(Assignments).filter(and_(
                Assignments.userId == userId,
                Assignments.assignmentId==assignmentId
            )).first()
    return assignment

def get_assignments_by_date(dbSession, userId, date=None):
    assert dbSession is not None
    
    assignment= dbSession.query(Assignments).filter(and_(
                Assignments.userId == userId,
                Assignments.dueDate==date
            )).all()
    return assignment

def get_first_assignmentInterval(dbSession,userId,dateId):
    assert dbSession is not None
    event= dbSession.query(AssignmentIntervals).filter(and_(
            AssignmentIntervals.userId == userId,
            AssignmentIntervals.dateId==dateId
        )).first()
    return event

def get_first_assignmnent(dbSession,userId,date):
    assert dbSession is not None
    assignment= dbSession.query(Assignments).filter(and_(
            Assignments.userId == userId,
            Assignments.dueDate==date
        )).first()
    return assignment

def get_first_event(dbSession,userId,dateId):
    assert dbSession is not None
    event= dbSession.query(Events).filter(and_(
            Events.userId == userId,
            Events.dateId==dateId
        )).first()
    return event


def create_assignment_tasks(dbSession,assignmentId,taskInputs):
    assert dbSession is not None
    for task in taskInputs:
        newTask=AssignmentTasks(assignmentId,task)
        dbSession.add(newTask)
        dbSession.commit()

    return True

def get_assignment_tasks(dbSession,assignmentId):
    assert dbSession is not None

    return (
        dbSession.query(AssignmentTasks)
        .filter(AssignmentTasks.assignmentId == assignmentId)
        .all()
    )


def create_assignment_intervals(dbSession,assignmentId,userId,startingTimes, endingTimes,dates):
    
    for i in range(len(startingTimes)):

        dateId=get_date(dbSession,dates[i])

        if not dateId:
            dateStr=dates[i].strftime("%Y-%m-%d")
            dateSplit=dateStr.split("-")
            dateId=create_date(dbSession, dateSplit[2],dateSplit[1],dateSplit[0],dateStr)

        newInterval=AssignmentIntervals(assignmentId,userId,dateId.dateId,startingTimes[i],endingTimes[i])
        
        dbSession.add(newInterval)
        dbSession.commit()
        print(dates[i].strftime("%Y-%m-%d"),assignmentId,userId,dateId.dateId,startingTimes[i],endingTimes[i])



def get_assignment_intervals(dbSession,assignmentId,):

    return (
        dbSession.query(AssignmentIntervals).join(Dates)
        .filter(AssignmentIntervals.assignmentId == assignmentId)
        .order_by(Dates.date).all()
    )


def get_assignment_intervals_by_date(dbSession,userId,dateId):
    print("DateID:",dateId)
    return (
        dbSession.query(AssignmentIntervals)
        .filter(and_(
                AssignmentIntervals.userId == userId,
                AssignmentIntervals.dateId==dateId))
        .order_by(AssignmentIntervals.startTime).all()
    )

def create_course(dbSession,userId,courseName):
    assert dbSession is not None
    course=Courses(userId,courseName)
    dbSession.add(course)
    dbSession.commit()
    return course

def get_courses(dbSession,userId):
    assert dbSession is not None

    return (
        dbSession.query(Courses)
        .filter(Courses.userId == userId)
        .all()
    )


def create_date(dbSession,day,month,year,date):
    assert dbSession is not None
    date=Dates(day,month,year,date)
    dbSession.add(date)
    dbSession.commit()
    return date

def get_date_by_id(dbSession,dateId):
    assert dbSession is not None
    return (
        dbSession.query(Dates)
        .filter(Dates.dateId == dateId)
        .first()
    )

def get_date(dbSession,date):
    
    assert dbSession is not None
    return (
        dbSession.query(Dates)
        .filter(Dates.date == date)
        .first()
    )



def get_date_id(dbSession,year,month,day):
    assert dbSession is not None
    return (
        dbSession.query(Dates)
        .filter(Dates.year == year)
        .filter(Dates.month == month)
        .filter(Dates.day == day)
        .first()
    )


def create_event(dbSession,userId,name,dateId,startTime,endTime):
    assert dbSession is not None

    event=Events(userId,name,dateId,startTime,endTime)
    dbSession.add(event)
    dbSession.commit()
    return event

def get_events_by_date(dbSession,userId,dateId):
    assert dbSession is not None
    
    assignment= dbSession.query(Events).filter(and_(
                Events.userId == userId,
                Events.dateId==dateId
            )).all()
    return assignment

def get_events(dbSession,userId,dateId):
    assert dbSession is not None
    
    assignment= dbSession.query(Events).filter(and_(
                Events.userId == userId,
                Events.dateId==dateId

                # func.time_format(Events.startTime, '%H:%i').asc()
            )).order_by(func.time_format(Events.startTime, '%H:%i').asc(), func.time_format(Events.endTime, '%H:%i').asc()).all()
    return assignment


def update_user_added(dbSession, userId):
    assert dbSession is not None
    userC= (
        dbSession.query(Users)
        .filter(Users.userId == userId)
        .first()
    )
    userC.numAdded = userC.numAdded+1

def update_user_completed(dbSession, userId):
    assert dbSession is not None
    userC= (
        dbSession.query(Users)
        .filter(Users.userId == userId)
        .first()
    )
    userC.numCompleted = userC.numCompleted+1
    
    dbSession.commit()


def get_date_id(dbSession, day, month, year):
    dateId=dbSession.query(Dates).filter(Dates.day == day,Dates.year == year, Dates.month==month).one()
    return dateId

def get_assignments_for_day(dbSession, userId, day, month, year ):
    assert dbSession is not None
    dateId= get_date_id(dbSession, day, month, year)

    user=dbSession.query(AssignmentIntervals).filter(AssignmentIntervals.userID == userId,AssignmentIntervals.dateId==dateId)






    



# ----------------------------------------------------------------------
# * UPDATE METHODS

# PROFILE SETTINGS


# Used for testing of methods
# def main():
#     try:
#         session, engine = create_session()
#         print("Test session", session)
#         print("Test engine", engine)

#     finally:
#         session.close()
#         engine.dispose


# if __name__ == "__main__":
#     main()