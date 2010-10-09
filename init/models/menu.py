# coding: utf8

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = T('OpenSVC')
#response.subtitle = T('datacenter control tower')
_f = request.function

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
    [T('dashboard'), _f == 'index',
     URL(request.application,'default','index'), []],
    [T('views'), False, '',
         [
             [T('services'), False,
              URL(request.application,'default','svcmon')],
             [T('nodes'), False,
              URL(request.application,'nodes','nodes')],
             [T('actions'), False,
              URL(request.application,'svcactions','svcactions?begin=>'+yesterday+'&status_log=empty')],
             [T('checks'), False,
              URL(request.application,'checks','checks')],
             [T('packages'), False,
              URL(request.application,'packages','packages')],
             [T('patches'), False,
              URL(request.application,'patches','patches')],
         ]
    ],
    [T('stats'), False, '',
         [
             [T('site'), False,
              URL(request.application,'stats','stats')],
             [T('os lifecycle'), False,
              URL(request.application,'lifecycle','lifecycle_os')],
             [T('availability'), False,
              URL(request.application,'svcmon_log','svcmon_log')],
             [T('alerts'), False,
              URL(request.application,'alerts','alerts')],
         ]
    ],
    [T('admin'), False, '',
         [
             [T('users'), False,
              URL(request.application,'users','users')],
             [T('obsolescence setup'), False,
              URL(request.application,'obsolescence','obsolescence_config')],
             [T('applications'), False,
              URL(request.application,'apps','apps')],
             [T('drplan'), False,
              URL(request.application,'drplan','drplan')],
             [T('billing'), False,
              URL(request.application,'billing','billing')],
         ]
    ],
]
