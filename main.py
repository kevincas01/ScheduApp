from flask import Flask, render_template, jsonify,request, redirect, url_for,session
from flask_login import LoginManager,login_user,current_user,login_required, logout_user

from flask_sqlalchemy import SQLAlchemy

import pymysql

from passlib.hash import pbkdf2_sha256
import json
from database_methods import (
    create_session,
    get_user)
from flask.helpers import make_response

import pandas as pd
import re
from sqlalchemy import exc
from sql_database import make_engine

from database_methods import (
    create_assignment,
    create_assignment_intervals,
    create_assignment_tasks,
    create_course,
    create_event,
    create_date,
    create_table,
    create_user,
    dangerous_reset_database,
    get_all_users,
    get_assignment_by_id,
    get_assignments,
    get_assignments_by_date,
    get_assignments_by_method,
    get_assignment_intervals,
    get_assignment_intervals_by_date,
    get_first_assignmentInterval,
    get_assignment_tasks,
    get_events,
    get_events_by_date,
    get_first_assignmnent,
    get_first_event,
    get_courses,
    get_date,
    get_date_by_id,
    update_user_completed,

    
)
from tables import Users

from key import SECRET_KEY
import calendar
from datetime import datetime,date, timedelta
from dateutil.relativedelta import relativedelta


# from flask_mysqldb import MySQL
# import MySQLdb.cursors
# import re

app = Flask(__name__)
app.secret_key = SECRET_KEY
# MYSQL DATABASE
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://root:kevincas0522@localhost/ScheduApp'

# db=SQLAlchemy(app)

login=LoginManager(app)
login.init_app(app)

@login.unauthorized_handler
def unauthorized():
    # do stuff
     return redirect(url_for("login_page"))

dbSession, engine = create_session()
# dangerous_reset_database(engine)


@app.route("/")
def index():
    if "logged_in" in session:
        return redirect(url_for("assignments_page"))
        
    return render_template('landing.html')

@login.user_loader
def load_user(userId):
    return dbSession.query(Users).get(userId)
    

@app.route("/login",methods=["POST", "GET"])
def login_page():
# Check if "username" and "password" POST requests exist (user submitted form)
    
    if request.method == 'POST' and 'email' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
    
        user=get_user(dbSession,email)
        if user is None:

            msg="Incorrect Email/Password"
            return render_template('login.html',errorMsg=msg)
        # hash the password that we get from the form
        elif not pbkdf2_sha256.verify(password,user.password):
            msg="Incorrect Email/Password"
            return render_template('login.html',errorMsg=msg)
        else:
            login_user(user, remember=True)
            
            return redirect(url_for("assignments_page"))
        
    else:
        if current_user.is_authenticated:
            return redirect(url_for("assignments_page"))
        else:
            return render_template('login.html')
        


def changeTime(time):
    timeString = time.strftime("%I:%M %p")
    return timeString

def changeDate(date):
    dateObj=date.strftime("%m/%d/%Y")
    return dateObj

def stripDate(date):
    return date.split("-")
    

@app.route("/register",methods=["POST", "GET"])
def register_page():
    if request.method == 'POST' and 'name' in request.form:
        # Create variables for easy access
        name=request.form['name']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        if password!=password2:
            msg="*Passwords do not match* "
            return render_template('register.html',errorMsg=msg )
       
        user=get_user(dbSession,email)
        
        if user:
            msg="*User with this email already exists* "
            
            return render_template('register.html',errorMsg=msg )
        
        # this takes care of salting and number of derivations
        # 16 byte salt 

        hashPassword= pbkdf2_sha256.hash(password)

        minTimeGap=request.form['minTimeGap']
        timeStartDay=request.form['timeStartDay']
        timeEndDay=request.form['timeEndDay']
        userId=create_user(dbSession,name,email,hashPassword,"student",minTimeGap,timeStartDay,timeEndDay)

        # session["userId"]= userId
        
        return redirect(url_for("login_page"))
    else:
        return render_template('register.html')


