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

def sysrep():
    d = DIV(
      _sysrep(),
      _style="padding:1em;text-align:left",
    )
    return dict(table=d)

@auth.requires_login()
def _sysrep():
    nodes = request.vars.nodes
    path = request.vars.path if request.vars.path else ""
    begin = request.vars.begin if request.vars.begin else ""
    end = request.vars.end if request.vars.end else ""
    cid = request.vars.cid if request.vars.cid else ""
    d = DIV(
      SCRIPT("""sysrep("sysreport_simple", "%(nodes)s", "%(path)s", "%(begin)s", "%(end)s", "%(cid)s") """ %
                dict(nodes=nodes, path=path, begin=begin, end=end, cid=cid)),
      _id="sysreport_simple",
    )
    return d

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
