def _drplan_scripts_header(phase):
    l = ["""#!/bin/sh"""]
    l += ["""if [ "`id -u`" != "0" ] ; then echo excute this script as root ; exit 1 ; fi"""]
    l += ["""echo Confirm excution of the '%s' disaster recovery phase"""%phase]
    l += ["""echo Type 'GO' to confirm"""]
    l += ["""read confirm"""]
    l += ["""if [ "$confirm" != "GO" ] ; then echo "aborted" ; exit 0 ; fi"""]
    l += ["""rm -f ~root/authorized_keys"""]
    l += ["""cat - <<EOF >/tmp/ssh_config_drp || exit 1"""]
    l += ['StrictHostKeyChecking=no']
    l += ['ForwardX11=no']
    l += ['PasswordAuthentication=no']
    l += ['ConnectTimeout=10']
    l += ['EOF']
    l += ['']
    return l

def _scripts(rows, title, action, nodecol=None, service=False):
    ssh = '/usr/bin/ssh -F /tmp/ssh_config_drp'
    cmd = '/service/bin/svcmgr'
    lines = _drplan_scripts_header(title)
    for row in rows:
        _cmd = ' '.join([ssh, row.services[nodecol], '--'])
        if service:
            _cmd += """ %s --service %s %s"""%(cmd, row.services.svc_name, action)
        else:
            _cmd += """ %s %s"""%(cmd, action)
        lines += ["""echo %s"""%_cmd]
        lines += [_cmd+' >/dev/null 2>&1 &']
    lines += ['']
    sh = '\n'.join(lines)
    nodes_nb = len(rows)
    return (sh, nodes_nb)

@auth.requires_login()
def drplan_scripts():
    q_drpnode_is_set = (db.services.svc_drpnode!=None)
    q_drpnode_is_set &= (db.services.svc_drpnode!='')
    q_autostart_is_set = (db.services.svc_autostart!=None)
    q_autostart_is_set &= (db.services.svc_autostart!='')
    q_wave_is_set = (db.drpservices.drp_wave!=None)&(db.drpservices.drp_wave!='')
    q_cur_project = (db.drpservices.drp_project_id==request.vars.prj)
    p = {}

    """stop/start DEV
    """
    query = q_drpnode_is_set & q_wave_is_set & q_cur_project
    dev_rows = db(query).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on(db.services.svc_name==db.drpservices.drp_svcname),groupby=db.services.svc_drpnode)
    (sh, node_nb) = _scripts(dev_rows, 'STOP DEV', 'stop', 'svc_drpnode')
    p['stopdev'] =  dict(action='stop', phase='DEV', sh=sh, node_nb=node_nb, shname='00_stop_dev.sh')
    (sh, node_nb) = _scripts(dev_rows, 'START DEV', 'startdev', 'svc_drpnode')
    p['startdev'] =  dict(action='start', phase='DEV', sh=sh, node_nb=node_nb, shname='15_start_dev.sh')

    """stop/start PRD
    """
    query = q_autostart_is_set & q_drpnode_is_set & q_wave_is_set & q_cur_project
    prd_rows = db(query).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on(db.services.svc_name==db.drpservices.drp_svcname),groupby=db.services.svc_autostart)
    (sh, node_nb) = _scripts(prd_rows, 'STOP PRD', 'stop', 'svc_autostart')
    p['stopprd'] =  dict(action='stop', phase='PRD', sh=sh, node_nb=node_nb, shname='01_stop_prd.sh')

    wquery = query & (db.drpservices.drp_wave==0)
    prd_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prj)),groupby=db.services.svc_name,orderby=(db.services.svc_autostart))
    (sh, node_nb) = _scripts(prd_rows, 'START PRD WAVE 0', 'start', 'svc_autostart')
    p['startprd0'] =  dict(action='start', phase='PRD WAVE 0', sh=sh, node_nb=node_nb, shname='11_start_prd0.sh')

    wquery = query & (db.drpservices.drp_wave==1)
    prd_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prj)),groupby=db.services.svc_name,orderby=(db.services.svc_autostart))
    (sh, node_nb) = _scripts(prd_rows, 'START PRD WAVE 1', 'start', 'svc_autostart')
    p['startprd1'] =  dict(action='start', phase='PRD WAVE 1', sh=sh, node_nb=node_nb, shname='12_start_prd1.sh')

    wquery = query & (db.drpservices.drp_wave==2)
    prd_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave,
db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prj)),groupby=db.services.svc_name,orderby=(db.services.svc_autostart))
    (sh, node_nb) = _scripts(prd_rows, 'START PRD WAVE 2', 'start', 'svc_autostart')
    p['startprd2'] =  dict(action='start', phase='PRD WAVE 2', sh=sh, node_nb=node_nb, shname='13_start_prd2.sh')

    wquery = query & (db.drpservices.drp_wave==3)
    prd_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave,
