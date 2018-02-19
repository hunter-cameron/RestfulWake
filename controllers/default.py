# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----
import datetime

from fitbit import Fitbit
# update teh API version
Fitbit.API_VERSION = 1.2
from collections import Counter

def _update_token(token):
    """ Called by fitbit when token needs to be updates"""
    session.token = token

def _get_fitbit():
    return Fitbit(session.client_id, session.client_secret,
                  access_token=session.token['access_token'],
                  refresh_token=session.token['refresh_token'],
                  expires_at=session.token['expires_at'],
                  refresh_cb=_update_token
                  )


def index():
    form = SQLFORM.factory(
        Field('Earliest', type='time', default="8:00"),
        Field('Latest', type='time'),
    )

    return dict(form=form)


class SleepLog(object):

    @staticmethod
    def to_datetime(dt_str):
        """ Convets a datetime string to a datetime object """
        return datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%f")

    def __init__(self, start_time, end_time, stages=None):
        # convert all the info to datetime objects
        self.start_time = self.to_datetime(start_time)
        self.end_time = self.to_datetime(end_time)

        # the date is always the date the end time falls on
        self.date = self.end_time.date()

        for stage in stages:
            stage['dateTime'] = self.to_datetime(stage['dateTime'])

        self.stages = stages

    def __str__(self):
        return "Sleep Log from {self.date}".format(self=self)

    def __getitem__(self, datetime_time):
        """ Returns the stage at the supplied time """
        for stage in self.stages:
            start = stage['dateTime'].time()
            end = (stage['dateTime'] + timedelta(seconds=stage['seconds'])).time()

            # check if the times are on the same day
            if start <= datetime_time < end:
                return stage['level']
            # if start is > end, the stage loops from one day to another
            # technically, this could be wrong if someone maintained the same sleep stage for over 24 hours
            # e.g. go to sleep at 9pm until 10pm the next day would be missed.
            elif start >= datetime_time < end and start > end:
                return stage['level']

        return None



def _parse_sleep_history(log):
    """
    Parses multiple days in sleep history

    Returns a data frame with sleep stages with 30 second granularity

     """
    sleep_logs = []
    for sleep_event in log['sleep']:
        # look for the main sleep
        # history doesn't have isMainSleep so it is possble to have multiple entries per day
        # however, often naps will be recorded as "classic" types because they are less that ~3 hours
        if sleep_event['type'] == "stages":
            log = SleepLog(sleep_event['startTime'], sleep_event['endTime'], sleep_event['levels']['data'])
            sleep_logs.append(log)

    for log in sleep_logs:
        print(str(log))



def _parse_sleep_log(log):
    for sleep_event in log['sleep']:
        # look for the main sleep
        if sleep_event['isMainSleep']:
            if sleep_event['type'] == "stages":
                # parse stages, this is what we want
                for entry in sleep_event['levels']['data']:
                    pass

            elif sleep_event['type'] == "classic":
                # parse classic style
                pass
            else:
                # sleep unknown...
                pass
            sleep_start = datetime.datetime.strptime(sleep_event["startTime"], "%Y-%m-%dT%H:%M:%S.%f")
            print((sleep_start, type(sleep_start)))

            stages = Counter()
            for minute in sleep_event['minuteData']:
                # 1 = asleep
                # 2 = restless
                # 3 = awake
                stages[minute['value']] += 1

            print(stages)
        print(sleep_event.keys())

@auth.requires_login()
def test():
    sleep_date = datetime.date(2018, 2, 12)

    fb = _get_fitbit()

    # get a two week sleep history
    today = datetime.datetime.today()
    old = today - datetime.timedelta(days=14)
    sleep_history = fb.time_series("sleep", base_date=old, end_date=today)
    _parse_sleep_history(sleep_history)


    #sleep_log = fb.get_sleep(sleep_date)
    #_parse_sleep_log(sleep_log)

    return dict(vars=sleep_history)




def alarm_request():
    """ Fields an alarm request """
    return dict(vars=request.vars)

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())
