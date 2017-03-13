import gluon.contrib.simplejson as sjson
from applications.init.modules import gittrack

def lib_provisioning_templates_add_to_git(tpl_id, tpl):
    o = gittrack.gittrack(otype='provisioning_templates')
    r = o.commit(tpl_id, tpl)

def lib_provisioning_templates_revisions(tpl_id):
    o = gittrack.gittrack(otype='provisioning_templates')
    r = o.timeline([tpl_id])
    return sjson.dumps(r)

def lib_provisioning_templates_diff(tpl_id, cid):
    o = gittrack.gittrack(otype='provisioning_templates')
    r = o.diff_cids(tpl_id, cid, 'HEAD', 'provisioning_templates')
    return sjson.dumps(r)

def lib_provisioning_templates_rollback(tpl_id, cid):
    o = gittrack.gittrack(otype='provisioning_templates')
    r = o.rollback(tpl_id, cid)
    row = db(db.prov_templates.id == tpl_id).select().first()
    here_d = os.path.dirname(__file__)
    collect_d = os.path.join(here_d, '..', 'private', 'provisioning_templates')
    with open (collect_d+"/"+tpl_id+"/provisioning_templates", "r") as myfile:
        data=myfile.readlines()
    row.update_record(tpl_definition=''.join(data))