db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prj)),groupby=db.services.svc_name,orderby=(db.services.svc_autostart))
    (sh, node_nb) = _scripts(prd_rows, 'START PRD WAVE 3', 'start', 'svc_autostart')
    p['startprd3'] =  dict(action='start', phase='PRD WAVE 3', sh=sh, node_nb=node_nb, shname='14_start_prd3.sh')

    """stop/start DR
    """
    query = q_drpnode_is_set & q_wave_is_set & q_cur_project & q_drpnode_is_set
    dr_rows = db(query).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on(db.services.svc_name==db.drpservices.drp_svcname),groupby=db.services.svc_drpnode)
    (sh, node_nb) = _scripts(dr_rows, 'STOP DR', 'stop', 'svc_drpnode')
    p['stopdr'] =  dict(action='stop', phase='DR', sh=sh, node_nb=node_nb, shname='10_stop_dr.sh')

    wquery = query & (db.drpservices.drp_wave==0)
    dr_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave,
db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prj)),groupby=db.services.svc_name,orderby=(db.services.svc_drpnode))
    (sh, node_nb) = _scripts(dr_rows, 'START DR WAVE 0', 'start', 'svc_drpnode', service=True)
    p['startdr0'] =  dict(action='start', phase='DR WAVE 0', sh=sh, node_nb=node_nb, shname='02_start_dr0.sh')

    wquery = query & (db.drpservices.drp_wave==1)
    dr_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave,
db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prj)),groupby=db.services.svc_name,orderby=(db.services.svc_drpnode))
    (sh, node_nb) = _scripts(dr_rows, 'START DR WAVE 1', 'start', 'svc_drpnode', service=True)
    p['startdr1'] =  dict(action='start', phase='DR WAVE 1', sh=sh, node_nb=node_nb, shname='03_start_dr1.sh')

    wquery = query & (db.drpservices.drp_wave==2)
    dr_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave,
db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prj)),groupby=db.services.svc_name,orderby=(db.services.svc_drpnode))
    (sh, node_nb) = _scripts(dr_rows, 'START DR WAVE 2', 'start', 'svc_drpnode', service=True)
    p['startdr2'] =  dict(action='start', phase='DR WAVE 2', sh=sh, node_nb=node_nb, shname='04_start_dr2.sh')

    wquery = query & (db.drpservices.drp_wave==3)
    dr_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave,
db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prj)),groupby=db.services.svc_name,orderby=(db.services.svc_drpnode))
    (sh, node_nb) = _scripts(dr_rows, 'START DR WAVE 3', 'start', 'svc_drpnode', service=True)
    p['startdr3'] =  dict(action='start', phase='DR WAVE 3', sh=sh, node_nb=node_nb, shname='05_start_dr3.sh')

    return dict(p=p)

def _drplan_script_write(fpath, buff):
    import os
    f = open(fpath, 'w')
    f.write(buff)
    f.close()
    os.chmod(fpath, 0755)
    return fpath

def drplan_scripts_archive():
    import os
    import tarfile
    import tempfile
    import gluon.contenttype
    r = drplan_scripts()
    p = r['p']
    dir = tempfile.mkdtemp()
    olddir = os.getcwd()
    os.chdir(dir)
    tarpath = "dr_scripts.tar"
    tar = tarfile.open(tarpath, "w")
    for key in p.keys():
        _drplan_script_write(p[key]['shname'], p[key]['sh'])
        tar.add(p[key]['shname'])
    tar.close()
    response.headers['Content-Type']=gluon.contenttype.contenttype('.tar')
    f = open(tarpath, 'r')
    buff = f.read()
    f.close()
    for key in p.keys():
        os.unlink(p[key]['shname'])
    os.unlink(tarpath)
    os.chdir(olddir)
    os.rmdir(dir)
    return buff

@auth.requires_membership('Manager')
def clone_project():
    prj = request.vars.prj
    new = request.vars.clone_project_i
    q = db.drpprojects.drp_project==new
    prj_rows = db(q).select(db.drpprojects.drp_project_id)
    if len(prj_rows) != 0:
        raise ToolError("project '%(prj)s' already exists", dict(prj=new))
    db.drpprojects.insert(drp_project=new)
    q = db.drpprojects.drp_project==new
    dst_prj = db(q).select(db.drpprojects.drp_project_id).first()
    q = db.drpservices.drp_project_id==prj
    src_prj_rows = db(q).select(db.drpservices.drp_project_id,
                                db.drpservices.drp_svcname,
                                db.drpservices.drp_wave,)
    for row in src_prj_rows:
        db.drpservices.insert(drp_svcname=row.drp_svcname,
                              drp_wave=row.drp_wave,
                              drp_project_id=dst_prj.drp_project_id)
    q = db.drpprojects.drp_project_id==prj
    src_prj = db(q).select(db.drpprojects.drp_project).first()
    _log('drp.project.clone',
         "project '%(dst)s' cloned from '%(src)s'. %(num)s services DR configurations ported to the new project",
         dict(dst=new, src=src_prj.drp_project, num=len(src_prj_rows)))
    request.vars.prj = str(dst_prj.drp_project_id)
    del request.vars.clone_project_i

