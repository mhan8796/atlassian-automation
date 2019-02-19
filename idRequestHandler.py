from CrowdHandler import CrowdHandler
from JiraHandler import JiraHandler
from validate_email import validate_email
import configparser

def main():
    # Get parameters
    config = configparser.ConfigParser()
    config.read('config.ini') 
    #config.read('/home/ubuntu/atlassian-automation/config.ini') # Change to this in the server!
    jiraUrl = config['legacy_jira_prod']['url']
    jiraUsername = config['legacy_jira_prod']['username']
    jiraPassword = config['legacy_jira_prod']['password']
    crowdUrl = config['legacy_crowd_prod']['url']
    crowdUsername = config['legacy_crowd_prod']['username']
    crowdPassword = config['legacy_crowd_prod']['password']

    # Initialize two handlers
    jh = JiraHandler(jiraUsername,jiraPassword,jiraUrl)
    ch = CrowdHandler(crowdUsername,crowdPassword,crowdUrl)

    idRequests = jh.getIdRequests()
    issueList = idRequests.get('issues')
    for issue in issueList:
        '''
        * A method to process the given ID request.
        * If the request is,
        * A. For a new user then it,
        * 1. Creates the user in the crowd.
        * 2. Adds the user to the groups 'confluence-users' and 'jira-users' based on the request (If it is an internal(CB) user (as determined from user's email address) then adds it to 'cb-users' and 'jira-developers' groups as well.)
        * 3. Requests password reset for the user. This triggers an email to the user to reset his/her password.
        * 4. Marks the ID request JIRA ticket "Resolved"
        * B. For an existing user
        * 1. First find the user info from crowd based on username.
        * 2. Compare the first-name, last-name, display-name, and  email to the request input.
        * 3. If they are all the same, then the user is an existing user, give the access, set user to active, left a comment and move to resolved.
        * 4. If one of them is different then the request is invalid, left a comment and move to resolved.
        * C. Containing invalid email then it marks the ID request JIRA ticket "Resolved" with a comment saying that the email address in the ticket is invalid.
        '''
        print ('***********************************')
        print ('Start to process issue NO.' + issue.get('id'))

        email = issue.get('fields').get('customfield_10968').lstrip().rstrip()
        firstName = issue.get('fields').get('customfield_10966').lstrip().rstrip()
        lastName = issue.get('fields').get('customfield_10967').lstrip().rstrip()

        if not validate_email(email):
            jh.addComment(issue.get('id'),'Invalid email address, ticket will not process. Please create a new ticket with correct information.')
            jh.doTransition(issue.get('id'),'5')
            print ('Done Processing this issue due to invalid email.')
            print ('***********************************')
            print ('')
            continue

        # Internal user
        if isInternal(email):
            print ('It is an internal user')
            msg = 'Internal user will not be added here. User should use their AD/laptop login for production Jira.'
            jh.addComment(issue.get('id'),msg)
            jh.doTransition(issue.get('id'),'5')
            print ('Done Processing this issue due to internal user.')
            print ('***********************************')
            print ('')
            continue

        # External user only. # External users use email address as ID
        name = email
        request = issue.get('fields').get('customfield_11671').get('value')
        msg = ''

        # New user
        if len(ch.getInfoFromUsernames([name])) == 0 :
            userInfo = {}
            userInfo['name'] = name
            userInfo['email'] = email
            userInfo['first-name'] = firstName
            userInfo['last-name'] = lastName
            userInfo['display-name'] = firstName + ' ' + lastName
            if not ch.addUser(userInfo):
                msg = 'User failed to add to crowd.'
            else:
                msg = '''User successfully added to crowd.
                You may need to wait at most 30min for both jira and wiki to sync.
                An password reset email has been sent to the user's email.'''

                # Add to groups based on request type
                msg = handleRequest(request,msg,ch,name)

        # username already exists
        else:
            print ('Username already exists')
            msg = 'This username already exists in crowd.'
            existUserInfo = ch.getInfoFromUsernames([name])[0]
            existFirstName = existUserInfo.get('first-name')
            existLastName = existUserInfo.get('last-name')
            existEmail = existUserInfo.get('email')
            existingUser = True
            if existEmail and email.lower() != existEmail.lower():
                existingUser = False
            if existFirstName and firstName.lower() != existFirstName.lower():
                existingUser = False
            if existLastName and lastName.lower() != existLastName.lower():
                existingUser = False
            # Invalid request
            if not existingUser:
                msg += '\nThis is an invalid request. User info does not match existing record.'
                jh.addComment(issue.get('id'),msg)
                jh.doTransition(issue.get('id'),'5')
                print ('Done Processing this issue due to invalid request')
                print ('***********************************')
                print ('')
                continue
            # Everything matches, it is an existing user
            else:
                # Add to groups based on request type
                msg = handleRequest(request,msg,ch,name)
                # Update user to be active
                data = {
                'name':name,
                'active':True,
                'first-name':firstName,
                'last-name':lastName,
                'display-name':firstName+' '+lastName,
                'email':email
                }
                ch.updateUser(name,data)
                msg += '\n User has been set to active. If there is still access issue, please reset your password.'

        # move issue as resolved
        jh.doTransition(issue.get('id'),'5')
        # Add comments corresponding to each option
        jh.addComment(issue.get('id'),msg)

        print ('Done Processing this issue')
        print ('***********************************')
        print ('')

def isInternal(email):
    return True if (email.split('@')[-1].lower()=='.org') else False

def handleRequest(request,msg,ch,name):
    if request=='Both':
        ch.addUserstoGroup([name],'confluence-users')
        ch.addUserstoGroup([name],'jira-users')
        msg += '\nUser added to jira-users, confluence-users.'
    elif request=='Jira':
        ch.addUserstoGroup([name],'jira-users')
        msg += '\nUser added to jira-users.'
    elif request=='Wiki':
        ch.addUserstoGroup([name],'confluence-users')
        msg += '\nUser added to confluence-users.'
    return msg

if __name__== "__main__":
    main()
