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

def menu_fmt_e(title, subtitle, _class, icontext=""):
    d = DIV(
      DIV(icontext, _class="menu_icon "+_class),
      DIV(
        DIV(T(title), _class="menu_title"),
        DIV(T(subtitle), _class="menu_subtitle"),
      ),
      _class="menu_box",
    )
    return d

if 'auth' in globals():
    if not auth.is_logged_in():
       response.menu_auth = [
           [DIV(T('Help'),_class='menu16'), False, auth.settings.login_url,
            [
              ['', False, '',
               [
                   [menu_fmt_e('Register', "Create a new user", "guy16"), True,
                    URL(request.application,'default','user/register')],
                   [menu_fmt_e('Lost Password', "Send a new password by email", "mail"), True,
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
                    [menu_fmt_e('Logout', "Reconnect as another user", "logout"), True,
                     URL(request.application,'default','user/logout')],
                    [menu_fmt_e('Edit Profile', "User name, alerting levels, ...", "guy16"), True,
                     URL(request.application,'default','user/profile')],
                    [menu_fmt_e('Change Password', "You need to know your current password", "key"), True,
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
  'key-l': menu_fmt_e("Link", "Show url to share your filters", "", "l"),
  'key-n': menu_fmt_e("Navigation", "Open the navigation menu", "", "n"),
  'key-r': menu_fmt_e("Refresh", "Reload table data", "", "r"),
  'key-s': menu_fmt_e("Search", "Focus the global search tool", "", "s"),
  'key-esc': menu_fmt_e("Unfocus", "Close pop-ups and menus", "", "ESC"),
  'help-api': menu_fmt_e("Rest API", "Documentation", "api"),
  'view-dashboard': menu_fmt_e('Dashboard', "Current issues on nodes and services", 'alert16'),
  'view-service-instances': menu_fmt_e('Services Instances', "Service instances status", 'svc'),
  'view-services': menu_fmt_e('Services', "Services information and status", 'svc'),
  'view-resources': menu_fmt_e('Resources', "Service resources status", 'svc'),
  'view-appinfo': menu_fmt_e('App Info', "Service 'app' resources key:val store", 'svc'),
  'view-nodes': menu_fmt_e('Nodes', "Technical and organizational info", 'node16'),
  'view-tagattach': menu_fmt_e('Tag Attachments', "Tags attached to nodes and services", 'tags'),
  'view-actions': menu_fmt_e('Actions', "Service actions log", 'actions'),
  'view-checks': menu_fmt_e('Checks', "Nodes health monitoring", 'check16'),
  'view-pkg': menu_fmt_e('Packages', "All packages installed on nodes", 'pkg16'),
  'view-patch': menu_fmt_e('Patches', "All patches installed on nodes", 'patch'),
  'view-net': menu_fmt_e('Networks', "Known subnets, gateways, vlans, ...", 'net16'),
  'view-node-net': menu_fmt_e('Node Networks', "Node ips with their network information", 'net16'),
  'view-node-san': menu_fmt_e('Node SAN', "Node SAN ports with their fabric information", 'net16'),
  'view-san': menu_fmt_e('SAN switches', "Ports id, state, remote ports", 'net16'),
  'view-dns': menu_fmt_e('Domain Name Service', "Internal dns zones and records", '', 'IN'),
  'view-saves': menu_fmt_e('Saves', "Backup servers aggregated index", 'save16'),
  'view-disks': menu_fmt_e('Disks', "All known disks with their array information", 'hd16'),
  'view-arrays': menu_fmt_e('Storage Arrays', "Symmetrix detailled information", 'hd16'),
  'comp-status': menu_fmt_e('Status', "Nodes and service last configuration checks", 'check16'),
  'comp-log': menu_fmt_e('Log', "All configuration checks and fixes", 'log16'),
  'comp-modsets': menu_fmt_e('Modulesets', "Search-optimized modules grouping view", 'actions'),
  'comp-rsets': menu_fmt_e('Rulesets', "Search-optimized target configurations view", 'comp16'),
  'comp-designer': menu_fmt_e('Designer', "Creation-optimized configuration targets tool", 'wf16'),
  'comp-node-rset': menu_fmt_e('Node rulesets', "Mass attach and detach tool", 'node16'),
  'comp-node-modset': menu_fmt_e('Node modulesets', "Mass attach and detach tool", 'node16'),
  'comp-svc-rset': menu_fmt_e('Service rulesets', "Mass attach and detach tool", 'svc'),
  'comp-svc-modset': menu_fmt_e('Service modulesets', "Mass attach and detach tool", 'svc'),
  'stat-reports': menu_fmt_e('Reports', "User-defined reports", 'spark16'),
  'stat-site': menu_fmt_e('Site', "Pre-defined site report", 'spark16'),
  'stat-compare': menu_fmt_e('Compare', "Compare node and service subsets evolution", 'spark16'),
  'stat-os-lifecycle': menu_fmt_e('Os lifecycle', "Operating systems dispatch evolution", 'spark16'),
  'stat-avail': menu_fmt_e('Availability', "Service outage timelines", 'avail16'),
  'req-new': menu_fmt_e('New request', "Start a new workflow or orchestration", 'wf16'),
  'req-pending-my': menu_fmt_e('Assigned to my team', "Workflows waiting for action from my team", 'wf16'),
  'req-pending-tiers': menu_fmt_e('Pending tiers action', "Workflows started by my team waiting action from a tier", 'wf16'),
  'req-all': menu_fmt_e('All requests', "Workflow and orchestration history", 'wf16'),
  'adm-usr': menu_fmt_e('Users', "Users and group administration", 'guys16'),
  'adm-log': menu_fmt_e('Log', "Collector events log", 'log16'),
  'adm-obs': menu_fmt_e('Obsolescence setup', "Set server models and os releases obsolescence dates", 'obs16'),
  'adm-app': menu_fmt_e('Applications', "Application codes assigned to nodes and services", 'svc'),
  'adm-drp': menu_fmt_e('Drplan', "Designer for disaster recovery plans", 'drp16'),
  'adm-batchs': menu_fmt_e('Batchs', "Collector janitoring batchs", 'actions'),
  'adm-bill': menu_fmt_e('Billing', "Licensing tokens count and dispatch", 'bill16'),
  'adm-prov': menu_fmt_e('Provisioning', "Create service provisioning templates", 'prov'),
  'adm-filters': menu_fmt_e('Filters', "Create new filtersets", 'filter16'),
  'adm-forms': menu_fmt_e('Forms', "Design new workflows and orchestrations", 'wf16'),
  'adm-metrics': menu_fmt_e('Metrics', "Design sql requests to embed in charts", 'spark16'),
  'adm-charts': menu_fmt_e('Charts', "Design charts to embed in reports", 'spark16'),
  'adm-reports': menu_fmt_e('Reports', "Design custom reports", 'spark16'),
  'adm-tags': menu_fmt_e('Tags', "Manage tag properties", 'tags'),
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
                     _onclick="""$(this).children("div").toggle("fold");$("#search_input").focus();"""
                   )
        return ul


