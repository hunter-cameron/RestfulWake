
# from: http://web2py.com/books/default/chapter/29/09/access-control
from gluon.contrib.login_methods.oauth20_account import OAuthAccount
from fitbit import Fitbit

# Define oauth application id and secret.
CLIENT_ID = '22CMMH'
CLIENT_SECRET = "28a2e2e8bedd901d4bf5357309fcd055"
REDIRECT = "http://45.37.168.50:8418/restfulwake/default/user/login"


AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"





from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError


def update_token(token):
    """ Fitbit module will take care of refreshing tokens and call this method when necessary """

    print("Updating token")

    # update the user dict
    user = db(db.auth_user.username == token['user_id']).select()

    if user:
        user.update(
            access_token=token['access_token'],
            refresh_token=token['refresh_token'],
            expires_at=token['expires_at']
        )
    else:
        print("Token refreshed but user not found!!!")

    # update session token
    session.token = token


class FitbitOAuth(object):

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        """ Initialize the FitbitOauth2Client """

        if client_id is None:
            self.client_id = CLIENT_ID
        else:
            self.client_id = client_id

        if client_secret is None:
            self.client_secret = CLIENT_SECRET
        else:
            self.client_secret = client_secret

        if redirect_uri is None:
            self.redirect_uri = REDIRECT
        else:
            self.redirect_uri = redirect_uri

        session.client_id = self.client_id
        session.client_secret = self.client_secret

    def get_profile(self, token):
        fb = Fitbit(self.client_id, self.client_secret,
                    access_token=token['access_token'],
                    refresh_token=token['refresh_token'],
                    expires_at=token['expires_at'],
                    refresh_cb=update_token
                    )
        profile = fb.user_profile_get()
        print("got profile")

        return dict(first_name=profile['user']['firstName'],
                    last_name=profile['user']['lastName'],
                    username=token['user_id'])
#                    access_token=token['access_token'],
#                    refresh_token=token['refresh_token'],
#                    expires_at=token['expires_at'])

    def get_user(self):
        """
        Web2py required method
        """

        print(("get_user called", request.vars))

        # check if there is already a token
        if session.token:
            print("Session token found: using current auth")
            return self.get_profile(session.token)

        # handle getting access tokens
        code = request.vars.code
        if code:
            print("Auth code found: Getting access token")
            self.fitbit.client.fetch_access_token(code=code, redirect_uri=self.redirect_uri)

            # store token for later
            session.token = self.fitbit.client.session.token

            return self.get_profile(session.token)

        else:
            # handle getting initial user auth
            print("Blank slate: Getting authorization code")
            url, _ = self.fitbit.client.authorize_token_url(scope=['profile', 'sleep', 'settings'], redirect_uri=self.redirect_uri)

            # redirect the user to fitbit
            redirect(url)

        print("Never reach the end!!!")

    def login_url(self, next="/"):
        """ Used by web2py; called upon login """
        print("Calling login url")
        self.get_user()
        return next

    def logout_url(self, next="/"):
        """ Used by web2py; called upon logout """
        del session.token
        return next


class Fitbit2(OAuthAccount):
    pass


# use the above class to build a new login form
auth.settings.login_form=FitbitOAuth()
