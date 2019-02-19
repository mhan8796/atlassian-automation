# Python code to utilize some of the atlassian API and DB access

Use pip to install missing packages

## To handle ID request
```
python3 idRequestHandler.py
```
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

## To handle ID deactivation
```
python3 idDeactivationHandler.py
```
* A method to process the given ID deacticvation.
* The request only handle the request from certain people. 
* A. If the request created by other peope other than the "creators", leave a comment and mark as resolved.
* B. Else handle the request, for each user
* 1. if the user cannot be found, add info to the comment and continue to next user
* 2. everything is fine, then process the request


## Write code in main.py using existing functions
```
python3 main.py
```