@auth.requires_membership('Manager')
def add_project():
    new = request.vars.add_project_i
    q = db.drpprojects.drp_project==new
    prj_rows = db(q).select(db.drpprojects.drp_project_id)
    if len(prj_rows) != 0:
        raise ToolError("project '%(prj)s' already exists", dict(prj=new))
    db.drpprojects.insert(drp_project=new)
    _log("drp.project.add",
         "project '%(prj)s' created",
         dict(prj=new))
    dst_prj = db(q).select(db.drpprojects.drp_project_id).first()
    request.vars.prj = str(dst_prj.drp_project_id)
    del request.vars.add_project_i

@auth.requires_membership('Manager')
def del_project():
    prj = request.vars.prj
    q = db.drpprojects.drp_project_id==prj
    p = db(q).select().first()
    num_deleted = db(q).delete()
    _log("drp.project.del",
         "project '%(p)s' deleted. %(num)s services DR configurations dropped.",
         dict(p=p.drp_project, num=num_deleted))

@auth.requires_membership('Manager')
def setwave(ids):
    if len(ids) == 0:
        raise ToolError(T("No service selected"))
    q = db.drpservices.drp_project_id==request.vars.prj
    q &= db.drpservices.drp_project_id==db.drpprojects.drp_project_id
    row = db(q).select().first()
    if row is None:
        raise ToolError(T("project id %(id)s not found"%dict(id=request.vars.prj)))
    prj_name = row.drpprojects.drp_project
    for id in ids:
        svc = db(db.v_svcmon.id==id).select().first().svc_name
        if request.vars.setwave == "clear":
            q = db.drpservices.drp_svcname == svc
            q &= db.drpservices.drp_project_id == request.vars.prj
            db(q).delete()
            _log('drp.wave.set',
                 'clear wave for service %(s)s in project %(p)s',
                 dict(s=svc, p=request.vars.prj))
        else:
            try:
                db.drpservices.insert(drp_svcname=svc,
                                      drp_wave=request.vars.setwave,
                                      drp_project_id=request.vars.prj)
            except:
                q = db.drpservices.drp_svcname == svc
                q &= db.drpservices.drp_project_id == request.vars.prj
                db(q).update(drp_wave=request.vars.setwave)
            _log('drp.wave.set',
                 'set wave %(w)s for service %(s)s in project %(p)s',
                 dict(w=request.vars.setwave, s=svc, p=prj_name))


