
import datetime
from gluon import current


from fitbit import Fitbit
# update teh API version
Fitbit.API_VERSION = 1.2


def _update_token(token):
    """ Fitbit module will take care of refreshing tokens and call this method when necessary """

    print("Updating token")

    # update the user dict
    user = current.db(current.db.auth_user.username == token['user_id']).select().first()

    if user:
        user.update(
            token=token
        )
    else:
        print("Token refreshed but user not found!!!")

class FitBitHelper(object):
    """ Wraps around Fitbit api and contains useful methods for interacting with FitBit data """

    def __init__(self, user_id):
        self.user_id = user_id

        # look up the user in the database
        self.user = current.db(current.db.auth_user.id == user_id).select().first()
        if self.user is None:
            raise ValueError("User {user_id} wasn't found in the database!".format(user_id=user_id))

        self.fitbit = Fitbit(current.client_id, current.client_secret,
               access_token=self.user.token['access_token'],
               refresh_token=self.user.token['refresh_token'],
               expires_at=self.user.token['expires_at'],
               refresh_cb=_update_token
               )

    def get_sleep_history(self, period=datetime.timedelta(days=14)):
        """
        Gets a slice of sleep history ending with today

        The default slice is two weeks.
        """
        # get a two week sleep history
        today = datetime.datetime.today()
        old = today - datetime.timedelta(days=14)
        return self.fitbit.time_series("sleep", user_id=self.user.username, base_date=old, end_date=today)

