import os
import requests
from requests.auth import HTTPBasicAuth
import json

from management.Utils import utils

auth = HTTPBasicAuth(os.getenv('JIRA_USER'), os.getenv('JIRA_PASSWORD'))
headers = {"Accept": "application/json"}
base_url = 'https://velco-tech.atlassian.net'


####### ISSUES
def get_all_issue_type_for_project(project_id):
    url = base_url + '/rest/api/3/issuetype/project'
    query = {
        'projectId': project_id
    }
    response = requests.request("GET", url, headers=headers, params=query, auth=auth)
    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))


def get_all_issue_from_project(project_key):
    list_issues = []
    url = base_url + "/rest/api/3/search"

    query = {
        'jql': '(updated >= -60d) and status != "WONT DO" and project = ' + project_key + ' order by created DESC'
    }
    response = requests.request("GET", url, headers=headers, params=query, auth=auth)
    print(json.loads(response.text))
    issues = json.loads(response.text)['issues']

    for issue in issues:
        list_issues.append(issue)

    query = {
        'jql': 'updated <= -60d and status != "DONE" and status != "WONT DO" and project = ' + project_key + ' order by created DESC'
    }
    response = requests.request("GET", url, headers=headers, params=query, auth=auth)
    issues = json.loads(response.text)['issues']

    for issue in issues:
        list_issues.append(issue)

    return list_issues


def get_all_issue_not_end_from_customer_project(project_key):
    list_issues = []
    url = base_url + "/rest/api/3/search"

    query = {
        'jql': 'status != "WONT DO" and status != "DONE" and (type = Story or type = Bug) and project = ' + project_key + ' order by created DESC'
    }
    response = requests.request("GET", url, headers=headers, params=query, auth=auth)
    issues = json.loads(response.text)['issues']

    for issue in issues:
        list_issues.append(issue)

    return list_issues


def get_all_issue_by_personne(assignee):
    list_issues = []
    url = base_url + "/rest/api/3/search"

    query = {
        'jql': '(updated >= -60d) and status != "WONT DO" and assignee = \"' + assignee + '\"'
    }
    response = requests.request("GET", url, headers=headers, params=query, auth=auth)
    issues = json.loads(response.text)['issues']

    for issue in issues:
        list_issues.append(issue)

    query = {
        'jql': 'updated <= -60d and status != "DONE" and status != "WONT DO" and assignee = \"' + assignee + '\"'
    }
    response = requests.request("GET", url, headers=headers, params=query, auth=auth)
    issues = json.loads(response.text)['issues']
    for issue in issues:
        list_issues.append(issue)

    return list_issues


def get_story_details(story_key):
    url = base_url + "/rest/api/3/issue/" + story_key
    response = requests.request("GET", url, headers=headers, auth=auth)
    issue = json.loads(response.text)

    s = utils.get_last_sprint_issue(issue)
    sprint = s['sprints']
    start_date = s['start_date']
    end_date = s['end_date']
    concat_version = ''

    try:
        for version in issue['fields']['fixVersions']:
            if 'TARGET' in str(version['name']) or 'PROD' in str(version['name']) and concat_version == '':
                concat_version = str(version['name'])
        if concat_version == '':
            print('ERROR Version : ' + str(issue['key']))
    except KeyError:
        pass

    return {
        'sprint': sprint,
        'start_date': start_date,
        'end_date': end_date,
        'version': concat_version
    }


def get_task(task_key):
    url = base_url + "/rest/api/3/issue/" + task_key
    response = requests.request("GET", url, headers=headers, auth=auth)
    issue = json.loads(response.text)
    return issue


def get_task_assignation(task) -> str:
    assigne = 'Unassigne'
    try:
        assigne = task['fields']['assignee']['displayName']
        print(assigne)
    except KeyError:
        pass
    except TypeError:
        pass
    return assigne


def get_task_ressource_type(task):
    try:
        return task['fields']['customfield_10071']['value']
    except KeyError:
        return None
    except TypeError:
        return None


def get_task_assignee(task):
    try:
        return task['fields']['assignee']['displayName']
    except KeyError:
        return ''
    except TypeError:
        return ''


def get_task_estimation(issue):
    if str(issue['fields']['status']['name']) == 'WONT DO':
        return 0
    estimation = issue['fields']['timeestimate']
    if estimation is None or estimation == 0:
        estimation = issue['fields']['aggregatetimespent']
    if estimation is None or estimation == 0:
        estimation = issue['fields']['timeoriginalestimate']
    try:
        if estimation is None or estimation == 0:
            estimation = issue['fields']['timetracking']['originalEstimateSeconds']
        if estimation is None or estimation == 0:
            estimation = issue['fields']['timetracking']['timeSpentSeconds']
    except KeyError:
        pass
    # Passage en jours pour les estimations JIRA
    if estimation is None:
        estimation = 0
    estimation = estimation / 60 / 60 / 8
    return estimation


