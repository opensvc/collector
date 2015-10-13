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

def encode_fpath(fpath):
    if fpath is None or fpath == "":
        return
    if "/bin/" in fpath:
        fpath = fpath.replace(' ', '(space)')
        fpath = fpath.replace('|', '(pipe)')
        fpath = fpath.replace('&', '(amp)')
        fpath = fpath.replace('$', '(dollar)')
        fpath = fpath.replace('^', '(caret)')
        fpath = fpath.replace('/', '(slash)')
        fpath = fpath.replace(':', '(colon)')
        fpath = fpath.replace(';', '(semicolon)')
        fpath = fpath.replace('<', '(lt)')
        fpath = fpath.replace('>', '(gt)')
        fpath = fpath.replace('=', '(eq)')
        fpath = fpath.replace('?', '(question)')
        fpath = fpath.replace('@', '(at)')
        fpath = fpath.replace('!', '(excl)')
        fpath = fpath.replace('#', '(num)')
        fpath = fpath.replace('%', '(pct)')
        fpath = fpath.replace('"', '(dquote)')
        fpath = fpath.replace("'", '(squote)')
    fpath = "*/" + fpath
    return fpath

def beautify_fpath(fpath):
    if fpath.startswith("cmd/"):
        fpath = fpath[3:]
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
    elif fpath.startswith("file/"):
        fpath = fpath[4:]

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

@auth.requires_login()
def sysrep_allow(nodenames, fpath):
    q = db.sysrep_allow.group_id.belongs(user_group_ids())
    rows = db(q).select(db.sysrep_allow.fset_id, db.sysrep_allow.pattern)
    for row in rows:
        if not row.fset_id:
            continue
        pattern = re.compile(row.pattern)
        if not pattern.match(fpath):
            continue
        _nodenames, _svcnames = filterset_encap_query(row.fset_id)
        if len(set(nodenames) & _nodenames) != len(nodenames):
            continue
        return True
    return False

def lib_get_sysreport(nodename, path=None, begin=None, end=None):
    data = sysreport.sysreport().timeline([nodename], path=encode_fpath(path))
    for i, d in enumerate(data):
        for j, fpath in enumerate(d["stat"]):
            data[i]["stat"][j] = beautify_fpath(fpath)
    return data

def lib_get_sysreport_timediff(nodename, path=None, begin=None, end=None):
    sysresponsible = is_sysresponsible(nodename)
    data = sysreport.sysreport().show_data(None,
                                           nodename,
                                           path=encode_fpath(path),
                                           begin=begin,
                                           end=end
                                          )
    sec_pattern = get_pattern_secure()
    for k in data['blocks'].keys():
        diff = data['blocks'][k]
        if sec_pattern.match(k):
            secure = True
            if not sysresponsible and not sysrep_allow([nodename], k):
                diff = T("You are not allowed to view this change")
        else:
            secure = False
        data['blocks'][k] = {
          "secure": secure,
          "diff": diff,
        }

    return data

def lib_get_sysreport_commit(nodename, cid, path=None):
    sysresponsible = is_sysresponsible(nodename)
    data = sysreport.sysreport().show_data(cid, nodename, path=encode_fpath(path),
                                          )
    sec_pattern = get_pattern_secure()
    for k in data['blocks'].keys():
        diff = data['blocks'][k]
        if sec_pattern.match(k):
            secure = True
            if not sysresponsible and not sysrep_allow([nodename], k):
                diff = T("You are not allowed to view this change")
        else:
            secure = False
        data['blocks'][k] = {
          "secure": secure,
          "diff": diff,
        }

    return data

def lib_get_sysreport_commit_tree(nodename, cid, path=None):
    sysresponsible = is_sysresponsible(nodename)
    data = sysreport.sysreport().lstree_data(cid, nodename, path=encode_fpath(path))
    sec_pattern = get_pattern_secure()
    for i, d in enumerate(data):
        if sec_pattern.match(d["fpath"]):
            data[i]["secure"] = True
        else:
            data[i]["secure"] = False
    return data

def lib_get_sysreport_commit_tree_file(nodename, cid, oid):
    sysresponsible = is_sysresponsible(nodename)
    data = sysreport.sysreport().lstree_data(cid, nodename)
    sec_pattern = get_pattern_secure()
    for d in data:
        if d["oid"] != oid:
            continue
        if not sec_pattern.match(d["fpath"]):
            break
        if not sysresponsible and not sysrep_allow([nodename], k):
            return {
              "oid": oid,
              "content": T("You are not allowed to view this file content"),
            }
    data = sysreport.sysreport().show_file_unvalidated(cid, oid, nodename)
    return data

def lib_get_sysreport_nodediff(nodes, path=None, ignore_blanks=False):
    import os
    import subprocess
    import fnmatch

    here_d = os.path.dirname(__file__)
    sysrep_d = os.path.join(here_d, '..', 'uploads', 'sysreport')
    cwd = os.getcwd()
    try:
        os.chdir(sysrep_d)
    except:
        raise Exception("path %s does not exist on the collector" % sysrep_d)
    if not os.path.exists(nodes[0]):
        os.chdir(cwd)
        raise Exception("node %s has no sysreport"%nodes[0])
    if not os.path.exists(nodes[1]):
        os.chdir(cwd)
        return Exception("node %s has no sysreport"%nodes[1])

    cmd = ["diff", "-urN", "--exclude=.git"]
    if ignore_blanks:
        cmd += ["-Bb"]
    cmd += [nodes[0], nodes[1]]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None)
    out, err = p.communicate()

    sysresponsible = is_sysresponsible(nodes[0]) & is_sysresponsible(nodes[1])

    # load secure patterns
    sec_pattern = get_pattern_secure()

    diff_data = sysreport.sysreport().parse_show(out)
    os.chdir(cwd)

    data = []
    for key in sorted(diff_data["blocks"].keys()):
        if "\t" in key:
            fpath = key.split("\t")[0]
        else:
            fpath = key
        fpath = beautify_fpath(fpath)
        if not fnmatch.fnmatch(fpath, path):
            continue
        if sec_pattern.match(fpath):
            secure = True
            if sysresponsible:
                diff = diff_data["blocks"][key]
            else:
                diff = T("You are not allowed to view this change")
        else:
            diff = diff_data["blocks"][key]
            secure = False
        d = {
          "path": fpath,
          "secure": secure,
          "diff": diff,
        }
        data.append(d)
    return data

