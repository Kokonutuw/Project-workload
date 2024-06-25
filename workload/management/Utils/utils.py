from datetime import date
import datetime

from django.utils.dateparse import parse_datetime


def check_date_under_30(creation_date):
    date_creation = date.fromisoformat(creation_date[0:10])
    now = date.today()
    diff = now - date_creation
    return diff.days < 30


def check_date_over_30(creation_date):
    date_creation = date.fromisoformat(creation_date[0:10])
    now = date.today()
    diff = now - date_creation
    return diff.days > 30


def compare_two_date(first_date, second_date):
    date_1 = date.fromisoformat(first_date[0:10])
    date_2 = date.fromisoformat(second_date[0:10])
    return date_1 > date_2


def get_task_estimation_done(status, estimation):
    if str(status) == 'Done':
        return estimation
    elif str(status) == 'WONT DO':
        return 0
    elif str(status) == 'CODE REVIEW':
        return estimation * 0.8
    elif str(status) == 'validated on test' or str(status) == 'READY ON TEST':
        return estimation * 0.9
    else:
        return 0


def get_last_sprint_issue(issue):
    sprint = ''
    start_date = ''
    end_date = ''
    try:
        if issue['fields']['customfield_10020'] is not None:
            if len(issue['fields']['customfield_10020']) == 1:
                sprt = issue['fields']['customfield_10020'][0]
                if str(sprt['state']) != 'closed':
                    sprint = sprt['name']
                    start_date = sprt['startDate']
                    end_date = sprt['endDate']
            else:
                for s in issue['fields']['customfield_10020']:
                    if start_date != '' and str(s['state']) != 'closed' and str(s['startDate']) != '':
                        if compare_two_date(s['startDate'], start_date):
                            sprint = s['name']
                            start_date = s['startDate']
                            end_date = s['endDate']
                    else:
                        if str(s['state']) != 'closed':
                            sprint = s['name']
                            start_date = s['startDate']
                            end_date = s['endDate']
    except KeyError:
        pass
    return {
        'sprints': sprint,
        'start_date': start_date,
        'end_date': end_date
    }


def get_first_sprint(sprint1, sprint2):
    if compare_two_date(sprint1['start_date'], sprint2['start_date']):
        return sprint2
    else:
        return sprint1


def get_last_sprint(sprint1, sprint2):
    if compare_two_date(sprint1['start_date'], sprint2['start_date']) :
        return sprint1
    else:
        return sprint2


def get_first_date(date1, date2):
    if compare_two_date(str(date1), str(date2)):
        return date2
    else:
        return date1


def get_last_date(date1, date2):
    if compare_two_date(str(date1), str(date2)):
        return date1
    else:
        return date2



def count_week_days(start_date, nb_day_end_month):
    print(start_date,nb_day_end_month )
    list = []
    list.append(parse_datetime('2023-01-01'))
    list.append(parse_datetime('2023-04-10'))
    list.append(parse_datetime('2023-05-01'))
    list.append(parse_datetime('2023-05-08'))
    list.append(parse_datetime('2023-05-18'))
    list.append(parse_datetime('2023-05-29'))
    list.append(parse_datetime('2023-07-14'))
    list.append(parse_datetime('2023-08-15'))
    list.append(parse_datetime('2023-11-01'))
    list.append(parse_datetime('2023-12-25'))
    list.append(parse_datetime('2024-01-01'))

    nbDays=0
    inc=0
    new_date = start_date - datetime.timedelta(days=1)
    while (inc <= nb_day_end_month):
        new_date = new_date + datetime.timedelta(days=1)
        if new_date.weekday() != 5 and new_date.weekday() != 6 and not list.__contains__(new_date):
            nbDays = nbDays + 1
        inc = inc + 1
    print(nbDays)
    return nbDays

