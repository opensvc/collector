from applications.init.modules import sysreport

@auth.requires_login()
def ajax_sysreport_commit():
    cid = request.vars.id
    nodename = request.vars.nodename

    # diff data
    diff_data = sysreport.sysreport().show_data(cid)
    l = []
    for k in sorted(diff_data['blocks'].keys()):
        l.append(H2(k))
        l.append(PRE(CODE(diff_data['blocks'][k])))

    # file tree data
    tree_data = sysreport.sysreport().lstree_data(cid, nodename)
    t = []
    for d in tree_data:
        if "/cmd/" in d["fpath"]:
            cl = "action16"
        else:
            cl = "log16"
        attrs = {
          '_class': "clickable "+cl,
          '_uuid': d["uuid"],
          '_ftype': d["type"],
        }
        t.append(H2(d['fpath'], **attrs))

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
    uuid = request.vars.id
    data = sysreport.sysreport().show_file(uuid)
    return data

@auth.requires_login()
def ajax_sysreport():
    nodename = request.args[0]
    tid = 'sysreport_'+nodename.replace('.','_')
    data = sysreport.sysreport().timeline(nodename)
    if len(data) == 0:
        return DIV(T("No sysreport available for this node"))
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