@app.route("/update_complete",methods=["POST"])
@login_required
def update_completed_state():
    assignmentId=request.args.get("assignmentId")

    assignment=get_assignment_by_id(dbSession,current_user.userId, assignmentId)
    if assignment:
        assignment.completed=True
        update_user_completed(dbSession,current_user.userId)

    return json.dumps({'redirect': '/dashboard'})
   

@app.route("/dashboard")
@login_required
def dashboard_page():

    assignments=get_assignments(dbSession,current_user.userId)
    users=get_all_users(dbSession)


    count=1
    return render_template('dashboard.html', assignments=assignments,changeTime=changeTime,changeDate=changeDate,users=users)


@app.route("/assignments")
@login_required
def assignments_page():

    assignments=get_assignments(dbSession,current_user.userId)
    
    assignmentsHtml=generate_sorted_assignments_html(assignments)
    dateTd=datetime.today().date()
    


    return render_template('assignments.html', assignmentsHtml=assignmentsHtml)


@app.route("/sort_assignments")
@login_required
def sort_assignments():
    method=request.args.get('method')

    assignments=get_assignments_by_method(dbSession,current_user.userId,method)
    return generate_sorted_assignments_html(assignments)


def generate_sorted_assignments_html(assignments):
    html=""

    if not assignments:
        html+="<h1>You have no assignments added yet=(</h1>"
        return html
            
    html = ""

    for assignment in assignments:
        html += '<div class="row" style="width:100%" data-assignmentId="'+str(assignment.assignmentId)+'" data-toggle="modal" data-target="#assignment_modal">'
        
        html += '<div class="col-2 d-flex align-items-center justify-content-center" style="flex-direction: column;padding: 0;">'
        date=stripDate(assignment.dueDate.strftime("%Y-%m-%d"))
        html+='<div class="rounded-circle bg-primary" style="width: 50px; height: 50px; margin: 0; padding: 0;">'
        html+=monthsAbbr[int(date[1])-1]+"<br>" +date[2]+"<br>"
        html += '</div>'
        html += changeTime(assignment.dueTime)
        html += '</div>'

        html += '<div class="col-10">'

        html += '<div class="row ">'

        html += '<div class="col-md-7">'
        html += "<h3>"+assignment.assignmentName+"</h3>"
        html += '</div>'

        html+='<div class="col-md-5 ">'
        if assignment.assignmentCourse:
            html += "<h5>"+assignment.assignmentCourse+": "+assignment.assignmentType+"</h5>"
        else:
            html += "<h5>"+assignment.assignmentType+"</h5>"
        html += '</div>'

        html += '</div>'
        html += '</div>'

        html += '</div>'
        html+='<hr style="width:110%;background-color: rgba(0,0,0,0.5);margin: 5px;border-width: 2px;">'

    return html


