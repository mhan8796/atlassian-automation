import requests
import json
from progressbar import ProgressBar


class ConfluenceHandler:

    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url

    # Delete content
    def deleteContent(self, contentId):
        url = self.url +'/rest/api/content/' + contentId
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.delete(url,headers = headers, auth = (self.username,self.password))
        if r.status_code==204:
            return True
        else:
            return False

    # Get content
    def getContent(self, contentId):
        url = self.url +'/rest/api/content/' + contentId
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.get(url,headers = headers, auth = (self.username,self.password))
        return r.json()