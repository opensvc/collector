from applications.init.modules import sysreport
import re

def show_diff_data(nodenames, diff_data, sysresponsible, sec_pattern):
    l = []
    max_blocks = 5
    stat_width = 30
    js = "$(this).next().toggle()"
    if len(diff_data['blocks']) > max_blocks:
        block_cl = "hidden"
    else:
        block_cl = ""

    if 'stat' in diff_data:
        max_change = 0
        for inse, dele in diff_data['stat'].values():
            tot = inse + dele
            if tot > max_change: max_change = tot

    for k in sorted(diff_data['blocks'].keys()):
        diff_data['blocks'][k] = diff_data['blocks'][k].replace(" @@ ", " @@\n ")
        if sec_pattern.match(k):
            cl = "highlight "
            if sysresponsible or sysrep_allow(nodenames, k):
                block = PRE(diff_data['blocks'][k], _class="diff "+block_cl)
            else:
                block = SPAN(T("You are not allowed to view this change"), _class=block_cl)
        else:
            cl = ""
            block = PRE(diff_data['blocks'][k], _class="diff "+block_cl)

        if 'stat' in diff_data and k in diff_data['stat']:
            inse = diff_data['stat'][k][0]
            dele = diff_data['stat'][k][1]
            tot = inse + dele
            quota = int(stat_width*tot/max_change)
            if quota == 0:
                quota = 1
            elif quota > tot:
                quota = tot
            _inse = int(inse*quota/tot)
            _dele = quota-_inse
            stat = PRE(tot, " ", "+"*_inse+"-"*_dele)
        else:
            stat = ""
        l.append(H2(beautify_fpath(k), stat, _class=cl, _onclick=js))
        l.append(block)
    return l

@auth.requires_login()
def ajax_sysreport_commit():
    cid = request.vars.cid
    path = request.vars.path
    begin = request.vars.begin
    end = request.vars.end
    nodename = request.vars.nodename
    return _sysreport_commit(nodename, cid, path=path, begin=begin, end=end)

def _sysreport_range_diff(nodenames, path=None, begin=None, end=None):
    d = []
    for nodename in nodenames:
        d += __sysreport_range_diff(nodename, path=path, begin=begin, end=end)
    return DIV(d)

def __sysreport_range_diff(nodename, path=None, begin=None, end=None):
    sysresponsible = is_sysresponsible(nodename)
    l = []

    # load secure patterns
    sec_pattern = get_pattern_secure()

    # diff data
    try:
        diff_data = sysreport.sysreport().show_data(None, nodename,
                                                path=encode_fpath(path),
                                                begin=begin,
                                                end=end
                                               )
    except Exception as e:
        return str(e)

    dd = show_diff_data([nodename], diff_data, sysresponsible, sec_pattern)
    if len(dd):
        l += dd
    else:
        l += SPAN(T("No changes"))

    return DIV(
      #SPAN(request.vars.nodename, _name="nodename", _class="hidden"),
      H2(T("Node %(nodename)s changes between %(begin)s and %(end)s", dict(nodename=nodename, begin=begin, end=end))),
      DIV(l, _name="diff"),
    )

def _sysreport_commit(nodename, cid, path=None, begin=None, end=None):
    sysresponsible = is_sysresponsible(nodename)
    l = []

    # load secure patterns
    sec_pattern = get_pattern_secure()

    # diff data
    diff_data = sysreport.sysreport().show_data(cid, nodename,
                                                path=encode_fpath(path),
                                                begin=begin,
                                                end=end
                                               )
    l += show_diff_data([nodename], diff_data, sysresponsible, sec_pattern)

    # file tree data
    tree_data = sysreport.sysreport().lstree_data(cid, nodename, path=encode_fpath(path))
    t = []
    for d in tree_data:
        if sec_pattern.match(d["fpath"]):
            cl = "highlight "
        else:
            cl = "clickable "
        if d["fpath"].startswith("cmd/"):
            cl += "action16"
        else:
            cl += "log16"
        attrs = {
          '_class': cl,
          '_nodename': nodename,
          '_oid': d["oid"],
          '_cid': d["cid"],
          '_ftype': d["type"],
          '_fpath': d["fpath"],
        }
        t.append(H2(beautify_fpath(d['fpath']), **attrs))

    return DIV(
      SPAN(request.vars.nodename, _name="nodename", _class="hidden"),
      SPAN(request.vars.cid, _name="cid", _class="hidden"),
      H1(T("Node %(nodename)s changes", dict(nodename=nodename))),
      H3(diff_data['date']),
      DIV(l, _name="diff"),
      H1(T("Files")),
      H3(diff_data['date']),
      DIV(t, _name="tree"),
    )

