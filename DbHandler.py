import csv
import psycopg2


class DbHandler:

    def __init__(self, hostname, username, password, dbname):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.dbname = dbname
        self.myConnection = psycopg2.connect(host=hostname, user=username, password=password, dbname=dbname)

    def closeCon(self):
        self.myConnection.close()

    def doQuery(self, query):
        cur = self.myConnection.cursor()
        cur.execute( query )
        return cur.fetchall()
