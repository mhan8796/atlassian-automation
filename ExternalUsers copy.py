from CrowdHandler import CrowdHandler
from DbHandler import DbHandler
from progressbar import ProgressBar
from datetime import datetime
import csv
import configparser

class ExternalUsers:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini') # Change this in the server!


    # Get external users' info from crowd through API and
    # write it together with Jira last login, confluence last login, and user created date to csv
    def externalUserstoCSV(self,jiraLastLogin,confluLastLogin,userCreated):
        # Get parameters
        crowdUrl = self.config['legacy_crowd_prod']['url']
        crowdUsername = self.config['legacy_crowd_prod']['username']
        crowdPassword = self.config['legacy_crowd_prod']['password']
        # Initialize Crowd Handler
        ch = CrowdHandler(crowdUsername,crowdPassword,crowdUrl)
        current_time = datetime.now().strftime('%Y-%m-%d')
        w = csv.writer(open('out/external_user('+current_time+').csv','w'))
        w.writerow(['name','email','active','lastAuthenticated','groups','jiraLastLogin','confluenceLastLogin','createdDate'])
        print('Start to get external users...')
        externalUserInfoList = ch.getExternalUserInfo()
        print ('Done getting external users, start to write file...')
        pbar = ProgressBar()
        for userInfo in pbar(externalUserInfoList):
            name = userInfo.get('name')
            email = userInfo.get('email')
            active = userInfo.get('active')
            attribute = ch.getAttrifromUsernames([name])[0]
            lastAuthenticated = attribute.get('lastAuthenticated')
            groups = ch.getGroupsfromUsernames([name])[0].get('groups')
            groupstr = ', '.join(groups)
            w.writerow([name,email,active,lastAuthenticated,groupstr,jiraLastLogin.get(name),confluLastLogin.get(name),userCreated.get(name)])

    # Get users last login time from jira database and return a dictionary and write to csv
    def getJiraLastLogin(self):
        # Get parameters
        jiraDbUrl = self.config['legacy_jira_db']['url']
        jiraDbUsername = self.config['legacy_jira_db']['username']
        jiraDbPassword = self.config['legacy_jira_db']['password']
        jiraDbname = self.config['legacy_jira_db']['db_name']

        dh = DbHandler(jiraDbUrl,jiraDbUsername,jiraDbPassword,jiraDbname)

        query = '''
        SELECT cu.user_name, cu.email_address, to_timestamp(CAST(cua.attribute_value AS BIGINT)/1000) AS "Last Login"
        FROM cwd_user_attributes cua
        LEFT JOIN cwd_user cu ON cua.user_id=cu.id
        WHERE cua.attribute_name='login.lastLoginMillis'
        '''

        jiraLastLogin = {}
        results = dh.doQuery(query)
        w = csv.writer(open('out/jiraLastLogin.csv','w'))
        w.writerow(['name','email','jiraLastLogin'])
        for name,email,time in results:
            if time:
                w.writerow([name,email,time.strftime('%Y-%m-%d %H:%M:%S')])
                jiraLastLogin[name] = time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                w.writerow([name,email,time])
                jiraLastLogin[name] = time
        dh.closeCon()
        return jiraLastLogin

    # Get users last login time from confluence database and return a dictionary and write to csv
    def getConfluLastLogin(self):
        # Get parameters
        confluenceDbUrl = self.config['legacy_confluence_db']['url']
        confluenceDbUsername = self.config['legacy_confluence_db']['username']
        confluenceDbPassword = self.config['legacy_confluence_db']['password']
        confluenceDbname = self.config['legacy_confluence_db']['db_name']

        dh = DbHandler(confluenceDbUrl,confluenceDbUsername,confluenceDbPassword,confluenceDbname)

        query = '''
        SELECT cu.user_name, li.SUCCESSDATE
        FROM LOGININFO li
        JOIN user_mapping um ON um.user_key = li.USERNAME
        JOIN CWD_USER cu ON um.username = cu.USER_NAME
        '''

        confluLastLogin = {}
        results = dh.doQuery(query)
        w = csv.writer(open('out/ConfluLastLogin.csv','w'))
        w.writerow(['name','ConfluLastLogin'])
        for name,time in results:
            if(time):
                w.writerow([name,time.strftime('%Y-%m-%d %H:%M:%S')])
                confluLastLogin[name] = time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                w.writerow([name,time])
                confluLastLogin[name] = time
        dh.closeCon()
        return confluLastLogin

    # Get users created time from crowd database and return a dictionary and write to csv
    def getUserCreated(self):
        # Get parameters
        crowdDbUrl = self.config['legacy_crowd_db']['url']
        crowdDbUsername = self.config['legacy_crowd_db']['username']
        crowdDbPassword = self.config['legacy_crowd_db']['password']
        crowdDbname = self.config['legacy_crowd_db']['db_name']

        dh = DbHandler(crowdDbUrl,crowdDbUsername,crowdDbPassword,crowdDbname)

        query = '''
        SELECT user_name, created_date
        FROM cwd_user
        '''

        userCreated = {}
        results = dh.doQuery(query)
        w = csv.writer(open('out/UserCreated.csv','w'))
        w.writerow(['name','createdDate'])
        for name,time in results:
            if(time):
                w.writerow([name,time.strftime('%Y-%m-%d %H:%M:%S')])
                userCreated[name] = time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                w.writerow([name,time])
                userCreated[name] = time
        dh.closeCon()
        return userCreated

def main():
    eu = ExternalUsers()
    create = eu.getUserCreated()
    conflu = eu.getConfluLastLogin()
    jira = eu.getJiraLastLogin()
    eu.externalUserstoCSV(jira,conflu,create)

if __name__== "__main__":
    main()