@auth.requires_login()
def ajax_sysreport_show_file():
    nodename = request.vars.nodename
    fpath = request.vars.fpath
    cid = request.vars.cid
    oid = request.vars.oid

    # load secure patterns
    sec_pattern = get_pattern_secure()
    sysresponsible = is_sysresponsible(nodename)

    data = sysreport.sysreport().show_file(fpath, cid, oid, nodename)

    if sec_pattern.match(data["fpath"]) and not (sysresponsible or \
       sysrep_allow([nodename], data["fpath"])):
        data['content'] = T("You are not allowed to view this file content")
    return data['content']


def sysrep():
    d = DIV(
      ajax_sysrep(),
      _style="padding:1em;text-align:left",
    )
    return dict(table=d)

@auth.requires_login()
def ajax_sysrep():
    nodes = request.vars.nodes.split(",")
    path = request.vars.path
    begin = request.vars.begin
    end = request.vars.end
    d = DIV(
      _sysreport(nodes, path=path, begin=begin, end=end),
      SCRIPT("""$(".diff").each(function(i, block){hljs.highlightBlock(block);})"""),
    )
    return d

@auth.requires_login()
def ajax_sysreport():
    nodes = request.args[0].split(",")
    path = request.vars.path
    begin = request.vars.begin
    end = request.vars.end
    return _sysreport(nodes, path=path, begin=begin, end=end)

def _sysreport(nodes, path=None, begin=None, end=None):
    if begin == "":
        begin = None
    if end == "":
        end = None
    import uuid
    tid = uuid.uuid1().hex
    data = sysreport.sysreport().timeline(nodes, path=encode_fpath(path))

    if begin or end:
        title = ""
    elif len(nodes) == 1:
        title = T("Node %(nodename)s changes timeline", dict(nodename=nodes[0]))
    else:
        title = T("Nodes %(nodename)s changes timeline", dict(nodename=', '.join(nodes)))

    # beautify fpaths
    max_fpath = 5
    for i, d in enumerate(data):
        buff = ""
        n = len(d['stat'])
        for j, fpath in enumerate(d['stat']):
            if j > max_fpath:
                buff += T("... %(n)s more", dict(n=n-max_fpath))
                break
            buff += beautify_fpath(fpath) + '\n'
        data[i]['stat'] = buff

    if begin or end:
        r_cl1 = ""
        r_cl2 = "hidden"
    else:
        r_cl1 = "hidden"
        r_cl2 = ""

    rangesel = DIV(
      DIV(
        INPUT(
          _value=end,
          _name="end",
          _class="date",
          _onkeyup="""
sysreport_onchangebeginenddate(event,"%(nodes)s")
""" % dict(nodes=','.join(nodes)),
),
        _class="end "+r_cl1,
        _style="float:right",
      ),
      DIV(
        INPUT(
          _value=begin,
          _name="begin",
          _class="date",
          _onkeyup="""
sysreport_onchangebeginenddate(event,"%(nodes)s")
""" % dict(nodes=','.join(nodes)),
),
        _class="begin "+r_cl1,
        _style="float:right",
      ),
      DIV(
        _class="time16 clickable " + r_cl2,
        _onclick="""
$(this).toggle()
$(this).siblings().toggle().children("input").focus()
$("input.date").datetimepicker({dateFormat:"yy-mm-dd"})
""",
),
      _style="float:right",
    )

    if path:
        _cl1 = ""
        _cl2 = "hidden"
    else:
        _cl1 = "hidden"
        _cl2 = ""

    filt = DIV(
      DIV(
        INPUT(
          _value=path,
          _name="filter",
          _onclick="""$(this).focus()""",
          _onkeyup="""
sysreport_onchangebeginenddate(event,"%(nodes)s")
""" % dict(nodes=','.join(nodes)),
),
          _class="filter " + _cl1,
      ),
      DIV(
        _class="filter16 clickable " + _cl2,
        _onclick="""$(this).toggle();$(this).siblings().toggle().children("input").focus()""",
      ),
      _style="float:right",
    )

    link = DIV(
      DIV(
        _class="hidden",
      ),
      _onclick="""
sysreport_createlink(this)
""",
      _style="float:right",
      _class="link16 clickable",
    )

    if "Manager" in user_groups():
        admin = DIV(
          _style="float:right",
          _class="lock clickable",
        )
    else:
        admin = ""

    if len(data) == 0:
        mesg = DIV(T("No sysreport available for this node"))
    else:
        mesg = ""

    if begin or end:
        show_data = _sysreport_range_diff(nodes, path=path, begin=begin, end=end)
        scr = ""
    elif request.vars.cid:
        show_data = _sysreport_commit(request.vars.nodename, request.vars.cid, path=path)
        scr = SCRIPT("""sysreport_timeline("%s", %s)"""% (tid, str(data))),
    else:
        show_data = ""
        scr = SCRIPT("""sysreport_timeline("%s", %s)"""% (tid, str(data))),

    return DIV(
      admin,
      link,
      filt,
      rangesel,
      DIV(_id=tid+"_admin", _class="hidden"),
      SPAN(','.join(nodes), _name="nodes", _class="hidden"),
      H1(title),
      DIV(
        _id=tid,
      ),
      mesg,
      DIV(
        show_data,
        _id=tid+"_show",
      ),
      SPAN(scr),
      _name="sysrep_top",
    )

