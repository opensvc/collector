from applications.init.modules import gittrack
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

def is_sysresponsible(node_ids):
    # managers are allowed
    ug = set(user_groups())
    if "Manager" in ug:
        return True

    # compute user and nodes groups intersection
    if type(node_ids) not in  (list, set):
        node_ids = [node_ids]
    q = db.nodes.node_id.belongs(node_ids)
    g = set([r.team_responsible for r in db(q).select(db.nodes.team_responsible)])
    if g < ug:
        return True

    return False

@auth.requires_login()
def sysrep_allow(node_ids, fpath):
    q = db.sysrep_allow.group_id.belongs(user_group_ids())
    rows = db(q).select(db.sysrep_allow.fset_id, db.sysrep_allow.pattern)
    for row in rows:
        if not row.fset_id:
            continue
        pattern = re.compile(row.pattern)
        if not pattern.match(fpath):
            continue
        _node_ids, _svc_ids = filterset_encap_query_id(row.fset_id)
        if len(set(node_ids) & _node_ids) != len(node_ids):
            continue
        return True
    return False

def lib_get_sysreport(node_ids, path=None, begin=None, end=None):
    data = gittrack.gittrack().timeline(node_ids, path=encode_fpath(path), begin=begin, end=end)
    for i, d in enumerate(data):
        for j, fpath in enumerate(d["stat"]):
            data[i]["stat"][j] = beautify_fpath(fpath)
    return data

def lib_get_sysreport_timediff(node_id, path=None, begin=None, end=None):
    sysresponsible = is_sysresponsible(node_id)
    data = gittrack.gittrack().show_data(None,
                                           node_id,
                                           path=encode_fpath(path),
                                           begin=begin,
                                           end=end
                                          )
    for k, d in data['stat'].items():
        del(data['stat'][k])
        data['stat'][beautify_fpath(k)] = d
    sec_pattern = get_pattern_secure()
    for k in data['blocks'].keys():
        diff = data['blocks'][k]
        if k.startswith("cmd/"):
            content_type = "command"
        else:
            content_type = "file"
        if sec_pattern.match(k):
            secure = True
            if not sysresponsible and not sysrep_allow([node_id], k):
                diff = T("You are not allowed to view this change")
        else:
            secure = False
        del(data['blocks'][k])
        data['blocks'][beautify_fpath(k)] = {
          "secure": secure,
          "content_type": content_type,
          "diff": diff,
        }

    return data

def lib_get_sysreport_commit(node_id, cid, path=None):
    sysresponsible = is_sysresponsible(node_id)
    data = gittrack.gittrack().show_data(cid, node_id, path=encode_fpath(path),
                                          )
    for k, d in data['stat'].items():
        del(data['stat'][k])
        data['stat'][beautify_fpath(k)] = d
    sec_pattern = get_pattern_secure()
    for k in data['blocks'].keys():
        diff = data['blocks'][k]
        if k.startswith("cmd/"):
            content_type = "command"
        else:
            content_type = "file"
        if sec_pattern.match(k):
            secure = True
            if not sysresponsible and not sysrep_allow([node_id], k):
                diff = T("You are not allowed to view this change")
        else:
            secure = False
        del(data['blocks'][k])
        data['blocks'][beautify_fpath(k)] = {
          "secure": secure,
          "content_type": content_type,
          "diff": diff,
        }

    return data

def lib_get_sysreport_commit_tree(node_id, cid, path=None):
    sysresponsible = is_sysresponsible(node_id)
    data = gittrack.gittrack().lstree_data(cid, node_id, path=encode_fpath(path))
    sec_pattern = get_pattern_secure()
    for i, d in enumerate(data):
        if d["fpath"].startswith("cmd/"):
            data[i]["content_type"] = "command"
        else:
            data[i]["content_type"] = "file"
        if sec_pattern.match(d["fpath"]):
            data[i]["secure"] = True
        else:
            data[i]["secure"] = False
        data[i]["fpath"] = beautify_fpath(d["fpath"])
    return data

def lib_get_sysreport_commit_tree_file(node_id, cid, oid):
    sysresponsible = is_sysresponsible(node_id)
    data = gittrack.gittrack().lstree_data(cid, node_id)
    sec_pattern = get_pattern_secure()
    for d in data:
        if d["oid"] != oid:
            continue
        if not sec_pattern.match(d["fpath"]):
            break
        if not sysresponsible and not sysrep_allow([node_id], k):
            return {
              "oid": oid,
              "content": T("You are not allowed to view this file content"),
            }
    data = gittrack.gittrack().show_file_unvalidated(cid, oid, node_id)
    return data

def lib_get_sysreport_nodediff(node_ids, path=None, ignore_blanks=False):
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
    if not os.path.exists(node_ids[0]):
        os.chdir(cwd)
        raise Exception("node %s has no sysreport"%node_ids[0])
    if not os.path.exists(node_ids[1]):
        os.chdir(cwd)
        return Exception("node %s has no sysreport"%node_ids[1])

    cmd = ["diff", "-urN", "--exclude=.git"]
    if ignore_blanks:
        cmd += ["-Bb"]
    cmd += [node_ids[0], node_ids[1]]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None)
    out, err = p.communicate()

    sysresponsible = is_sysresponsible(node_ids[0]) & is_sysresponsible(node_ids[1])

    # load secure patterns
    sec_pattern = get_pattern_secure()

    diff_data = gittrack.gittrack().parse_show(out)
    os.chdir(cwd)

    data = []
    for key in sorted(diff_data["blocks"].keys()):
        if "\t" in key:
            fpath = key.split("\t")[0]
        else:
            fpath = key
        fpath = beautify_fpath(fpath)
        if path is not None and not fnmatch.fnmatch(fpath, path):
            continue
        if fpath.startswith("cmd/"):
            content_type = "command"
        else:
            content_type = "file"
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
          "content_type": content_type,
          "diff": diff,
        }
        data.append(d)
    return data

