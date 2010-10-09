@auth.requires_login()
def ajax_svc_message_save():
    vars = {
            'msg_svcname': request.vars.mon_svcname,
            'msg_last_editor': user_name(),
            'msg_last_edit_date':str(datetime.datetime.now()),
            'msg_body':request.vars['msgbody_'+request.vars.mon_svcname],
           }
    v = lambda x: "%(x)s=values(%(x)s)"%dict(x=x)
    r = lambda x: "'%(x)s'"%dict(x=x.replace("'",'"'))
    sql = """insert into svcmessages (%s) values (%s)
             on duplicate key update %s
          """%(
               ','.join(vars.keys()),
               ','.join(map(r, vars.values())),
               ','.join(map(v, vars.keys())),
              )
    db.executesql(sql)

@auth.requires_login()
def ajax_svc_message_load():
    rows = db(db.svcmessages.msg_svcname==request.vars.mon_svcname).select()
    if len(rows) != 1:
        return DIV(
                P(H3("%(svc)s"%dict(svc=request.vars.mon_svcname), _style="text-align:center")),
                P(T("new message"), _style="text-align:center"),
                TEXTAREA(_id='msgbody_'+request.vars.mon_svcname)
               )
    return DIV(
            H3(T("%(s)s messages",dict(s=rows[0].msg_svcname)), _style="text-align:center"),
            P(
              T("last edited on "),
              rows[0].msg_last_edit_date,
              BR(),
              T(" by "),
              rows[0].msg_last_editor,
            ),
            TEXTAREA(
              rows[0].msg_body,
              _id='msgbody_'+rows[0].msg_svcname,
            ),
           )