@auth.requires_login()
def ajax_sysrepdiff():
    nodes = request.vars.nodes
    path = request.vars.path
    ignore_blanks = request.vars.ignore_blanks
    if ignore_blanks == "true":
        ignore_blanks = True
    else:
        ignore_blanks = False
    if nodes is None:
        return "No data"
    nodes = set(nodes.split(','))
    nodes -= set([""])
    nodes = sorted(list(nodes))

    l = []

    if path:
        l.append(H1(path))
        try:
            data = _sysrepdiff(nodes, path=path, ignore_blanks=ignore_blanks)
        except Exception as e:
            import traceback
            data = PRE(traceback.format_exc())
        l.append(data)
    else:
        for node in nodes[1:]:
            l.append(H1(' > '.join((nodes[0],node))))
            try:
                data = _sysrepdiff(nodes, path=path,
                                   ignore_blanks=ignore_blanks)
            except Exception as e:
                import traceback
                data = PRE(traceback.format_exc())
            l.append(data)

    if path:
        _cl1 = ""
        _cl2 = "hidden"
    else:
        _cl1 = "hidden"
        _cl2 = ""

    ignore_blanks_chk = DIV(
      INPUT(
        _checked="checked" if ignore_blanks else False,
        _type="checkbox",
        _name="ignore_blanks",
        _style="position:relative;top:0.3em",
        _onclick="""
sysreport_onsubmitsysrepdiff("%(nodes)s")
""" % dict(nodes=','.join(nodes)),
      ),
      DIV(
        T("Ignore blanks"),
      ),
      _style="float:right;display:flex",
    )

    filt = DIV(
      DIV(
        INPUT(
          _value=path,
          _name="filter",
          _onclick="""$(this).focus()""",
          _onkeyup="""
sysreport_onsubmitsysrepdiff("%(nodes)s")
""" % dict(nodes=','.join(nodes)),
        ),
        _class="filter " + _cl1,
      ),
      DIV(
        _class="filter16 clickable " + _cl2,
        _onclick="""$(this).toggle();$(this).siblings().toggle().children("input").focus()""",
      ),
      _style="float:right;margin-left:0.3em",
      _title="Paths to submit to the diff command. The paths begin with the nodename and the 'file' or 'cmd' directory. For example 'node1/file/dir1 node2/file/dir2'"
    )

    link = DIV(
      DIV(
        _class="hidden",
      ),
      _onclick="""
        url = $(location).attr("origin")
        url += "/init/ajax_sysreport/sysrepdiff?nodes="
        url += $(this).parent().parent().find("[name=nodes]").text()
        fval = $(this).parent().parent().find("input[name=filter]").val()
        if (fval!="") {
          url += "&path="+fval
        }
        fval = $(this).parent().parent().find("input[name=ignore_blanks]").is(":checked")
        if (fval) {
          url += "&ignore_blanks="+fval
        }
        $(this).children().html(url)
        $(this).children().show()
      """,
      _style="float:right;margin-left:0.3em",
      _class="link16 clickable",
    )

    return DIV(
      link,
      filt,
      ignore_blanks_chk,
      SPAN(','.join(nodes), _class='hidden', _name='nodes'),
      SPAN(l),
      _name="sysrepdiff_top"
    )

