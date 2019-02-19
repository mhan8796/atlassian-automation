from PasswordHandler import PasswordHandler
from CrowdHandler import CrowdHandler
from JiraHandler import JiraHandler
from ConfluenceHandler import ConfluenceHandler
import csv
import configparser
from ExternalUsers import ExternalUsers

config = configparser.ConfigParser()
config.read('config.ini') # Change this in the server!
jiraUrl = config['legacy_jira_prod']['url']
jiraUsername = config['legacy_jira_prod']['username']
jiraPassword = config['legacy_jira_prod']['password']
crowdUrl = config['legacy_crowd_prod']['url']
crowdUsername = config['legacy_crowd_prod']['username']
crowdPassword = config['legacy_crowd_prod']['password']
confUrl = config['legacy_confluence_prod']['url']
confUsername = config['legacy_confluence_prod']['username']
confPassword = config['legacy_confluence_prod']['password']

def main():
    # Initialize three handlers
    jh = JiraHandler(jiraUsername,jiraPassword,jiraUrl)
    ch = CrowdHandler(crowdUsername,crowdPassword,crowdUrl)
    coh = ConfluenceHandler(confUsername,confPassword,confUrl)

    # Write your code here


if __name__== "__main__":
    main()
