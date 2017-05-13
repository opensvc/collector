auth_google = config_get('auth_google', False)

if auth_google:
    import urllib2
    from gluon.contrib.login_methods.oauth20_account import OAuthAccount
    client_id = config_get('google_client_id', None)
    client_secret = config_get('google_client_secret', None)

    class googleAccount(OAuthAccount):
        AUTH_URL="https://accounts.google.com/o/oauth2/auth"
        TOKEN_URL="https://accounts.google.com/o/oauth2/token"
    
        def __init__(self):
            OAuthAccount.__init__(self,
                                  client_id=client_id,
                                  client_secret=client_secret,
                                  auth_url=self.AUTH_URL,
                                  token_url=self.TOKEN_URL,
                                  approval_prompt='force',
                                  state='auth_provider=google',
                                  scope='https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email')
    
        def get_user(self):
            token = self.accessToken()
            if not token:
                return None
    
            uinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo?access_token=%s' % urllib2.quote(token, safe='')
            uinfo = None
            try:
                uinfo_stream = urllib2.urlopen(uinfo_url)
            except:
                session.token = None
                return
            data = uinfo_stream.read()
            uinfo = json.loads(data)
            return dict(first_name = uinfo['given_name'],
                            last_name = uinfo['family_name'],
                            username = uinfo['id'], email=uinfo['email'])
    
    
    #auth.settings.actions_disabled=['register', 'change_password','request_reset_password','profile']
    #auth.settings.login_form=googleAccount()