@app.route('/showAssignment',methods=["GET"])
@login_required
def assignment_show():
    assignmentId=request.args.get('id')
    headerHtml=""

    intervalsHtml=""

    tasksHtml=""

    headerHtml += '<div class="row"  >'
        
    assignment=get_assignment_by_id(dbSession,current_user.userId,assignmentId)


    if not assignment:
        return "False"
    
    headerHtml += '<div class="col-3 d-flex align-items-center justify-content-center" style="flex-direction: column;padding: 0;">'
    date=stripDate(assignment.dueDate.strftime("%Y-%m-%d"))
    headerHtml+='<div class="rounded-circle text-center bg-primary" style="width: 50px; height: 50px; margin: 0; padding: 0;">'
    headerHtml+=monthsAbbr[int(date[1])-1]+"<br>" +date[2]+"<br>"
    headerHtml += '</div>'
    headerHtml += changeTime(assignment.dueTime)
    headerHtml += '</div>'

    headerHtml += '<div class="col-9">'

    headerHtml += '<div class="row ">'

    headerHtml += '<div class="col-8">'

    headerHtml += "<h3>"+assignment.assignmentName+"</h3>"
    headerHtml += '</div>'
    headerHtml += '<div class="col-4">'
    # headerHtml+='<button id="edit_profile"type="button" class="btn btn-primary" > <i class="bi bi-pencil-square"></i><br></button>'
          
    headerHtml += '</div>'
    headerHtml += '</div>'

    headerHtml += '<div class="row ">'
    headerHtml+='<div class="col-12 ">'
    if assignment.assignmentCourse:
        headerHtml += "<h5>"+assignment.assignmentCourse+": "+assignment.assignmentType+"</h5>"
    else:
        headerHtml += "<h5>"+assignment.assignmentType+"</h5>"
    headerHtml += '</div>'

    headerHtml += '</div>'

    headerHtml += '</div>'
    headerHtml += '</div>'

    headerHtml += '</div>'

    intervals=get_assignment_intervals(dbSession,assignmentId)
    if intervals:
        intervalsHtml += '<div class="row">'
        intervalsHtml += '<div class="col-12">'
        intervalsHtml+='<h5>Assignment Work Intervals</h5>'
        

        for interval in intervals:
            print(interval.dateId)
            intervalDate=get_date_by_id(dbSession,interval.dateId)
            print(intervalDate.date,intervalDate.dateId)
            intervalsHtml+='<div>'+changeDate(intervalDate.date)+"  "+changeTime(interval.startTime)+" - "+ changeTime(interval.endTime)+'<div>'
        
        intervalsHtml += '</div>'
        intervalsHtml += '</div>'
    
    
    tasks=get_assignment_tasks(dbSession,assignmentId)
       
    if tasks:
        tasksHtml += '<div class="row">'
        tasksHtml += '<div class="col-12">'
        tasksHtml+='<h5>Subtasks</h5>'
        tasksHtml += "<ul>"
        for task in tasks:
            tasksHtml += "<li>"+task.taskName+"</li>"
        tasksHtml += "</ul>"
        tasksHtml += '</div>'
        tasksHtml += '</div>'

    return json.dumps({"header":headerHtml,"intervals":intervalsHtml,"tasks":tasksHtml})

@app.route('/changeAssignment',methods=["GET"])
@login_required
def assignment_change():
    id=request.args.get('id')

