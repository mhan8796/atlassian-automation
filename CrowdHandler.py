import requests
import json
from datetime import datetime
from progressbar import ProgressBar


class CrowdHandler:

    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url

    # Get usernames from a list of group names if the group exists
    def getUsernameFromGroups(self, groupList):
        retList = []
        for group in groupList:
            url = self.url +'/rest/usermanagement/1/group/user/direct?groupname=' + group
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            r = requests.get(url,headers = headers, auth = (self.username,self.password))
            if r.status_code == 200:
                userList = r.json().get('users')
                for user in userList:
                    if (user.get('name') not in retList):
                        retList.append(user.get('name'))
        return retList

    # Get Info from a list of usernames if the user exists
    def getInfoFromUsernames(self, usernameList):
        userInfoList = []
        for user in usernameList:
            userDict = {}
            url = self.url + '/rest/usermanagement/1/user?username=' + user
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            r = requests.get(url,headers = headers, auth = (self.username,self.password))
            if r.status_code == 200:
                userDict['name'] = r.json().get('name')
                userDict['email'] = r.json().get('email')
                userDict['active'] = r.json().get('active')
                userDict['first-name'] = r.json().get('first-name')
                userDict['last-name'] = r.json().get('last-name')
                userDict['display-name'] = r.json().get('display-name')
                userInfoList.append(userDict)
        return userInfoList

    # Get emails from a list of group names
    def getEmailsFromGroups(self,groupList):
        usernameList = self.getUsernameFromGroups(groupList)
        userInfoList = self.getInfoFromUsernames(usernameList)
        emailList = []
        for userInfo in userInfoList:
            emailList.append(userInfo.get('email'))
        return emailList

    # Merge members in groupA to groupB. Create groupB if it does not exists
    def mergeGroupAtoGroupB(self, groupA, groupB):
        self.addGroup(groupB)
        groupAUsers = self.getUsernameFromGroups([groupA])
        groupBUsers = {i:True for i in self.getUsernameFromGroups([groupB])}
        print('start merging from '+ groupA +' to '+groupB)
        pbar = ProgressBar()
        for groupAuser in pbar(groupAUsers):
            if (groupBUsers.get(groupAuser)==None):
                self.addUserstoGroup([groupAuser],groupB)

    # Add a group to crowd. return true if succeed, otherwise return false
    def addGroup(self, group, description = ''):
        url = self.url +'/rest/usermanagement/1/group'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        data = {'name':group,'description':description,'type':'GROUP','active':True}
        r = requests.post(url,headers = headers, auth = (self.username,self.password), data = json.dumps(data) )
        if r.status_code == 201:
            print('group added: '+group)
            return True
        else:
            return False

    # Add users to a group
    def addUserstoGroup(self, usernameList, group):
        self.addGroup(group)
        url = self.url +'/rest/usermanagement/1/group/user/direct?groupname='+group
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        alladded = True
        for user in usernameList:
            data = {'name':user}
            r = requests.post(url,headers = headers, auth = (self.username,self.password), data = json.dumps(data))
            if r.status_code != 201:
                    alladded = False
        return alladded

    # Get all user from crowd
    def getAllUsers(self):
        allUsers = []
        url = self.url +'/rest/usermanagement/1/search?entity-type=user&max-results=99999'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.get(url,headers = headers, auth = (self.username,self.password))
        if r.status_code == 200:
            pbar = ProgressBar()
            for user in pbar(r.json().get('users')):
                allUsers.append(user.get('name'))
        return allUsers

    # Get all user info with email not @collegeboard.org
    def getExternalUserInfo(self):
        allUsers = self.getAllUsers()
        externalUserInfoList = []
        pbar = ProgressBar()
        for user in pbar(allUsers):
            userInfo = self.getInfoFromUsernames([user])
            if (userInfo[0].get('email')==None):
                externalUserInfoList.append(userInfo[0])
            elif (userInfo[0].get('email').split('@')[-1].lower() != 'collegeboard.org'):
                externalUserInfoList.append(userInfo[0])
        return externalUserInfoList

    # Get groups from a list of usernames
    def getGroupsfromUsernames(self, usernameList):
        retList = []
        for username in usernameList:
            groupDict = {}
            url = self.url +'/rest/usermanagement/1/user/group/direct?max-results=99999&username='+username
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            r = requests.get(url,headers = headers, auth = (self.username,self.password))
            if r.status_code==200:
                groups = [group.get('name') for group in r.json().get('groups')]
                groupDict['name'] = username
                groupDict['groups'] = groups
                retList.append(groupDict)
        return retList

    # Get attributes from a list of usernames
    def getAttrifromUsernames(self, usernameList):
        retAttriList = []
        for username in usernameList:
            userAttriDict = {}
            url = self.url +'/rest/usermanagement/1/user/attribute?username='+username
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            r = requests.get(url,headers = headers, auth = (self.username,self.password))
            if r.status_code == 200:
                userAttriDict['name'] = username
                for attribute in r.json().get('attributes'):
                    if (attribute.get('name')=='lastActive' or attribute.get('name')=='lastAuthenticated'):
                        timestamp = int(float(attribute.get('values')[0])/1000)
                        userAttriDict[attribute.get('name')]=datetime.fromtimestamp(timestamp)
                    else:
                        userAttriDict[attribute.get('name')]=attribute.get('values')
            retAttriList.append(userAttriDict)
        return retAttriList

    # Delete a list of groups, return true if all succeed. return false if not
    def deleteGroup(self,groupList):
        allDone = True
        for group in groupList:
            url = self.url +'/rest/usermanagement/1/group?groupname='+group
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            r = requests.delete(url,headers = headers, auth = (self.username,self.password))
            if r.status_code!=204:
                allDone = False
                print ('Failed to delete: ' + group)
        return allDone


    # Add a user to crowd. return true if succeed, otherwise return false
    def addUser(self, userInfo):
        url = self.url +'/rest/usermanagement/latest/user'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        data = {
            'name':userInfo.get('name'),
            'password':{'value':'please_change_this'}, # password has to be long enough to be accepted by server
            'active':True,
            'first-name':userInfo.get('first-name'),
            'last-name':userInfo.get('last-name'),
            'display-name':userInfo.get('display-name'),
            'email':userInfo.get('email'),
        }
        r = requests.post(url,headers = headers, auth = (self.username,self.password), data = json.dumps(data))
        if r.status_code == 201:
            print('User added: '+ userInfo.get('name'))
            self.resetUserPassword(userInfo.get('name'))
            return True
        else:
            print('Error adding user: ' + str(r.status_code))
            return False

    # Reset user password by send them an email
    def resetUserPassword(self, username):
        url = self.url +'/rest/usermanagement/1/user/mail/password?username=' + username
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        data = {'username':username}
        r = requests.post(url,headers = headers, auth = (self.username,self.password), data = json.dumps(data))
        if r.status_code == 204:
            print('Sent email to reset password')
            return True
        else:
            print('Error resetting password: ' + str(r.status_code))
            return False

    # Update user info
    def updateUser(self, username, data):
        url = self.url +'/rest/usermanagement/1/user?username=' + username
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.put(url,headers = headers, auth = (self.username,self.password), data = json.dumps(data))
        if r.status_code == 204:
            return True
        else:
            print('Error updating user: ' + str(r.status_code))
            return False
