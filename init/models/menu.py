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
           [DIV(T('Login'),_class='guy16'), False, auth.settings.login_url,
            [
                   [T('Register'), False,
                    URL(request.application,'default','user/register')],
                   [T('Lost Password'), False,
                    URL(request.application,'default','user/retrieve_password')]]
            ],
           ]
    else:
        response.menu_auth = [
            [DIV(auth.user.first_name, _class='guy16'),False,None,
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
    [XML('&diams;'), _f == '',
     '',[]],
    [T('Dashboard'), _f == 'index',
     URL(request.application,'dashboard','index'), []],
    [T('Views'), False, '',
         [
             [DIV(T('Services'), _class='svc'), False,
              URL(request.application,'default','svcmon')],
             [DIV(T('Nodes'), _class='node16'), False,
              URL(request.application,'nodes','nodes')],
             [DIV(T('Actions'), _class='action16'), False,
              URL(request.application,'svcactions','svcactions',
                  vars={'actions_f_begin': '>'+yesterday,
                        'actions_f_status_log': 'empty',
                        'clear_filters': 'true'})],
             [DIV(T('Checks'), _class='check16'), False,
              URL(request.application,'checks','checks')],
             [DIV(T('Packages'), _class='pkg16'), False,
              URL(request.application,'packages','packages')],
             [DIV(T('Patches'), _class='pkg16'), False,
              URL(request.application,'patches','patches')],
             [DIV(T('Compliance'), _class='comp16'), False,
              URL(request.application,'compliance','comp_status',
                  vars={'cs0_f_run_date': '>'+sevendays,
                        'clear_filters': 'true'})],
             [DIV(T('App Info'), _class='svc'), False,
              URL(request.application,'appinfo','appinfo')],
             [DIV(T('Networks'), _class='net16'), False,
              URL(request.application,'networks','networks')],
             [DIV(T('Domain Name Service'), _class='dns16'), False,
              URL(request.application,'dns','dns')],
             [DIV(T('Disks'), _class='hd16'), False,
              URL(request.application,'disks','disks')],
             [DIV(T('Storage Arrays'), _class='hd16'), False,
              URL(request.application,'sym','index')],
         ]
    ],
    [T('Stats'), False, '',
         [
             [DIV(T('Site'), _class='wspark16'), False,
              URL(request.application,'stats','stats')],
             [DIV(T('Compare'), _class='wspark16'), False,
              URL(request.application,'stats','compare')],
             [DIV(T('Os lifecycle'), _class='refresh16'), False,
              URL(request.application,'lifecycle','lifecycle_os')],
             [DIV(T('Availability'), _class='avail16'), False,
              URL(request.application,'svcmon_log','svcmon_log')],
         ]
    ],
    [T('Admin'), False, '',
         [
             [DIV(T('Users'), _class='guys16'), False,
              URL(request.application,'users','users')],
             [DIV(T('Log'), _class='log16'), False,
              URL(request.application,'log','log')],
             [DIV(T('Obsolescence setup'), _class='obs16'), False,
              URL(request.application,'obsolescence','obsolescence_config')],
             [DIV(T('Applications'), _class='svc'), False,
              URL(request.application,'apps','apps')],
             [DIV(T('Drplan'), _class='drp16'), False,
              URL(request.application,'drplan','drplan')],
             [DIV(T('Billing'), _class='bill16'), False,
              URL(request.application,'billing','billing')],
             [DIV(T('Provisioning'), _class='prov'), False,
              URL(request.application,'provisioning','prov_admin')],
             [DIV(T('Filters'), _class='filters'), False,
              URL(request.application,'compliance','comp_filters')],
         ]
    ],
]