@app.route('/getUnavailableTimes',methods=["GET"])
@login_required
def getUnavailableTimes():

    requestDate1=request.args.get("startDate")
    requestDate2=request.args.get("endDate")
    
    startDate= datetime.strptime(requestDate1, "%Y-%m-%d").date()

    dueDate=datetime.strptime(requestDate2, "%Y-%m-%d").date()
   
    datesInbetween=pd.date_range(startDate,dueDate, freq='D')
    html=""
    dates=[]
    freeTime=[]
    count=0
    for dateCur in datesInbetween:
        dateCurStr=dateCur.strftime("%Y-%m-%d")
        dateId=get_date(dbSession,dateCurStr)
        html+='<div class="row" style="width:100%">'

        html+='<div class="col-4" style="display: flex; align-items: center; justify-content: center;">'
        html+= changeDate(dateCur)
        html+='</div>'
        


        html+='<div class="col-4" style="display: flex; align-items: center; flex-direction:column;justify-content: center;padding:0px;">'
        if dateId:
            unavailableTimes=get_events(dbSession,current_user.userId,dateId.dateId)

            if unavailableTimes:

                prev_endingTime=current_user.dayStart
                for event in unavailableTimes:
                    
                    # print(event.eventName,changeTime(event.startTime),changeTime(event.endTime))
                    if event.startTime>prev_endingTime:

                       
                        html+='<div><span>'+ changeTime(prev_endingTime) +'</span>-<span>'+ changeTime(event.startTime) +'</span></div>'
                        # html+='<input style="width:100px" id="assignment_date_input"class="form-control form-control-sm" type="time" name="dueTime" value='+ str(prev_endingTime) +' required>'
                        # html+='<input style="width:100px" id="assignment_date_input"class="form-control form-control-sm" type="time" name="dueTime" value='+ str(event.startTime) +' required>'
                        
                    prev_endingTime=event.endTime

                if prev_endingTime < current_user.dayEnd:
                    html+='<div><span>'+ changeTime(prev_endingTime) +'</span>-<span>'+ changeTime(current_user.dayEnd) +'</span></div>'
                    
            else:
                # check if there are assignments for this day 
                html+="<div>Free Time ALL DAY</div>"
                # html+='<div style="display: flex; align-items: center;">'
                # html+='<input style="width:100px" id="assignment_date_input"class="form-control form-control-sm" type="time" name="dueTime" value='+ str(current_user.dayStart) +' required>'
                # html+='<input style="width:100px" id="assignment_date_input"class="form-control form-control-sm" type="time" name="dueTime" value='+ str(current_user.dayEnd) +' required>'
                # html+='</div>'
        else:
            # no assignments or events at all 
            html+="<div>Free Time ALL DAY</div>"

            # html+='<div style="display: flex; align-items: center;">'
            # html+='<input style="width:100px" id="assignment_date_input"class="form-control form-control-sm" type="time" name="dueTime" value='+ str(current_user.dayStart) +' required>'
            # html+='<input style="width:100px" id="assignment_date_input"class="form-control form-control-sm" type="time" name="dueTime" value='+ str(current_user.dayEnd) +' required>'
            # html+='</div>'



        html+='</div>'

        html+='<div class="col-4" style="display: flex; align-items: center; flex-direction: column;">'

        html+='Start Time<input style="width:100px" id="assignment_date_input"class="form-control form-control-sm" type="time" name="startingTime{}" value='.format(count)+ str(current_user.dayStart) +' required>'
        html+='End Time<input style="width:100px" id="assignment_date_input"class="form-control form-control-sm" type="time" name="endingTime{}" value='.format(count)+ str(current_user.dayEnd) +' required>'
        
        html+='</div>'
        count+=1
            

    
        html+='</div>'
        html+='<hr>'

    return html

# html+='<input style="width:100px" id="assignment_date_input"class="form-control form-control-sm" type="time" name="dueTime" value='+ str(prev_endingTime) +' required>'
# html+='<input style="width:100px" id="assignment_date_input"class="form-control form-control-sm" type="time" name="dueTime" value='+ str(event.startTime) +' required>'
                        
    

@app.route('/createAssignment',methods=["GET","POST"])
@login_required
def assignment_creation():
    if request.method == 'POST':
        name=request.form['assignmentName']
        dueDate=request.form['dueDate']
        dueTime=request.form['dueTime']
        type=request.form['assignmentType']
        course=request.form['courseName']

        assignment=create_assignment(dbSession,current_user.userId, name,type,course,dueDate,dueTime)

        # Making the dates column if it doesnt exist already
        dateObj=get_date(dbSession,dueDate)
        # If the date is not null
        if not dateObj:
            # add date to the database
            
            day=assignment.dueDate.day
            month=assignment.dueDate.month
            year=assignment.dueDate.year

            dateStr="{} {}, {}".format(months[month-1],day,year)

            dateObj=create_date(dbSession,day,month,year,dueDate)


        # Making the assignment tasks columns

        taskInputs = []
        startingTimeInputs=[]
        endingTimeInputs=[]
        for key in request.form:
            if key.startswith('taskInput'):
                taskInputs.append(request.form[key])
            elif key.startswith('startingTime'):
                startingTimeInputs.append(request.form[key])
            elif key.startswith('endingTime'):
                endingTimeInputs.append(request.form[key])


        create_assignment_tasks(dbSession,assignment.assignmentId,taskInputs)

        # requestDate=request.args.get("date")
        # dueDate=datetime.strptime(requestDate, "%Y-%m-%d").date()
    
        today = date.today()

        datesInbetween=pd.date_range(today,dateObj.date, freq='D')
        print(startingTimeInputs,endingTimeInputs,datesInbetween)
        create_assignment_intervals(dbSession,assignment.assignmentId,current_user.userId,startingTimeInputs, endingTimeInputs,datesInbetween)
        
        return redirect(url_for("assignments_page"))
    
    return redirect(url_for("assignments_page"))

