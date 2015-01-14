from applications.init.modules import sysreport
import re

def get_pattern_secure():
    q = db.sysrep_secure.id > 0
    sec_patterns = [r.pattern for r in db(q).select(db.sysrep_secure.pattern)]
    if len(sec_patterns) == 0:
        # protect all files if secure table is not populated
        sec_pattern = re.compile(".*")
    else:
        try:
            sec_pattern = re.compile('|'.join(sec_patterns))
        except:
            # protect all files if a corrupt regex is defined
            sec_pattern = re.compile(".*")
    return sec_pattern

def beautify_fpath(fpath):
    if "/cmd/" in fpath:
        fpath = fpath.replace('(space)', ' ')
        fpath = fpath.replace('(pipe)', '|')
        fpath = fpath.replace('(amp)', '&')
        fpath = fpath.replace('(dollar)', '$')
        fpath = fpath.replace('(caret)', '^')
        fpath = fpath.replace('(slash)', '/')
        fpath = fpath.replace('(colon)', ':')
        fpath = fpath.replace('(semicolon)', ';')
        fpath = fpath.replace('(lt)', '<')
        fpath = fpath.replace('(gt)', '>')
        fpath = fpath.replace('(eq)', '=')
        fpath = fpath.replace('(question)', '?')
        fpath = fpath.replace('(at)', '@')
        fpath = fpath.replace('(excl)', '!')
        fpath = fpath.replace('(num)', '#')
        fpath = fpath.replace('(pct)', '%')
        fpath = fpath.replace('(dquote)', '"')
        fpath = fpath.replace('(squote)', "'")

    l = fpath.split('/')
    if len(l) > 2:
        del(l[1])
    fpath = '/'.join(['']+l[1:])

    if '\t' in fpath:
        l = fpath.split('\t')
        fpath = '\t'.join(l[:-1])

    if fpath.startswith("b//"):
        fpath = fpath[2:]

    return fpath.replace('//', '/')

def is_sysresponsible(nodenames):
    # managers are allowed
    ug = set(user_groups())
    if "Manager" in ug:
        return True

    # compute user and nodes groups intersection
    if type(nodenames) in (str, unicode):
        nodenames = [nodenames]
    q = db.nodes.nodename.belongs(nodenames)
    g = set([r.team_responsible for r in db(q).select(db.nodes.team_responsible)])
    if g < ug:
        return True

    return False

def show_diff_data(diff_data, sysresponsible, sec_pattern):
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
            if sysresponsible:
                block = PRE(CODE(diff_data['blocks'][k]), _class=block_cl)
            else:
                block = SPAN(T("You are not allowed to view this change"), _class=block_cl)
        else:
            cl = ""
            block = PRE(CODE(diff_data['blocks'][k]), _class=block_cl)

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
    nodename = request.vars.nodename
    sysresponsible = is_sysresponsible(nodename)
    l = []

    # load secure patterns
    sec_pattern = get_pattern_secure()

    # diff data
    diff_data = sysreport.sysreport().show_data(cid, nodename)
    l += show_diff_data(diff_data, sysresponsible, sec_pattern)

    # file tree data
    tree_data = sysreport.sysreport().lstree_data(cid, nodename)
    t = []
    for d in tree_data:
        if sec_pattern.match(d["fpath"]):
            cl = "highlight "
        else:
            cl = "clickable "
        if "/cmd/" in d["fpath"]:
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

    data = sysreport.sysreport().show_file(fpath, cid, oid)

    if sec_pattern.match(data["fpath"]) and not sysresponsible:
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
    return _sysreport(nodes)

@auth.requires_login()
def ajax_sysreport():
    nodes = request.args[0].split(",")
    return _sysreport(nodes)

def _sysreport(nodes):
    import uuid
    tid = uuid.uuid1().hex
    data = sysreport.sysreport().timeline(nodes)
    if len(data) == 0:
        return DIV(T("No sysreport available for this node"))

    if len(data) == 1:
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

    link = DIV(
      DIV(
        _class="hidden",
      ),
      _onclick="""
        url = $(location).attr("origin")
        url += "/init/ajax_sysreport/sysrep?nodes="
        url += $(this).parent().parent().find("[name=nodes]").text()

        cid = $(this).parent().parent().find("[name=cid]").text()
        nodename = $(this).parent().parent().find("[name=nodename]").text()
        if (cid != "") {
          url += "&cid="+cid
          url += "&nodename="+nodename
        }

        $(this).children().html(url)
        $(this).children().show()
      """,
      _style="float:right",
      _class="link16 clickable",
    )

    if request.vars.cid is not None:
        show_data = ajax_sysreport_commit()
    else:
        show_data = ""

    return DIV(
      link,
      SPAN(','.join(nodes), _name="nodes", _class="hidden"),
      H1(title),
      DIV(
        _id=tid,
      ),
      DIV(
        show_data,
        _id=tid+"_show",
      ),
      SCRIPT(_src=URL(c="static", f="sysreport.js")),
      SCRIPT("""sysreport_timeline("%s", %s)"""% (tid, str(data))),
    )

@auth.requires_login()
def ajax_sysrepdiff():
    nodes = request.vars.nodes
    if nodes is None:
        return "No data"
    nodes = set(nodes.split(','))
    nodes -= set([""])
    nodes = sorted(list(nodes))

    l = []

    for node in nodes[1:]:
        l.append(H1(' > '.join((nodes[0],node))))
        try:
            data = _sysrepdiff(nodes)
        except Exception as e:
            import traceback
            data = PRE(traceback.format_exc())
        l.append(data)

    link = DIV(
      DIV(
        _class="hidden",
      ),
      _onclick="""
        url = $(location).attr("origin")
        url += "/init/ajax_sysreport/sysrepdiff?nodes="
        url += $(this).parent().parent().find("[name=nodes]").text()
        $(this).children().html(url)
        $(this).children().show()
      """,
      _style="float:right",
      _class="link16 clickable",
    )

    return DIV(
      link,
      SPAN(','.join(nodes), _class='hidden', _name='nodes'),
      SPAN(l),
    )

def _sysrepdiff(nodes):
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

    cmd = ["diff", "-urN", nodes[0], nodes[1]]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None)
    out, err = p.communicate()

    sysresponsible = is_sysresponsible(nodes[0]) & is_sysresponsible(nodes[1])

    # load secure patterns
    sec_pattern = get_pattern_secure()

    diff_data = sysreport.sysreport().parse_show(out)
    l = show_diff_data(diff_data, sysresponsible, sec_pattern)

    os.chdir(cwd)
    return SPAN(l)

def sysrepdiff():
    d = DIV(
      ajax_sysrepdiff(),
      _style="padding:1em;text-align:left",
    )
    return dict(table=d)
