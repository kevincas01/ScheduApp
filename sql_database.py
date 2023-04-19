import mysql.connector

from sqlalchemy import create_engine


#MAKE LOCAL DATABASE
def make_db():

    myDatabase= mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="kevincas0522",
    )

    cursor=myDatabase.cursor()
    cursor.execute("CREATE DATABASE ScheduApp")
    cursor.execute("SHOW DATABASES")

def make_engine():
    return create_engine("mysql+pymysql://root:kevincas0522@localhost/ScheduApp")





#https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_quick_guide.htm