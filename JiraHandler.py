import requests
import json

class JiraHandler:
    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url

    # Get the project role based on the project key, return a dictionary.
    # return None if failed
    def getProRole(self, key):
        url = self.url +'/rest/api/2/project/' + key + '/role'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.get(url,headers = headers, auth = (self.username,self.password))
        if r.status_code==200:
            return r.json()
        else:
            return None

    # Get the project role info based on project key and role name.
    def getProRoleInfo(self, key, role):
        roleDict = self.getProRole(key)
        url = roleDict.get(role)
        if (url):
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            r = requests.get(url,headers = headers, auth = (self.username,self.password))
            if r.status_code==200:
                return r.json()
        return None

    # Get the project role actor users' and groups' username based on project key and role name.
    def getProRoleActorUsernames(self, key, role):
        userList = []
        groupList = []
        actors = self.getProRoleInfo(key,role).get('actors')
        if (actors):
            for actor in actors:
                if (actor.get('type')=='atlassian-user-role-actor'):
                    userList.append(actor.get('name'))
                elif (actor.get('type')=='atlassian-group-role-actor'):
                    groupList.append(actor.get('name'))
        return userList, groupList

    # Get the screen available fields to add
    def getScrAvaFields(self,screenId):
        url = self.url +'/rest/api/2/screens/'+screenId+'/availableFields'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.get(url,headers = headers, auth = (self.username,self.password))
        if r.status_code==200:
            return r.json()
        else:
            return None

    # Get the screen tabs
    def getScrTabs(self,screenId):
        url = self.url +'/rest/api/2/screens/'+screenId+'/tabs'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.get(url,headers = headers, auth = (self.username,self.password))
        if r.status_code==200:
            return r.json()
        else:
            return None

    # Get the screen tabs
    def getScrFields(self,screenId,tabId):
        url = self.url +'/rest/api/2/screens/'+screenId+'/tabs/' +tabId+'/fields'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.get(url,headers = headers, auth = (self.username,self.password))
        if r.status_code==200:
            return r.json()
        else:
            return None

    # Get the version from id
    def getVersion(self,id):
        url = self.url +'/rest/api/2/version/'+id
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.get(url,headers = headers, auth = (self.username,self.password))
        if r.status_code==200:
            return r.json()
        else:
            return None

    # Get the version from id
    def updateVersion(self,id,data):
        url = self.url +'/rest/api/2/version/'+id
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.put(url,headers = headers, auth = (self.username,self.password),data = json.dumps(data))
        if r.status_code==200:
            return True
        else:
            return False

    # Get the project by key
    def getProject(self, key):
        url = self.url +'/rest/api/2/project/'+key
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.get(url,headers = headers, auth = (self.username,self.password))
        if r.status_code==200:
            return r.json()
        else:
            return None

    # Get the issues for ID requests
    def getIdRequests(self):
        url = self.url +'/rest/api/2/search?maxResults=1000&jql=project = NEWMEDIATOOLSPROCESS AND type = "ID Request" AND status = Open'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.get(url,headers = headers, auth = (self.username,self.password))
        if r.status_code==200:
            return r.json()
        else:
            return None

    # Get the issues for ID deactivations
    def getIdDeactivations(self):
        url = self.url +'/rest/api/2/search?maxResults=1000&jql=project = NEWMEDIATOOLSPROCESS AND type = "ID Deactivation" AND status = Open AND "Deactivation Date" <= now()'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.get(url,headers = headers, auth = (self.username,self.password))
        if r.status_code==200:
            return r.json()
        else:
            return None

    # Add comments to JIRA issue
    def addComment(self,issueId,msg):
        url = self.url +'/rest/api/2/issue/' + issueId + '/comment'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        data = {
            'body':msg
        }
        r = requests.post(url,headers = headers, auth = (self.username,self.password),data = json.dumps(data))
        if r.status_code==201:
            return True
        else:
            print('Error adding comment: ' + str(r.status_code))
            return False

    # update issue
    def updateIssue(self,issueId,data):
        url = self.url +'/rest/api/2/issue/' + issueId
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.post(url,headers = headers, auth = (self.username,self.password),data = json.dumps(data))
        if r.status_code==204:
            return True
        else:
            print('Error updating issue: ' + str(r.status_code))
            return False

    # do transition
    def doTransition(self,issueId,id):
        url = self.url +'/rest/api/2/issue/' + issueId + '/transitions'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        data = {'transition': {'id': id}}
        r = requests.post(url,headers = headers, auth = (self.username,self.password),data = json.dumps(data))
        if r.status_code==204:
            return True
        else:
            print('Error doing transition: ' + str(r.status_code))
            return False

    # get user info
    def getUser(self,username):
        url = self.url +'/rest/api/2/user?username=' + username
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.get(url,headers = headers, auth = (self.username,self.password))
        if r.status_code==200:
            return r.json()
        else:
            print('Error getting user: ' + str(r.status_code))
            return None