# Implement asssignment completion
# on the check of a checkbox maybe, show a modal to ask if they are sure they finished an assignment
# asks them if they are sure

def generate_dates(start_date, end_date1, frequency, input_value):
    current_date=datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date=datetime.strptime(end_date1, "%Y-%m-%d").date()

    dates = []

    while current_date <= end_date:
        dates.append(current_date)
        if frequency == "days":
            current_date += timedelta(days=input_value)
        elif frequency == "weeks":
            current_date += timedelta(weeks=input_value)
        elif frequency == "months":
            
            current_date = current_date+relativedelta(months=input_value)
        elif frequency=="years":
            current_date = current_date+relativedelta(years=input_value)
    return dates

@app.route('/createEvent',methods=["POST"])
@login_required
def event_creation():
    if request.method == 'POST':
        name=request.form['eventName']
        eventDate=request.form['eventDate']
        startTime=request.form['startTime']
        endTime=request.form['endTime']
        repeatCheckbox=request.form.get('repeatCheckbox', 'off') 


        if repeatCheckbox!="off":
            repeatNum=int(request.form["repeatNum"])
            repeatType=request.form["repeatType"]
            repeatUntilDate=request.form["repeatUntilDate"]

            # Create all the events
            dates=generate_dates(eventDate, repeatUntilDate, repeatType, repeatNum)
            
            print("multiple events")

            print(dates)

            for date in dates:
                print(date)
                dateId=get_date(dbSession,date)

                if not dateId:
                    dateStr=date.strftime("%Y-%m-%d")
                    dateSplit=dateStr.split("-")
                    print(dateSplit)
                    dateId=create_date(dbSession, dateSplit[2],dateSplit[1],dateSplit[0],dateStr)
                
                create_event(dbSession,current_user.userId,name,dateId.dateId,startTime,endTime)

        else:
            # Only create the current event
            date=get_date(dbSession,eventDate)

            if not date:
                dateSplit=eventDate.split("-")
                date=create_date(dbSession, dateSplit[2],dateSplit[1],dateSplit[0],eventDate)
                
            create_event(dbSession,current_user.userId,name,date.dateId,startTime,endTime)


                

        # # Making the dates column if it doesnt exist already
        # date=get_date(dbSession,dueDate)
        # # If the date is not null
        # if not date:
        #     # add date to the database
            
        #     day=assignment.dueDate.day
        #     month=assignment.dueDate.month
        #     year=assignment.dueDate.year

        #     dateStr="{} {}, {}".format(months[month-1],day,year)

        #     date=create_date(dbSession,day,month,year,dueDate)
        # else:
        #     pass

        # Making the assignment tasks columns
        
        return redirect(url_for("schedule"))





@app.route('/add_course', methods=["POST"])
@login_required
def add_course_func():


    courseName = request.args.get('courseName')
    
    course=create_course(dbSession,current_user.userId,courseName)

    return "True"
    
@app.route('/get_course', methods=["GET"])
@login_required
def get_courses_func():

    courses=get_courses(dbSession,current_user.userId)
    
    html=""
    for course in courses:
        html+="<h2 data-dismiss='modal'>"+course.courseName+"</h2>"
        html+="<hr>"

    return html



