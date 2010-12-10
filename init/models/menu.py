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
           [SPAN(T('Login'),_class='guy16'), False, auth.settings.login_url,
            [
                   [T('Register'), False,
                    URL(request.application,'default','user/register')],
                   [T('Lost Password'), False,
                    URL(request.application,'default','user/retrieve_password')]]
            ],
           ]
    else:
        response.menu_auth = [
            [SPAN(auth.user.first_name, _class='guy16'),False,None,
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
now=datetime.datetime.today()
yesterday = str(now-datetime.timedelta(days=1))
sevendays = str(now-datetime.timedelta(days=7,
                                       hours=now.hour,
                                       minutes=now.minute,
                                       seconds=now.second,
                                       microseconds=now.microsecond))
response.menu = [
    [T('Dashboard'), _f == 'index',
     URL(request.application,'default','index'), []],
    [T('Views'), False, '',
         [
             [T('Services'), False,
              URL(request.application,'default','svcmon')],
             [T('Nodes'), False,
              URL(request.application,'nodes','nodes')],
             [T('Actions'), False,
              URL(request.application,'svcactions','svcactions',
                  vars={'actions_f_begin': '>'+yesterday,
                        'actions_f_status_log': 'empty',
                        'clear_filters': 'true'})],
             [T('Checks'), False,
              URL(request.application,'checks','checks')],
             [T('Packages'), False,
              URL(request.application,'packages','packages')],
             [T('Patches'), False,
              URL(request.application,'patches','patches')],
             [T('Compliance'), False,
              URL(request.application,'compliance','comp_status',
                  vars={'0_f_run_date': '>'+sevendays,
                        'clear_filters': 'true'})],
             [T('Storage'), False,
              URL(request.application,'sym','index')],
         ]
    ],
    [T('Stats'), False, '',
         [
             [T('Site'), False,
              URL(request.application,'stats','stats')],
             [T('Os lifecycle'), False,
              URL(request.application,'lifecycle','lifecycle_os')],
             [T('Availability'), False,
              URL(request.application,'svcmon_log','svcmon_log')],
             [T('Alerts'), False,
              URL(request.application,'alerts','alerts')],
         ]
    ],
    [T('Admin'), False, '',
         [
             [T('Users'), False,
              URL(request.application,'users','users')],
             [T('Log'), False,
              URL(request.application,'log','log')],
             [T('Obsolescence setup'), False,
              URL(request.application,'obsolescence','obsolescence_config')],
             [T('Applications'), False,
              URL(request.application,'apps','apps')],
             [T('Drplan'), False,
              URL(request.application,'drplan','drplan')],
             [T('Billing'), False,
              URL(request.application,'billing','billing')],
         ]
    ],
]
