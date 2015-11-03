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
           [DIV(T('Help'),_class='menu16'), False, auth.settings.login_url,
            [
              ['', False, '',
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
gids = user_org_group_ids()

def groups_common_hidden_menu_entries():
    if len(gids) == 0:
        return []
    sql = """select t.menu_entry from (
              select menu_entry,count(hme.id) as n
              from group_hidden_menu_entries hme
               join auth_group g on hme.group_id=g.id
              where
               hme.group_id in (%(group_ids)s) and
               g.privilege='F'
              group by hme.menu_entry
             ) t
             where t.n=%(n)d
          """ % dict(group_ids=','.join(map(lambda x: str(x), gids)), n=len(gids))
    rows = db.executesql(sql)
    return [r[0] for r in rows]

def display(s, privs=[]):
    # display menu entries if the user has one of the specified privilege
    if len(privs) > 0 and len(set(privs) & ug) == 0:
        return False

    try:
        if s in config.menu_hidden_entries:
             return False
    except:
        pass

    if s in groups_common_hidden_menu_entries():
        return False

    return True

menu_entries = [
  'key-l',
  'key-n',
  'key-r',
  'key-s',
  'key-esc',
  'view-dashboard',
  'view-services',
  'view-service-instances',
  'view-resources',
  'view-appinfo',
  'view-nodes',
  'view-tagattach',
  'view-actions',
  'view-checks',
  'view-pkg',
  'view-patch',
  'view-net',
  'view-node-net',
  'view-node-san',
  'view-san',
  'view-dns',
  'view-saves',
  'view-disks',
  'view-arrays',
  'comp-status',
  'comp-log',
  'comp-modsets',
  'comp-rsets',
  'comp-designer',
  'comp-node-rset',
  'comp-node-modset',
  'comp-svc-rset',
  'comp-svc-modset',
  'stat-reports',
  'stat-site',
  'stat-compare',
  'stat-os-lifecycle',
  'stat-avail',
  'req-new',
  'req-pending-my',
  'req-pending-tiers',
  'req-all',
  'adm-usr',
  'adm-log',
  'adm-obs',
  'adm-app',
  'adm-drp',
  'adm-batchs',
  'adm-bill',
  'adm-prov',
  'adm-filters',
  'adm-forms',
  'adm-metrics',
  'adm-charts',
  'adm-reports',
  'adm-tags'
]

menu_entries_data = {
  'key-l': DIV(SPAN('l', _class='keyboard-key'), T("Link"), DIV(T("Show url to share your filters"))),
  'key-n': DIV(SPAN('n', _class='keyboard-key'), T("Navigation"), DIV(T("Open the navigation menu"))),
  'key-r': DIV(SPAN('r', _class='keyboard-key'), T("Refresh"), DIV(T("Reload table data"))),
  'key-s': DIV(SPAN('s', _class='keyboard-key'), T("Search"), DIV(T("Focus the global search tool"))),
  'key-esc': DIV(SPAN('Esc', _class='keyboard-key'), T("Unfocus"), DIV(T("Close pop-ups and menus"))),
  'help-api': DIV(T("Rest API"), DIV(T("Documentation")), _class="api48", _style='background-size:40px 40px'),
  'view-dashboard': DIV(T('Dashboard'), DIV(T("Current issues on nodes and services")), _class='alert48', _style='background-size:40px 40px'),
  'view-service-instances': DIV(T('Services Instances'), DIV(T("Service instances status")), _class='svc48'),
  'view-services': DIV(T('Services'), DIV(T("Services information and status")), _class='svc48'),
  'view-resources': DIV(T('Resources'), DIV(T("Service resources status")), _class='svc48'),
  'view-appinfo': DIV(T('App Info'), DIV(T("Service 'app' resources key:val store")), _class='svc48'),
  'view-nodes': DIV(T('Nodes'), DIV(T("Technical and organizational info")), _class='node48', _style='background-size:40px 40px'),
  'view-tagattach': DIV(T('Tag Attachments'), DIV(T("Tags attached to nodes and services")), _class='tag48', _style='background-size:40px 40px'),
  'view-actions': DIV(T('Actions'), DIV(T("Service actions log")), _class='action48', _style='background-size:40px 40px'),
  'view-checks': DIV(T('Checks'), DIV(T("Nodes health monitoring")), _class='completed48'),
  'view-pkg': DIV(T('Packages'), DIV(T("All packages installed on nodes")), _class='pkg48'),
  'view-patch': DIV(T('Patches'), DIV(T("All patches installed on nodes")), _class='pkg48'),
  'view-net': DIV(T('Networks'), DIV(T("Known subnets, gateways, vlans, ...")), _class='net48'),
  'view-node-net': DIV(T('Node Networks'), DIV(T("Node ips with their network information")), _class='net48'),
  'view-node-san': DIV(T('Node SAN'), DIV(T("Node SAN ports with their fabric information")), _class='net48'),
  'view-san': DIV(T('SAN switches'), DIV(T("Ports id, state, remote ports")), _class='net48'),
  'view-dns': DIV(T('Domain Name Service'), DIV(T("Internal dns zones and records")), _class='dns48'),
  'view-saves': DIV(T('Saves'), DIV(T("Backup servers aggregated index")), _class='backup48', _style='background-size:40px 40px'),
  'view-disks': DIV(T('Disks'), DIV(T("All known disks with their array information")), _class='disk48', _style='background-size:40px 40px'),
  'view-arrays': DIV(T('Storage Arrays'), DIV(T("Symmetrix detailled information")), _class='disk48', _style='background-size:40px 40px'),
  'comp-status': DIV(T('Status'), DIV(T("Nodes and service last configuration checks")), _class='completed48'),
  'comp-log': DIV(T('Log'), DIV(T("All configuration checks and fixes")), _class='log48', _style='background-size:40px 40px'),
  'comp-modsets': DIV(T('Modulesets'), DIV(T("Search-optimized modules grouping view")), _class='action48', _style='background-size:40px 40px'),
  'comp-rsets': DIV(T('Rulesets'), DIV(T("Search-optimized target configurations view")), _class='comp48', _style='background-size:40px 40px'),
  'comp-designer': DIV(T('Designer'), DIV(T("Creation-optimized configuration targets tool")), _class='wf48'),
  'comp-node-rset': DIV(T('Node rulesets'), DIV(T("Mass attach and detach tool")), _class='rsetattach48', _style='background-size:40px 40px'),
  'comp-node-modset': DIV(T('Node modulesets'), DIV(T("Mass attach and detach tool")), _class='modsetattach48', _style='background-size:40px 40px'),
  'comp-svc-rset': DIV(T('Service rulesets'), DIV(T("Mass attach and detach tool")), _class='rsetattach48', _style='background-size:40px 40px'),
  'comp-svc-modset': DIV(T('Service modulesets'), DIV(T("Mass attach and detach tool")), _class='modsetattach48', _style='background-size:40px 40px'),
  'stat-reports': DIV(T('Reports'), DIV(T("User-defined reports")), _class='stats48', _style='background-size:40px 40px'),
  'stat-site': DIV(T('Site'), DIV(T("Pre-defined site report")), _class='stats48', _style='background-size:40px 40px'),
  'stat-compare': DIV(T('Compare'), DIV(T("Compare node and service subsets evolution")), _class='stats48', _style='background-size:40px 40px'),
  'stat-os-lifecycle': DIV(T('Os lifecycle'), DIV(T("Operating systems dispatch evolution")), _class='stats48', _style='background-size:40px 40px'),
  'stat-avail': DIV(T('Availability'), DIV(T("Service outage timelines")), _class='avail48', _style='background-size:40px 40px'),
  'req-new': DIV(T('New request'), DIV(T("Start a new workflow or orchestration")), _class='wf48'),
  'req-pending-my': DIV(T('Assigned to my team'), DIV(T("Workflows waiting for action from my team")), _class='wf48'),
  'req-pending-tiers': DIV(T('Pending tiers action'), DIV(T("Workflows started by my team waiting action from a tier")), _class='wf48'),
  'req-all': DIV(T('All requests'), DIV(T("Workflow and orchestration history")), _class='wf48'),
  'adm-usr': DIV(T('Users'), DIV(T("Users and group administration")), _class='guys48', _style='background-size:40px 40px'),
  'adm-log': DIV(T('Log'), DIV(T("Collector events log")), _class='log48', _style='background-size:40px 40px'),
  'adm-obs': DIV(T('Obsolescence setup'), DIV(T("Set server models and os releases obsolescence dates")), _class='obs48'),
  'adm-app': DIV(T('Applications'), DIV(T("Application codes assigned to nodes and services")), _class='svc48'),
  'adm-drp': DIV(T('Drplan'), DIV(T("Designer for disaster recovery plans")), _class='drp48'),
  'adm-batchs': DIV(T('Batchs'), DIV(T("Collector janitoring batchs")), _class='action48', _style='background-size:40px 40px'),
  'adm-bill': DIV(T('Billing'), DIV(T("Licensing tokens count and dispatch")), _class='billing48', _style='background-size:40px 40px'),
  'adm-prov': DIV(T('Provisioning'), DIV(T("Create service provisioning templates")), _class='prov48'),
  'adm-filters': DIV(T('Filters'), DIV(T("Create new filtersets")), _class='filter48', _style='background-size:40px 40px'),
  'adm-forms': DIV(T('Forms'), DIV(T("Design new workflows and orchestrations")), _class='wf48'),
  'adm-metrics': DIV(T('Metrics'), DIV(T("Design sql requests to embed in charts")), _class='stats48', _style='background-size:40px 40px'),
  'adm-charts': DIV(T('Charts'), DIV(T("Design charts to embed in reports")), _class='stats48', _style='background-size:40px 40px'),
  'adm-reports': DIV(T('Reports'), DIV(T("Design custom reports")), _class='stats48', _style='background-size:40px 40px'),
  'adm-tags': DIV(T('Tags'), DIV(T("Manage tag properties")), _class='tag48', _style='background-size:40px 40px'),
}

response.menu = [
  [DIV(T('Navigation'), _class="menu16"), False, '',
    [
    [T('Shortcuts'), False, '',
         [
             [menu_entries_data['key-l'], display('key-l'), ''],
             [menu_entries_data['key-n'], display('key-n'), ''],
             [menu_entries_data['key-r'], display('key-r'), ''],
             [menu_entries_data['key-s'], display('key-s'), ''],
             [menu_entries_data['key-esc'], display('key-esc'), ''],
             [menu_entries_data['help-api'], display('help-api'), URL(request.application,'rest','doc')],
         ]
    ],
    [T('Views'), False, '',
         [
             [menu_entries_data['view-dashboard'], display('view-dashboard'), URL(request.application,'dashboard','index')],
             [menu_entries_data['view-services'], display('view-services'), URL(request.application,'services','services')],
             [menu_entries_data['view-service-instances'], display('view-service-instances'), URL(request.application,'default','svcmon')],
             [menu_entries_data['view-resources'], display('view-resources'), URL(request.application,'resmon','resmon')],
             [menu_entries_data['view-appinfo'], display('view-appinfo'), URL(request.application,'appinfo','appinfo')],
             [menu_entries_data['view-nodes'], display('view-nodes'), URL(request.application,'nodes','nodes')],
             [menu_entries_data['view-tagattach'], display('view-tagattach'), URL(request.application,'tags','tagattach')],
             [menu_entries_data['view-actions'], display('view-actions'), URL(request.application,'svcactions','svcactions')],
             [menu_entries_data['view-checks'], display('view-checks'), URL(request.application,'checks','checks')],
             [menu_entries_data['view-pkg'], display('view-pkg'), URL(request.application,'packages','packages')],
             [menu_entries_data['view-patch'], display('view-patch'), URL(request.application,'patches','patches')],
             [menu_entries_data['view-net'], display('view-net'), URL(request.application,'networks','networks')],
             [menu_entries_data['view-node-net'], display('view-node-net'), URL(request.application,'nodenetworks','nodenetworks')],
             [menu_entries_data['view-node-san'], display('view-node-san'), URL(request.application,'nodesan','nodesan')],
             [menu_entries_data['view-san'], display('view-san'), URL(request.application,'sanswitches','sanswitches')],
             [menu_entries_data['view-dns'], display('view-dns'), URL(request.application,'dns','dns')],
             [menu_entries_data['view-saves'], display('view-saves'), URL(request.application,'saves','saves')],
             [menu_entries_data['view-disks'], display('view-disks'), URL(request.application,'disks','disks')],
             [menu_entries_data['view-arrays'], display('view-arrays'), URL(request.application,'sym','index')],
         ]
    ],
    [T('Compliance'), False, '',
         [
             [menu_entries_data['comp-status'], display('comp-status'), URL(request.application,'compliance','comp_status')],
             [menu_entries_data['comp-log'], display('comp-log'), URL(request.application,'compliance','comp_log')],
             [menu_entries_data['comp-modsets'], display('comp-modsets'), URL(request.application,'compliance','comp_modules')],
             [menu_entries_data['comp-rsets'], display('comp-rsets'), URL(request.application,'compliance','comp_rules')],
             [menu_entries_data['comp-designer'], display('comp-designer'), URL(request.application,'compliance','comp_admin', vars={"obj_filter": "opensvc"})],
             [menu_entries_data['comp-node-rset'], display('comp-node-rset'), URL(request.application,'compliance','comp_rulesets_nodes_attachment')],
             [menu_entries_data['comp-node-modset'], display('comp-node-modset'), URL(request.application,'compliance','comp_modulesets_nodes')],
             [menu_entries_data['comp-svc-rset'], display('comp-svc-rset'), URL(request.application,'compliance','comp_rulesets_services_attachment')],
             [menu_entries_data['comp-svc-modset'], display('comp-svc-modset'), URL(request.application,'compliance','comp_modulesets_services')],
         ]
    ],
    [T('Statistics'), False, '',
         [
             [menu_entries_data['stat-reports'], display('stat-reports'), URL(request.application,'charts','reports')],
             [menu_entries_data['stat-site'], display('stat-site'), URL(request.application,'stats','stats')],
             [menu_entries_data['stat-compare'], display('stat-compare'), URL(request.application,'stats','compare')],
             [menu_entries_data['stat-os-lifecycle'], display('stat-os-lifecycle'), URL(request.application,'lifecycle','lifecycle_os')],
             [menu_entries_data['stat-avail'], display('stat-avail'), URL(request.application,'svcmon_log','svcmon_log')],
         ]
    ],
    [T('Requests'), False, '',
         [
             [menu_entries_data['req-new'], display('req-new'), URL(request.application,'forms','forms')],
             [menu_entries_data['req-pending-my'], display('req-pending-my'), URL(request.application,'forms','workflows_assigned_to_me')],
             [menu_entries_data['req-pending-tiers'], display('req-pending-tiers'), URL(request.application,'forms','workflows_pending_tiers_action')],
             [menu_entries_data['req-all'], display('req-all'), URL(request.application,'forms','workflows')],
         ]
    ],
    [T('Administration'), False, '',
         [
             [menu_entries_data['adm-usr'], display('adm-usr', privs=['Manager']), URL(request.application,'users','users')],
             [menu_entries_data['adm-log'], display('adm-log'), URL(request.application,'log','log')],
             [menu_entries_data['adm-obs'], display('adm-obs'), URL(request.application,'obsolescence','obsolescence_config')],
             [menu_entries_data['adm-app'], display('adm-app'), URL(request.application,'apps','apps')],
             [menu_entries_data['adm-drp'], display('adm-drp'), URL(request.application,'drplan','drplan')],
             [menu_entries_data['adm-batchs'], display('adm-batchs', privs=['Manager']), URL(request.application,'batchs','batchs')],
             [menu_entries_data['adm-bill'], display('adm-bill', privs=['Manager']), URL(request.application,'billing','billing')],
             [menu_entries_data['adm-prov'], display('adm-prov', privs=['ProvisioningManager', 'Manager']), URL(request.application,'provisioning','prov_admin')],
             [menu_entries_data['adm-filters'], display('adm-filters'), URL(request.application,'compliance','comp_filters')],
             [menu_entries_data['adm-forms'], display('adm-forms'), URL(request.application,'forms','forms_admin')],
             [menu_entries_data['adm-metrics'], display('adm-metrics'), URL(request.application,'charts','metrics_admin')],
             [menu_entries_data['adm-charts'], display('adm-charts'), URL(request.application,'charts','charts_admin')],
             [menu_entries_data['adm-reports'], display('adm-reports'), URL(request.application,'charts','reports_admin')],
             [menu_entries_data['adm-tags'], display('adm-tags'), URL(request.application,'tags','tags')],
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
                     _onclick="""$(this).children("div").toggle("fold");$("#search_input").focus()"""
                   )
        return ul