def check_time_format(time_str):
    # Define a regular expression pattern for "XX:XX:XX" format
    pattern = r'^\d{2}:\d{2}:\d{2}$'
    
    match = re.match(pattern, time_str)
    
    return match


@app.route("/profile",methods=["GET"])
@login_required
def profile():
   
    # Given a UserId from the session, get the user information
    # pass it on to the render_template


    # UNLOCK DIFFERENT PROFILE PICTURES THAT THEY ARE ALLOWED TO CHOOSE FROM

    return render_template('profile.html',user=current_user,changeTime=changeTime)

@app.route("/edit_profile",methods=["POST"])
@login_required
def edit_profile():
    prefName=request.args.get('newName')
    newMinTime=request.args.get('newMinTime')
    newDayStart=request.args.get('newDayStart')
    newDayEnd=request.args.get('newDayEnd')
    
    user=get_user(dbSession,current_user.email)

    if prefName!=current_user.pref_name:
        user.pref_name=prefName
        dbSession.commit()


    if int(newMinTime)!=current_user.minTimeGap:
        user.minTimeGap=newMinTime
        dbSession.commit()
    

    if check_time_format(newDayStart) is None:
        user.dayStart=newDayStart
        dbSession.commit()
    if check_time_format(newDayEnd) is None:
    # if datetime.strptime(newDayEnd, "%H:%M:%S").time()!=current_user.dayEnd:
        user.dayEnd=newDayEnd
        dbSession.commit()

    return "True"


def generate_calendar_html(year, month,mode):
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(year, month)
    

    html = '<table class= "cal_table" id="days_table" style="width:100%; font-size:18px; table-layout:fixed;">'
    for week in cal:
        html += '<tr style="padding:0px">'
        for day in week:
            if day == 0:
                html += '<td style="text-align:center; width:14.3%;"></td>'
            else:
                dateInput=date(year,month,day)

                dateId=get_date(dbSession,dateInput)

                if mode=="assignments":

                    # Get first assignmentId to see if there is an asasignment for it 
                    assignment=get_first_assignmnent(dbSession,current_user.userId,dateInput)

                    assignmentInterval=None
                    if dateId:
                        assignmentInterval=get_first_assignmentInterval(dbSession,current_user.userId, dateId.dateId)

                    if assignment is not None or assignmentInterval is not None:
                        html += '<td class="calendar-day" data-day="{}" data-month="{}" data-year="{}" data-toggle="modal" data-target="#schedule_modal"> <div class="day-container"> <div class="day-top">{}</div> <div class="day-bottom " style="margin:auto;"> <div class="rounded-circle bg-primary" style="width: 20px; height: 20px;"></div> </div> </div> </td>'.format(day, month, year, day)
                    else:
                        html += '<td class="calendar-day" data-day="{}" data-month="{}" data-year="{}" data-toggle="modal" data-target="#schedule_modal"> <div class="day-container"> <div class="day-top">{}</div> </div> </td>'.format(day, month, year, day)
                
                else:
                    if dateId:
                        event=get_first_event(dbSession, current_user.userId, dateId.dateId)

                        if event is not None:
                            html += '<td class="calendar-day" data-day="{}" data-month="{}" data-year="{}" data-toggle="modal" data-target="#schedule_modal"> <div class="day-container"> <div class="day-top">{}</div> <div class="day-bottom " style="margin:auto;"> <div class="rounded-circle bg-primary" style="width: 20px; height: 20px;"></div> </div> </div> </td>'.format(day, month, year, day)
                        else:
                            html += '<td class="calendar-day" data-day="{}" data-month="{}" data-year="{}" data-toggle="modal" data-target="#schedule_modal"> <div class="day-container"> <div class="day-top">{}</div> </div> </td>'.format(day, month, year, day)
                    else:
                        html += '<td class="calendar-day" data-day="{}" data-month="{}" data-year="{}" data-toggle="modal" data-target="#schedule_modal"> <div class="day-container"> <div class="day-top">{}</div> </div> </td>'.format(day, month, year, day)
                    

                    # Get first unavailabel time to ssee if there is an event during that daay
                
                
        
        html += '</tr>'
    html += '</table>'
    if mode=="personal":
        html+='<button style="position:absolute;top:50px;right:25%"  type="button" class="btn btn-dark" data-toggle="modal" data-target="#event_modal">+</button>'
    return html