def _sysrepdiff(nodes, path=None, ignore_blanks=None):
    import os
    import subprocess

    here_d = os.path.dirname(__file__)
    sysrep_d = os.path.join(here_d, '..', 'uploads', 'sysreport')
    cwd = os.getcwd()
    try:
        os.chdir(sysrep_d)
    except:
        return "path %s does not exist on the collector" % sysrep_d
    if not os.path.exists(nodes[0]):
        os.chdir(cwd)
        return "node %s has no sysreport"%nodes[0]
    if not os.path.exists(nodes[1]):
        os.chdir(cwd)
        return "node %s has no sysreport"%nodes[1]

    cmd = ["diff", "-urN", "--exclude=.git"]
    if ignore_blanks:
        cmd += ["-Bb"]
    if path:
        cmd += path.split()
    else:
        cmd += [nodes[0], nodes[1]]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None)
    out, err = p.communicate()

    sysresponsible = is_sysresponsible(nodes[0]) & is_sysresponsible(nodes[1])

    # load secure patterns
    sec_pattern = get_pattern_secure()

    diff_data = sysreport.sysreport().parse_show(out)
    l = show_diff_data(nodes, diff_data, sysresponsible, sec_pattern)

    os.chdir(cwd)
    return DIV(l, name="diff")

def sysrepdiff():
    d = DIV(
      ajax_sysrepdiff(),
      _style="padding:1em;text-align:left",
    )
    return dict(table=d)

@auth.requires_login()
def ajax_sysreport_admin_del_secure():
    if "Manager" not in user_groups():
        raise HTTP(401) # Unauthorized exception
    q = db.sysrep_secure.id == request.vars.sec_id
    db(q).delete()

@auth.requires_login()
def ajax_sysreport_admin_add_secure():
    if "Manager" not in user_groups():
        raise HTTP(401) # Unauthorized exception
    pattern = request.vars.get("pattern")
    q = db.sysrep_secure.pattern == pattern
    if db(q).count() > 0:
        raise HTTP(400) # Bad Request
    db.sysrep_secure.insert(pattern=pattern)

@auth.requires_login()
def ajax_sysreport_admin():
    return DIV(
      H1(T("Sysreport administration")),
      ajax_sysreport_admin_secure(),
      ajax_sysreport_admin_allow(),
    )

@auth.requires_login()
def ajax_sysreport_admin_secure():
    tid = uuid.uuid1().hex
    secure = []

    def format_line(row):
        attrs = {
          "_sec_id": row.id,
          "_style": "display:table-row",
        }
        return DIV(
          DIV(
            _class="meta_del nologo16",
            _style="display:table-cell",
          ),
          DIV(
            row.pattern,
            _style="display:table-cell",
          ),
          **attrs
        )

    def add_line():
        d = DIV(
          DIV(
            T("Add secure pattern"),
            _class="add16 clickable",
            _onclick="$(this).next().toggle()",
          ),
          DIV(
            INPUT(),
            _class="hidden",
          ),
          _class="meta_add",
        )
        return d

    o = db.sysrep_secure.pattern
    q = db.sysrep_secure.id > 0
    rows = db(q).select()
    for row in rows:
        secure.append(format_line(row))
    secure.append(add_line())

    d = DIV(
      H2(T("Secure patterns")),
      DIV(
        secure,
      ),
      SCRIPT(
        """sysreport_admin_secure("%(tid)s")"""%dict(tid=tid),
      ),
      _id=tid,
    )
    return d

