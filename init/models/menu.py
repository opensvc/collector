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
              [T('Login actions'), False, '',
               [
                   [DIV(T('Register'), DIV(T("Create a new user")), _class="guy48"), True,
                    URL(request.application,'default','user/register')],
                   [DIV(T('Lost Password'), DIV(T("Send a new password by email")), _class="key48"), True,
                    URL(request.application,'default','user/retrieve_password')]]
               ],
              ],
            ],
        ]
    else:
        response.menu_auth = [
            [DIV(auth.user.first_name, _class='guy16'),False,None,
             [
              [T('User actions'), False, '',
               [
                    [DIV(T('Logout'), DIV(T("Reconnect as another user")), _class="logout48"), True, 
                     URL(request.application,'default','user/logout')],
                    [DIV(T('Edit Profile'), DIV(T("User name, alerting levels, ...")), _class="guy48"), True, 
                     URL(request.application,'default','user/profile')],
                    [DIV(T('Change Password'), DIV(T("You need to know your current password")), _class="key48"), True,
                     URL(request.application,'default','user/change_password')],
               ],
              ],
             ],
            ],
        ]

##########################################
## this is the main application menu
## add/remove items as required
##########################################

import datetime
from applications.init.modules import config

now=datetime.datetime.today()
yesterday = str(now-datetime.timedelta(days=1))
sevendays = str(now-datetime.timedelta(days=7,
                                       hours=now.hour,
                                       minutes=now.minute,
                                       seconds=now.second,
                                       microseconds=now.microsecond))
ug = set(user_groups())

def display(s, privs=[]):
    # display menu entries if the user has not one of the specified privilege
    if len(privs) > 0 and len(set(privs) & ug) == 0:
        return False

    try:
        if s in config.menu_hidden_entries:
             return False
    except:
        pass
    return True

