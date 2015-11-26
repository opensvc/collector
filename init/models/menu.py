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
menu_entries = [
  'key-f',
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
#  'view-arrays',
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
                     _onclick="""$(this).children("div").toggle("fold", function(){filter_menu()});$("#search_input").focus();"""
                   )
        return ul