months = ["January", "February", "March", "April", "May", "June", "July","August", "September", "October", "November", "December"]
monthsAbbr=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul","Aug", "Sep", "Oct", "Nov", "Dec"]

@app.route("/schedule")
@login_required
def schedule():
    date_str = "2023-11-12"
    date_obj =datetime.strptime(date_str, "%Y-%m-%d").date()
    

    date=datetime.now()
    
    currYear = date.year
    currMonth = date.month
    
    htmll=generate_calendar_html(currYear,currMonth,"assignments")
    
    return render_template('schedule.html',calendar=htmll,currYear=currYear, currMonth=months[currMonth-1])

@app.route("/update_calendar")
@login_required
def update_calendar():
    # Get the year and month from the query parameters
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    mode = request.args.get('mode')
    # Generate the calendar HTML for the new year and month
    calendar_html = generate_calendar_html(year, month,mode)

    # Return the calendar HTML as a plain text response
    return calendar_html


def generate_modal_html(year,month,day,mode):

    html=''

    dateObj = date(year,month,day)
    dateCol=get_date(dbSession, dateObj)


    if dateCol:
        if mode=="assignments":


            assignmentsDue=get_assignments_by_date(dbSession,current_user.userId, dateCol.date)
            
            if assignmentsDue:
                html+='<h2 style="color:red;">Assignments Due<h2>'
            for assignmentDue in assignmentsDue:
                
                html+='<h3>'+assignmentDue.assignmentName+" </h3>"
                html+='<p>'+changeDate(assignmentDue.dueDate)+"   "+ changeTime(assignmentDue.dueTime)+"</p>"

                if assignmentDue.assignmentCourse:
                    html+="<h5>"+assignmentDue.assignmentCourse+":  "+assignmentDue.assignmentType+"</h5>"
                else:
                    html+="<h5>"+assignmentDue.assignmentType+"</h5>"

                tasks=get_assignment_tasks(dbSession,assignmentDue.assignmentId)

                html+="<ul>"
                for i in range(len(tasks)):
                    html+="<li>" +tasks[i].taskName+"</li>"
                    
                html+="</ul>"
            
            assignmentIntervals=get_assignment_intervals_by_date(dbSession, current_user.userId,dateCol.dateId)
            print(assignmentIntervals)
            if assignmentIntervals:
                html+='<h2 style="color:red;">Assignments to work on <h2>'
            for interval in assignmentIntervals:

                assignment=get_assignment_by_id(dbSession,current_user.userId,interval.assignmentId)

                html+='<h3>'+assignment.assignmentName+" </h3>"
                html+='<p>'+changeTime(interval.startTime)+"-"+changeTime(interval.endTime)+"</p>"

        else:

            events=get_events(dbSession,current_user.userId,dateCol.dateId)
            if events:
                html+='<h2 style="color:red;">Events<h2>'
            for event in events:
                html+='<h3>'+event.eventName+" </h3>"
                html+='<h5>'+changeTime(event.startTime)+"-"+changeTime(event.endTime)+"</h5>"



    # else:
    #     assignments=get_assignments_by_date(dbSession,current_user.userId, None)
    

    return html

@app.route("/update_modal")
@login_required
def update_modal():
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    day = int(request.args.get('day'))

    mode=request.args.get("mode")

    html=generate_modal_html(year,month,day,mode)

    return html


@app.route("/logout",methods=['GET'])
@login_required
def logout():
    session.clear()
    logout_user()
    
    return redirect(url_for("index"))