class table_drplan(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['mon_svcname',
                     'drp_wave']
        self.cols += svcmon_cols
        self.cols += v_services_cols
        self.cols += v_nodes_cols
        self.colprops.update(v_services_colprops)
        self.colprops.update(svcmon_colprops)
        self.colprops.update(v_nodes_colprops)
        self.colprops.update({
            'drp_wave': HtmlTableColumn(
                title = 'Wave',
                table = 'drpservices',
                field = 'drp_wave',
                display = True,
                img = 'drp16',
            ),
        })
        self.colprops['mon_svcname'].display = True
        self.colprops['svc_app'].display = True
        self.colprops['svc_nodes'].display = True
        self.colprops['svc_drpnode'].display = True
        self.colprops['svc_drpnodes'].display = True
        for c in svcmon_cols + v_services_cols + v_nodes_cols + ['mon_svcname']:
            self.colprops[c].table = 'v_svcmon'
        for c in self.cols:
            self.colprops[c].t = self
        self.extraline = True
        self.checkboxes = True
        self.checkbox_id_table = 'v_svcmon'
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_drplan_col_values'
        self.additional_tools.append('tool_project')
        if 'Manager' in user_groups():
            self.additional_tools.append('tool_clone_project')
            self.additional_tools.append('tool_add_project')
            self.additional_tools.append('tool_del_project')
            self.additional_tools.append('tool_setwave')
            self.additional_tools.append('tool_gen')

    def tool_gen(self):
        d = DIV(
              A(
                T("Generate scripts"),
                _href=URL(r=request, f='drplan_scripts',
                          vars={'prj': request.vars.prj}),
              ),
              _class='floatw',
            )
        return d

    def tool_setwave(self):
        l = []
        for i in ['clear'] + range(0, 4):
            vars = dict(setwave=i, prj=request.vars.prj)
            l.append(P(A(
                       i,
                       _onclick=self.ajax_submit(args=['setwave'], vars=vars)
                     )))
        d = DIV(
              A(
                T("Set wave"),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div='wave'),
              ),
              DIV(
                SPAN(*l),
                _style='display:none',
                _class='white_float',
                _name='wave',
                _id='wave',
              ),
              _class='floatw',
            )
        return d

    def tool_add_project(self):
        return self._tool_add_project('New project', 'add_project')

    def tool_clone_project(self):
        return self._tool_add_project('Clone project', 'clone_project')

    def _tool_add_project(self, title, action):
        d = DIV(
              A(
                T(title),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div=action),
              ),
              DIV(
                TABLE(
                  TR(
                    TD(
                      T('New project name'),
                    ),
                    TD(
                      INPUT(
                       _id='%s_i'%action,
                       _onkeypress="if (is_enter(event)) {%s};"%\
                          self.ajax_submit(additional_inputs=['%s_i'%action],
                                           args=action,
                                           vars={'prj': request.vars.prj}),
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name=action,
                _id=action,
              ),
              _class='floatw',
            )
        return d

    def tool_del_project(self):
        rows = db().select(db.drpprojects.drp_project_id,
                           db.drpprojects.drp_project,
                           orderby=db.drpprojects.drp_project)
        l = []
        prj_name = None
        for r in rows:
            l.append(P(A(
                       r.drp_project,
                       _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                          text=T("Deleting a project also deletes its wave assignments. Please confirm project deletion"),
                          s=self.ajax_submit(args='del_project',
                                             vars={'prj': r.drp_project_id})),
                     )))
        d = DIV(
              A(
                T("Delete project"),
                _onclick="""click_toggle_vis('%(div)s', 'block');"""%dict(
                      div='del_project'),
              ),
              DIV(
                SPAN(*l),
                _style='display:none',
                _class='white_float',
                _name='del_project',
                _id='del_project',
              ),
              _class='floatw',
            )
        return d

    def tool_project(self):
        rows = db().select(db.drpprojects.drp_project_id,
                           db.drpprojects.drp_project,
                           orderby=db.drpprojects.drp_project)
        l = []
        prj_name = None
        for r in rows:
            if str(r.drp_project_id) == request.vars.prj:
                l.append(P(r.drp_project, _style='color:rgba(0,0,0,0.5);'))
                prj_name = r.drp_project
            else:
                l.append(P(A(
                           r.drp_project,
                           _onclick=self.ajax_submit(vars={'prj': r.drp_project_id})
                         )))
        if prj_name is None:
            s = B(T("Choose project"))
        else:
            s = SPAN(T("Project "), B(prj_name))
        d = DIV(
              A(
                s,
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div='project'),
              ),
              DIV(
                SPAN(*l),
                _style='display:none',
                _class='white_float',
                _name='project',
                _id='project',
              ),
              _class='floatw',
            )
        return d


@auth.requires_login()
def ajax_drplan_col_values():
    t = table_drplan('drplan', 'ajax_drplan')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    j = db.v_svcmon.svc_name==db.drpservices.drp_svcname
    j &= db.drpservices.drp_project_id==request.vars.prj
    q = db.v_svcmon.svc_drpnode!=None
    q &= db.v_svcmon.svc_drpnode!=''
    q = _where(q, 'v_svcmon', domain_perms(), 'svc_name')
    q = apply_db_filters(q, 'v_svcmon')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(orderby=o,
                                 left=db.drpservices.on(j),
                                 groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_drplan():
    t = table_drplan('drplan', 'ajax_drplan')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'setwave':
                setwave(t.get_checked())
            elif action == 'clone_project':
                clone_project()
            elif action == 'add_project':
                add_project()
            elif action == 'del_project':
                del_project()
        except ToolError, e:
            t.flash = str(e)

    if 'prj' not in request.vars:
        prj = -1
    else:
        prj = request.vars.prj

    o = db.v_svcmon.svc_name

    j = db.v_svcmon.svc_name==db.drpservices.drp_svcname
    j &= db.drpservices.drp_project_id==prj

    q = db.v_svcmon.svc_drpnode!=None
    q &= db.v_svcmon.svc_drpnode!=''
    q = _where(q, 'v_svcmon', domain_perms(), 'mon_svcname')
    q = apply_db_filters(q, 'v_svcmon')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(db.v_svcmon.ALL,
                                 db.drpservices.drp_wave,
                                 db.drpservices.drp_project_id,
                                 left=db.drpservices.on(j),
                                 limitby=(t.pager_start,t.pager_end),
                                 groupby=o,
                                 orderby=o)
    return t.html()

@auth.requires_login()
def drplan():
    t = DIV(
          ajax_drplan(),
          _id='drplan',
        )
    return dict(table=t)