response.menu = [
  [DIV(T('Navigation'), _class="menu16"), False, '',
    [
    [T('Shortcuts'), False, '',
         [
             [DIV(
               SPAN('l', _class='keyboard-key'),
               T("Link"),
               DIV(T("Show url to share your filters")),
              ), display('key-l'), ''],
             [DIV(
               SPAN('n', _class='keyboard-key'),
               T("Navigation"),
               DIV(T("Open the navigation menu")),
              ), display('key-n'), ''],
             [DIV(
               SPAN('r', _class='keyboard-key'),
               T("Refresh"),
               DIV(T("Reload table data")),
              ), display('key-r'), ''],
             [DIV(
               SPAN('s', _class='keyboard-key'),
               T("Search"),
               DIV(T("Focus the global search tool")),
              ), display('key-s'), ''],
             [DIV(
               SPAN('Esc', _class='keyboard-key'),
               T("Unfocus"),
               DIV(T("Close pop-ups and menus")),
              ), display('key-esc'), ''],
         ]
    ],
    [T('Views'), False, '',
         [
             [DIV(T('Dashboard'), DIV(T("Current issues on nodes and services")), _class='alert48'), display('view-dashboard'),
              URL(request.application,'dashboard','index')],
             [DIV(T('Services'), DIV(T("Service instances status")), _class='svc48'), display('view-services'),
              URL(request.application,'default','svcmon')],
             [DIV(T('Resources'), DIV(T("Service resources status")), _class='svc48'), display('view-resources'),
              URL(request.application,'resmon','resmon')],
             [DIV(T('App Info'), DIV(T("Service 'app' resources key:val store")), _class='svc48'), display('view-appinfo'),
              URL(request.application,'appinfo','appinfo')],
             [DIV(T('Nodes'), DIV(T("Technical and organizational info")), _class='node48'), display('view-nodes'),
              URL(request.application,'nodes','nodes')],
             [DIV(T('Actions'), DIV(T("Service actions log")), _class='action48'), display('view-actions'),
              URL(request.application,'svcactions','svcactions')],
             [DIV(T('Checks'), DIV(T("Nodes health monitoring")), _class='completed48'), display('view-checks'),
              URL(request.application,'checks','checks')],
             [DIV(T('Packages'), DIV(T("All packages installed on nodes")), _class='pkg48'), display('view-pkg'),
              URL(request.application,'packages','packages')],
             [DIV(T('Patches'), DIV(T("All patches installed on nodes")), _class='pkg48'), display('view-patch'),
              URL(request.application,'patches','patches')],
             [DIV(T('Networks'), DIV(T("Known subnets, gateways, vlans, ...")), _class='net48'), display('view-net'),
              URL(request.application,'networks','networks')],
             [DIV(T('Node Networks'), DIV(T("Node ips with their network information")), _class='net48'), display('view-node-net'),
              URL(request.application,'nodenetworks','nodenetworks')],
             [DIV(T('Node SAN'), DIV(T("Node SAN ports with their fabric information")), _class='net48'), display('view-node-san'),
              URL(request.application,'nodesan','nodesan')],
             [DIV(T('SAN switches'), DIV(T("Ports id, state, remote ports")), _class='net48'), display('view-san'),
              URL(request.application,'sanswitches','sanswitches')],
             [DIV(T('Domain Name Service'), DIV(T("Internal dns zones and records")), _class='dns48'), display('view-dns'),
              URL(request.application,'dns','dns')],
             [DIV(T('Saves'), DIV(T("Backup servers aggregated index")), _class='backup48'), display('view-saves'),
              URL(request.application,'saves','saves')],
             [DIV(T('Disks'), DIV(T("All known disks with their array information")), _class='disk48'), display('view-disks'),
              URL(request.application,'disks','disks')],
             [DIV(T('Storage Arrays'), DIV(T("Symmetrix detailled information")), _class='disk48'), display('view-arrays'),
              URL(request.application,'sym','index')],
         ]
    ],
    [T('Compliance'), False, '',
         [
             [DIV(T('Status'), DIV(T("Nodes and service last configuration checks")), _class='completed48'), display('comp-status'),
              URL(request.application,'compliance','comp_status')],
             [DIV(T('Log'), DIV(T("All configuration checks and fixes")), _class='log48'), display('comp-log'),
              URL(request.application,'compliance','comp_log')],
             [DIV(T('Modulesets'), DIV(T("Search-optimized modules grouping view")), _class='action48'), display('comp-modsets'),
              URL(request.application,'compliance','comp_modules')],
             [DIV(T('Rulesets'), DIV(T("Search-optimized target configurations view")),  _class='comp48'), display('comp-rsets'),
              URL(request.application,'compliance','comp_rules')],
             [DIV(T('Designer'), DIV(T("Creation-optimized configuration targets tool")), _class='wf48'), display('comp-designer'),
              URL(request.application,'compliance','comp_admin')],
             [DIV(T('Node rulesets'), DIV(T("Mass attach and detach tool")), _class='rsetattach48'), display('comp-node-rset'),
              URL(request.application,'compliance','comp_rulesets_nodes_attachment')],
             [DIV(T('Node modulesets'), DIV(T("Mass attach and detach tool")), _class='modsetattach48'), display('comp-node-modset'),
              URL(request.application,'compliance','comp_modulesets_nodes')],
             [DIV(T('Service rulesets'), DIV(T("Mass attach and detach tool")), _class='rsetattach48'), display('comp-svc-rset'),
              URL(request.application,'compliance','comp_rulesets_services_attachment')],
             [DIV(T('Service modulesets'), DIV(T("Mass attach and detach tool")), _class='modsetattach48'), display('comp-svc-modset'),
              URL(request.application,'compliance','comp_modulesets_services')],
         ]
    ],
    [T('Statistics'), False, '',
         [
             [DIV(T('Reports'), DIV(T("User-defined reports")), _class='stats48'), display('stat-reports'),
              URL(request.application,'charts','reports')],
             [DIV(T('Site'), DIV(T("Pre-defined site report")), _class='stats48'), display('stat-site'),
              URL(request.application,'stats','stats')],
             [DIV(T('Compare'), DIV(T("Compare node and service subsets evolution")), _class='stats48'), display('stat-compare'),
              URL(request.application,'stats','compare')],
             [DIV(T('Os lifecycle'), DIV(T("Operating systems dispatch evolution")), _class='stats48'), display('stat-os-lifecycle'),
              URL(request.application,'lifecycle','lifecycle_os')],
             [DIV(T('Availability'), DIV(T("Service outage timelines")), _class='avail48'), display('stat-avail'),
              URL(request.application,'svcmon_log','svcmon_log')],
         ]
    ],
    [T('Requests'), False, '',
         [
             [DIV(T('New request'), DIV(T("Start a new workflow or orchestration")), _class='wf48'), display('req-new'),
              URL(request.application,'forms','forms')],
             [DIV(T('Assigned to my team'), DIV(T("Workflows waiting for action from my team")), _class='wf48'), display('req-pending-my'),
              URL(request.application,'forms','workflows_assigned_to_me')],
             [DIV(T('Pending tiers action'), DIV(T("Workflows started by my team waiting action from a tier")), _class='wf48'), display('req-pending-tiers'),
              URL(request.application,'forms','workflows_pending_tiers_action')],
             [DIV(T('All requests'), DIV(T("Workflow and orchestration history")), _class='wf48'), display('req-all'),
              URL(request.application,'forms','workflows')],
         ]
    ],
    [T('Administration'), False, '',
         [
             [DIV(T('Users'), DIV(T("Users and group administration")), _class='guys48'), display('adm-usr', privs=['Manager']),
              URL(request.application,'users','users')],
             [DIV(T('Log'), DIV(T("Collector events log")), _class='log48'), display('adm-log'),
              URL(request.application,'log','log')],
             [DIV(T('Obsolescence setup'), DIV(T("Set server models and os releases obsolescence dates")), _class='obs48'), display('adm-obs'),
              URL(request.application,'obsolescence','obsolescence_config')],
             [DIV(T('Applications'), DIV(T("Application codes assigned to nodes and services")), _class='svc48'), display('adm-app'),
              URL(request.application,'apps','apps')],
             [DIV(T('Drplan'), DIV(T("Designer for disaster recovery plans")), _class='drp48'), display('adm-drp'),
              URL(request.application,'drplan','drplan')],
             [DIV(T('Batchs'), DIV(T("Collector janitoring batchs")), _class='action48'), display('adm-batchs', privs=['Manager']),
              URL(request.application,'batchs','batchs')],
             [DIV(T('Billing'), DIV(T("Licensing tokens count and dispatch")), _class='billing48'), display('adm-bill', privs=['Manager']),
              URL(request.application,'billing','billing')],
             [DIV(T('Provisioning'), DIV(T("Create service provisioning templates")), _class='prov48'), display('adm-prov', privs=['ProvisioningManager', 'Manager']),
              URL(request.application,'provisioning','prov_admin')],
             [DIV(T('Filters'), DIV(T("Create new filtersets")), _class='filter48'), display('adm-filters'),
              URL(request.application,'compliance','comp_filters')],
             [DIV(T('Forms'), DIV(T("Design new workflows and orchestrations")), _class='wf48'), display('adm-forms'),
              URL(request.application,'forms','forms_admin')],
             [DIV(T('Metrics'), DIV(T("Design sql requests to embed in charts")), _class='stats48'), display('adm-metrics'),
              URL(request.application,'charts','metrics_admin')],
             [DIV(T('Charts'), DIV(T("Design charts to embed in reports")), _class='stats48'), display('adm-charts'),
              URL(request.application,'charts','charts_admin')],
             [DIV(T('Reports'), DIV(T("Design custom reports")), _class='stats48'), display('adm-reports'),
              URL(request.application,'charts','reports_admin')],
         ]
    ],
    ]
  ]
]

