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

def beautify_fpath(fpath, nodename=None):
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
    if nodename is not None:
        fpath = fpath.replace(nodename+"/file", "")
        fpath = fpath.replace(nodename+"/cmd/", "")
    if fpath.startswith("b//"):
        fpath = fpath[2:]
    return fpath

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

@auth.requires_login()
def ajax_sysreport_commit():
    cid = request.vars.id
    nodename = request.vars.nodename
    sysresponsible = is_sysresponsible(nodename)

    # load secure patterns
    sec_pattern = get_pattern_secure()

    # diff data
    diff_data = sysreport.sysreport().show_data(cid)
    l = []
    for k in sorted(diff_data['blocks'].keys()):
        diff_data['blocks'][k] = diff_data['blocks'][k].replace(" @@ ", " @@\n ")
        if sec_pattern.match(k):
            cl = "highlight "
            if sysresponsible:
                block = PRE(CODE(diff_data['blocks'][k]))
            else:
                block = T("You are not allowed to view this change")
        else:
            cl = ""
            block = PRE(CODE(diff_data['blocks'][k]))

        l.append(H2(beautify_fpath(k, nodename), _class=cl))
        l.append(block)

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
        t.append(H2(beautify_fpath(d['fpath'], nodename), **attrs))

    return DIV(
      H1(T("Differences")),
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

@auth.requires_login()
def ajax_sysreport():
    nodename = request.args[0]
    tid = 'sysreport_'+nodename.replace('.','_')
    data = sysreport.sysreport().timeline(nodename)
    if len(data) == 0:
        return DIV(T("No sysreport available for this node"))

    # beautify fpaths
    for i, d in enumerate(data):
        buff = ""
        for fpath in d['stat']:
            buff += beautify_fpath(fpath, nodename) + '\n'
        data[i]['stat'] = buff

    return DIV(
      H1(T("Changes")),
      DIV(
        _id=tid,
      ),
      DIV(
        _id=tid+"_show",
      ),
      SCRIPT(_src=URL(c="static", f="sysreport.js")),
      SCRIPT("""sysreport_timeline("%s", "%s", %s)"""% (tid, nodename, str(data))),
    )