def get_story_linked(task):
    linked_story_key = ''
    for issueLinks in task['fields']['issuelinks']:
        try:
            if issueLinks['outwardIssue']['fields']['issuetype']['name'] == 'Story':
                return issueLinks['outwardIssue']['key']
            if issueLinks['outwardIssue']['fields']['issuetype']['name'] == 'Bug':
                return issueLinks['outwardIssue']['key']
        except KeyError:
            pass
    return linked_story_key


def get_all_issue_from_version(version_name):
    list_issues = []
    url = base_url + "/rest/api/3/search"

    query = {
        'jql': 'fixVersion = \'' + version_name + '\''
    }
    response = requests.request("GET", url, headers=headers, params=query, auth=auth)
    issues = json.loads(response.text)['issues']

    for issue in issues:
        list_issues.append(issue)
    return list_issues


def get_story_estimations(story):
    estimation = 0
    estimation_done = 0
    estimations = {
        'estimation': estimation,
        'estimation_done': estimation_done
    }
    for link_issue in story['fields']['issuelinks']:
        try:
            task = get_task(link_issue['inwardIssue']['key'])
            assignee = get_task_assignation(task)
            tmp_estimation = get_task_estimation(task)
            estimation = estimation + tmp_estimation
            estimation_done = estimation_done + utils.get_task_estimation_done(
                task['fields']['status']['name'], tmp_estimation)
        except KeyError:
            print('Error key', story['key'])
            pass
        except TypeError:
            print('Error type', story['key'])
            pass
    return {
        'estimation': estimation,
        'estimation_done': estimation_done
    }


####### PROJECT
def get_all_project_by_category(category):
    list_project = []
    size = 50
    initial = 0
    url = base_url + "/rest/api/3/project/search"
    while True:
        start = initial * size
        query = {
            'startAt': start,
            'maxResults': size
        }
        response = requests.request("GET", url, headers=headers, auth=auth, params=query)
        is_last = json.loads(response.text)['isLast']
        initial += 1
        projects = json.loads(response.text)['values']

        for project in projects:
            try:
                if project['projectCategory']['name'] == category:
                    list_project.append(project)
            except KeyError:
                print('{} {} {}'.format('WARNING!', project['key'], 'as no category'))
        if str(is_last) == 'True':
            break
    return list_project


def get_all_project_category_by_name(category_name):
    url = base_url + "/rest/api/3/projectCategory"
    response = requests.request("GET", url, headers=headers, auth=auth)
    for category in json.loads(response.text):
        if category['name'] == category_name:
            return category['id']
    return 0


def check_if_project_exist(project_key):
    url = base_url + "/rest/api/3/project/" + project_key
    response = requests.request("GET", url, headers=headers, auth=auth)
    project = json.loads(response.text)
    try:
        err = project['errorMessages']
        return False
    except KeyError:
        return True
    return True


def check_if_task_exist(task_key):
    url = base_url + "/rest/api/3/issue/" + task_key
    response = requests.request("GET", url, headers=headers, auth=auth)
    project = json.loads(response.text)
    try:
        err = project['errorMessages']
        return False
    except KeyError:
        return True
    return True


####### FIELD
def get_task_ressource_type(task):
    try:
        return task['fields']['customfield_10071']['value']
    except KeyError:
        return None
    except TypeError:
        return None


def get_task_assignee(task):
    try:
        return task['fields']['assignee']['displayName']
    except KeyError:
        return ''
    except TypeError:
        return ''


def get_task_estimation(issue):
    if str(issue['fields']['status']['name']) == 'WONT DO':
        return 0
    estimation = issue['fields']['timeestimate']
    if estimation is None or estimation == 0:
        estimation = issue['fields']['aggregatetimespent']
    if estimation is None or estimation == 0:
        estimation = issue['fields']['timeoriginalestimate']
    try:
        if estimation is None or estimation == 0:
            estimation = issue['fields']['timetracking']['originalEstimateSeconds']
        if estimation is None or estimation == 0:
            estimation = issue['fields']['timetracking']['timeSpentSeconds']
    except KeyError:
        pass
    # Passage en jours pour les estimations JIRA
    if estimation is None:
        estimation = 0
    estimation = estimation / 60 / 60 / 8
    return estimation


def get_epic():
    list_issues = []
    url = base_url + "/rest/api/3/search"

    query = {
        'jql': 'type=Epic and labels="RM2023"'
    }
    response = requests.request("GET", url, headers=headers, params=query, auth=auth)
    issues = json.loads(response.text)['issues']

    for issue in issues:
        list_issues.append(issue)
    return list_issues


def get_epic_stories(epic_key):
    list_issues = []
    url = base_url + "/rest/api/3/search"

    query = {
        'jql': 'status != "WONT DO" and "Epic Link" = ' + epic_key
    }
    response = requests.request("GET", url, headers=headers, params=query, auth=auth)
    issues = json.loads(response.text)['issues']

    for issue in issues:
        list_issues.append(issue)

    return list_issues