class OSVCMENU(MENU):
    def serialize(self, data, level=0):
        if level == 0:
            _data = data[0][3]
            level = 1
            ul = DIV(**self.attributes)
        else:
            _data = data
            ul = DIV(_class="")
        for item in _data:
           (name, active, link) = item[:3]
           if not active and len(item) == 3:
               continue
           if isinstance(link, DIV):
               li = DIV(link)
           elif 'no_link_url' in self.attributes and self['no_link_url'] == link:
               li = DIV(DIV(name))
           elif isinstance(link,dict):
               li = DIV(A(name, **link))
           elif link:
               li = DIV(A(name, _href=link))
           elif not link and isinstance(name, A):
               li = DIV(name)
           else:
               li = DIV(A(name, _href='#',
                         _onclick='javascript:void(0);return false;'))
           if level == 1 and item == _data[0]:
               li['_class'] = 'menu_item'
           elif level == 1 and item == _data[-1]:
               li['_class'] = 'menu_item'
           if len(item) > 3 and item[3]:
               li['_class'] = 'menu_section'
               deeper = self.serialize(item[3], level + 1)
               if len(deeper) > 0:
                   li.append(deeper)
               else:
                   li = SPAN()
           else:
               li['_class'] = 'menu_entry'
           if len(item) <= 4 or item[4] == True:
               ul.append(li)
        if level == 1:
            return DIV(
                     UL(LI(A(data[0][0])), _class="web2py-menu"),
                     ul,
                     _class="menu_top",
                     _onclick="""$(this).children("div").toggle("fade", 200)"""
                   )
        return ul