@auth.requires_login()
def ajax_sysreport_admin_del_allow():
    if "Manager" not in user_groups():
        raise HTTP(401) # Unauthorized Exception
    q = db.sysrep_allow.id == request.vars.allow_id
    db(q).delete()

@auth.requires_login()
def ajax_sysreport_admin_add_allow():
    if "Manager" not in user_groups():
        raise HTTP(401) # Unauthorized exception
    pattern = request.vars.get("pattern")
    role = request.vars.get("role")
    fset_name = request.vars.get("fset_name")

    q = db.auth_group.role == role
    try:
        group_id = db(q).select(db.auth_group.id).first().id
    except:
        raise HTTP(400) # Bad Request
    q = db.gen_filtersets.fset_name == fset_name
    try:
        fset_id = db(q).select(db.gen_filtersets.id).first().id
    except:
        raise HTTP(400) # Bad Request
    q = db.sysrep_allow.pattern == pattern
    q &= db.sysrep_allow.fset_id == fset_id
    q &= db.sysrep_allow.group_id == group_id
    if db(q).count() > 0:
        raise HTTP(400) # Bad Request
    db.sysrep_allow.insert(pattern=pattern, group_id=group_id, fset_id=fset_id)


@auth.requires_login()
def ajax_sysreport_admin_allow():
    tid = uuid.uuid1().hex
    allow = []

    def format_line(row):
        attrs = {
          "_allow_id": row.sysrep_allow.id,
          "_style": "display:table-row",
        }
        return DIV(
          DIV(
            _class="meta_del nologo16",
            _style="display:table-cell",
          ),
          DIV(
            T(
              "Group '%(g)s' can read secured files matching '%(p)s' from nodes matching the filterset '%(f)s'",
              dict(p=row.sysrep_allow.pattern, g=row.auth_group.role, f=row.gen_filtersets.fset_name),
            ),
            _style="display:table-cell",
          ),
          **attrs
        )

    def add_line():
        d = DIV(
          DIV(
            T("Add habilitation"),
            _class="add16 clickable",
            _onclick="$(this).next().toggle()",
          ),
          DIV(
            DIV(
              DIV(T("pattern"), _class="b", _style="display:table-cell"),
              DIV(T("group"), _class="b", _style="display:table-cell"),
              DIV(T("filterset"), _class="b", _style="display:table-cell"),
              _style="display:table-row",
            ),
            DIV(
              DIV(
                INPUT(_class="meta_pattern"),
                _style="display:table-cell",
              ),
              DIV(
                INPUT(_class="meta_role"),
                _style="display:table-cell",
              ),
              DIV(
                INPUT(_class="meta_fset_name"),
                _style="display:table-cell",
              ),
              _style="display:table-row",
            ),
            _class="hidden",
          ),
          _class="meta_add",
        )
        return d

    o = db.sysrep_allow.pattern|db.auth_group.role|db.gen_filtersets.fset_name
    q = db.sysrep_allow.id > 0
    q &= db.sysrep_allow.group_id == db.auth_group.id
    q &= db.sysrep_allow.fset_id == db.gen_filtersets.id
    rows = db(q).select(
      db.sysrep_allow.id,
      db.sysrep_allow.pattern,
      db.auth_group.role,
      db.gen_filtersets.fset_name,
    )
    for row in rows:
        allow.append(format_line(row))
    allow.append(add_line())

    d = DIV(
      H2(T("Habilitations")),
      DIV(
        allow,
      ),
      SCRIPT(
        """sysreport_admin_allow("%(tid)s")"""%dict(tid=tid),
      ),
      _id=tid,
    )
    return d
