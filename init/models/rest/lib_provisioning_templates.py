import gluon.contrib.simplejson as sjson
from applications.init.modules import gittrack

def lib_provisioning_templates_add_to_git(tpl_id, tpl):
    o = gittrack.gittrack(otype='provisioning_templates')
    r = o.commit(tpl_id, tpl, author=user_name(email=True))

def lib_provisioning_templates_revision(tpl_id, cid):
    o = gittrack.gittrack(otype='provisioning_templates')
    data = o.lstree_data(cid, tpl_id)
    oid = data[0]["oid"]
    return {"data": o.show_file_unvalidated(cid, oid, tpl_id)}

def lib_provisioning_templates_revisions(tpl_id):
    o = gittrack.gittrack(otype='provisioning_templates')
    r = o.timeline([tpl_id])
    return {"data": r}

def lib_provisioning_templates_diff(tpl_id, cid, other=None):
    o = gittrack.gittrack(otype='provisioning_templates')
    if other:
        r = o.diff_cids(tpl_id, cid, other, filename="provisioning_templates")
    else:
        r = o.show(cid, tpl_id, numstat=True)
    return {"data": r}

def lib_provisioning_templates_rollback(tpl_id, cid):
    o = gittrack.gittrack(otype='provisioning_templates')
    r = o.rollback(tpl_id, cid, author=user_name(email=True))
    row = db(db.prov_templates.id == tpl_id).select().first()
    here_d = os.path.dirname(__file__)
    collect_d = os.path.join(here_d, '..', 'private', 'provisioning_templates')
    with open (collect_d+"/"+tpl_id+"/provisioning_templates", "r") as myfile:
        data=myfile.readlines()
    row.update_record(tpl_definition=''.join(data))
