# coding: utf8

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = T('OpenSVC')
#response.subtitle = T('datacenter control tower')

##########################################
## this is the authentication menu
## remove if not necessary
##########################################

if 'auth' in globals():
    if not auth.is_logged_in():
       response.menu_auth = [
           [T('Login'), False, auth.settings.login_url,
            [
                   [T('Register'), False,
                    URL(request.application,'default','user/register')],
                   [T('Lost Password'), False,
                    URL(request.application,'default','user/retrieve_password')]]
            ],
           ]
    else:
        response.menu_auth = [
            [auth.user.first_name,False,None,
             [
                    [T('Logout'), False, 
                     URL(request.application,'default','user/logout')],
                    [T('Edit Profile'), False, 
                     URL(request.application,'default','user/profile')],
                    [T('Change Password'), False,
                     URL(request.application,'default','user/change_password')],
             ],
            ],
        ]

##########################################
## this is the main application menu
## add/remove items as required
##########################################

import datetime
yesterday = str(datetime.datetime.today()-datetime.timedelta(days=1))
response.menu = [
  [T('Views'), False, None,
    [
    [T('svcmon'), False, 
     URL(request.application,'default','svcmon'), []],
    [T('actions'), False, 
     URL(request.application,'default','svcactions?begin=>'+yesterday), []],
    [T('drplan'), False, 
     URL(request.application,'default','drplan'), []],
    [T('applications'), False, 
     URL(request.application,'default','apps'), []],
   ],
  ],
]
