from CrowdHandler import CrowdHandler
from JiraHandler import JiraHandler
from validate_email import validate_email
import configparser

# The code will only handle the request create by following people
creators = ['rhan']

def main():
    # Get parameters
    config = configparser.ConfigParser()
    config.read('config.ini') # Change this in the server!
    jiraUrl = config['legacy_jira_prod']['url']
    jiraUsername = config['legacy_jira_prod']['username']
    jiraPassword = config['legacy_jira_prod']['password']
    crowdUrl = config['legacy_crowd_prod']['url']
    crowdUsername = config['legacy_crowd_prod']['username']
    crowdPassword = config['legacy_crowd_prod']['password']

    # Initialize two handlers
    jh = JiraHandler(jiraUsername,jiraPassword,jiraUrl)
    ch = CrowdHandler(crowdUsername,crowdPassword,crowdUrl)

    idDeactivations = jh.getIdDeactivations()
    issueList = idDeactivations.get('issues')
    
    for issue in issueList:
        '''
        * A method to process the given ID deacticvation.
        * The request only handle the request from certain people. 
        * 1. If the request created by other peope other than the "creators",
        *    leave a comment and mark as resolved.
        * 2. Else handle the request, for each user
        *    2.1 if the user cannot be found, add info to the comment and continue to next user
        *    2.2 everything is fine, then process the request
        '''
        print ('***********************************')
        print ('Start to process issue NO.' + issue.get('id'))
        users = issue.get('fields').get('customfield_13662') # Legacy Jira # get('customfield_13581') # Legacy test Jira
        creator = issue.get('fields').get('creator').get('name')

        msg = '' #comment

        if creator not in creators:
            msg = 'Unauthorized creators detected. Request will not be taken. This request is for authrized personnel only.'
            print ('Unauthorized creators!!!!!')
        else:
            for user in users:
                username = user.get('name')
                # User not found
                if len(ch.getInfoFromUsernames([username])) == 0:
                    msg += 'Oops. User ' + username + ' does not exist in crowd.\n'
                    print ('User ' + username + 'not found.')
                # Else handle the request
                else:
                    userInfo = ch.getInfoFromUsernames([username])[0]
                    data = {
                    'name':username,
                    'active':False,
                    'first-name':userInfo.get('first-name'),
                    'last-name':userInfo.get('last-name'),
                    'display-name':userInfo.get('display-name'),
                    'email':userInfo.get('email')
                    }
                    ch.updateUser(username,data)
                    msg += 'User ' + username + ' has been deactivated successfully.\n'
                    print ('User ' + username + ' has been deactivated.')

        # move issue as resolve
        jh.doTransition(issue.get('id'),'5')
        # Add comments corresponding to each option
        jh.addComment(issue.get('id'),msg)
        print ('Done Processing this issue')
        print ('***********************************')
        print ('')
        

if __name__== "__main__":
    main()
