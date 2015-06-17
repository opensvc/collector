def call():
    session.forget()
    return service()

@request.restful()
@auth.requires_login()
def api():
    def GET(*args, **vars):
        # the default restful wrapper suppress the trailing .xxx
        # we need it for nodenames and svcname though.
        args = request.raw_args.split('/')

        try:
            n_args = len(args)
            if n_args == 1:
                if args[0] == "":
                    return doc()["doc"]
                if args[0] == "action_queue":
                    return get_action_queue(**vars)
                if args[0] == "alerts":
                    return get_alerts(**vars)
                if args[0] == "apps":
                    return get_apps(**vars)
                if args[0] == "arrays":
                    return get_arrays(**vars)
                if args[0] == "filtersets":
                    return get_filtersets(**vars)
                if args[0] == "forms":
                    return get_forms(**vars)
                if args[0] == "groups":
                    return get_groups(**vars)
                if args[0] == "ips":
                    return get_ips(**vars)
                if args[0] == "networks":
                    return get_networks(**vars)
                if args[0] == "nodes":
                    return get_nodes(**vars)
                if args[0] == "services":
                    return get_services(**vars)
                if args[0] == "tags":
                    return get_tags(**vars)
                if args[0] == "users":
                    return get_users(**vars)
            if n_args == 2:
                if args[0] == "action_queue" and args[1] == "stats":
                    return get_action_queue_stats()
                if args[0] == "action_queue":
                    return get_action_queue_one(args[1], **vars)
                if args[0] == "alerts":
                    return get_alert(args[1], **vars)
                if args[0] == "apps":
                    return get_app(args[1], **vars)
                if args[0] == "arrays":
                    return get_array(args[1], **vars)
                if args[0] == "forms":
                    return get_form(args[1], **vars)
                if args[0] == "groups":
                    return get_group(args[1], **vars)
                if args[0] == "ips":
                    return get_ip(args[1], **vars)
                if args[0] == "networks":
                    return get_network(args[1], **vars)
                if args[0] == "nodes":
                    return get_node(args[1], **vars)
                if args[0] == "scheduler" and args[1] == "tasks":
                    return get_scheduler_tasks(**vars)
                if args[0] == "scheduler" and args[1] == "runs":
                    return get_scheduler_runs(**vars)
                if args[0] == "scheduler" and args[1] == "workers":
                    return get_scheduler_workers(**vars)
                if args[0] == "services":
                    return get_service(args[1], **vars)
                if args[0] == "tags":
                    return get_tag(args[1], **vars)
                if args[0] == "users":
                    return get_user(args[1], **vars)
            if n_args == 3:
                if args[0] == "apps" and args[2] == "nodes":
                    return get_app_nodes(args[1], **vars)
                if args[0] == "apps" and args[2] == "quotas":
                    return get_app_quotas(args[1], **vars)
                if args[0] == "apps" and args[2] == "services":
                    return get_app_services(args[1], **vars)
                if args[0] == "arrays" and args[2] == "diskgroups":
                    return get_array_dgs(args[1], **vars)
                if args[0] == "arrays" and args[2] == "proxies":
                    return get_array_proxies(args[1], **vars)
                if args[0] == "arrays" and args[2] == "targets":
                    return get_array_targets(args[1], **vars)
                if args[0] == "groups" and args[2] == "apps":
                    return get_group_apps(args[1], **vars)
                if args[0] == "groups" and args[2] == "nodes":
                    return get_group_nodes(args[1], **vars)
                if args[0] == "groups" and args[2] == "services":
                    return get_group_services(args[1], **vars)
                if args[0] == "groups" and args[2] == "users":
                    return get_group_users(args[1], **vars)
                if args[0] == "networks" and args[2] == "nodes":
                    return get_network_nodes(args[1], **vars)
                if args[0] == "nodes" and args[2] == "alerts":
                    return get_node_alerts(args[1], **vars)
                if args[0] == "nodes" and args[2] == "checks":
                    return get_node_checks(args[1], **vars)
                if args[0] == "nodes" and args[2] == "disks":
                    return get_node_disks(args[1], **vars)
                if args[0] == "nodes" and args[2] == "hbas":
                    return get_node_hbas(args[1], **vars)
                if args[0] == "nodes" and args[2] == "ips":
                    return get_node_ips(args[1], **vars)
                if args[0] == "nodes" and args[2] == "services":
                    return get_node_services(args[1], **vars)
                if args[0] == "scheduler" and args[1] == "tasks":
                    return get_scheduler_task(args[2], **vars)
                if args[0] == "scheduler" and args[1] == "runs":
                    return get_scheduler_run(args[2], **vars)
                if args[0] == "scheduler" and args[1] == "workers":
                    return get_scheduler_worker(args[2], **vars)
                if args[0] == "services" and args[2] == "alerts":
                    return get_service_alerts(args[1], **vars)
                if args[0] == "services" and args[2] == "checks":
                    return get_service_checks(args[1], **vars)
                if args[0] == "services" and args[2] == "disks":
                    return get_service_disks(args[1], **vars)
                if args[0] == "services" and args[2] == "nodes":
                    return get_service_nodes(args[1], **vars)
                if args[0] == "tags" and args[2] == "nodes":
                    return get_tag_nodes(args[1], **vars)
                if args[0] == "tags" and args[2] == "services":
                    return get_tag_services(args[1], **vars)
                if args[0] == "users" and args[2] == "apps":
                    return get_user_apps(args[1], **vars)
                if args[0] == "users" and args[2] == "groups":
                    return get_user_groups(args[1], **vars)
                if args[0] == "users" and args[2] == "nodes":
                    return get_user_nodes(args[1], **vars)
                if args[0] == "users" and args[2] == "services":
                    return get_user_services(args[1], **vars)
            if n_args == 4:
                if args[0] == "services" and args[2] == "nodes":
                    return get_service_node(args[1], args[3], **vars)
                if args[0] == "nodes" and args[2] == "services":
                    return get_node_service(args[1], args[3], **vars)
        except Exception as e:
            return dict(error=str(e))
        return dict(error="Unsupported api url")
    def POST(*args, **vars):
        args = request.raw_args.split('/')
        try:
            n_args = len(args)
            if n_args == 1:
                if args[0] == "action_queue":
                    return post_action_queue(**vars)
                if args[0] == "networks":
                    return create_network(**vars)
                if args[0] == "nodes":
                    return create_node(**vars)
                if args[0] == "tags":
                    return add_tag(**vars)
            if n_args == 2:
                if args[0] == "action_queue":
                    return set_action_queue_one(args[1], **vars)
                if args[0] == "networks":
                    return set_network(args[1], **vars)
                if args[0] == "nodes":
                    return set_node(args[1], **vars)
            if n_args == 3:
                if args[0] == "scheduler" and args[1] == "tasks":
                    return set_scheduler_task(args[2], **vars)
                if args[0] == "scheduler" and args[1] == "runs":
                    return set_scheduler_run(args[2], **vars)
            if n_args == 4:
                if args[0] == "tags" and args[2] == "nodes":
                    return tag_node_attach(args[1], args[3], **vars)
                if args[0] == "tags" and args[2] == "services":
                    return tag_service_attach(args[1], args[3], **vars)
        except Exception as e:
            return dict(error=str(e))
        return dict()
    def PUT(*args, **vars):
        args = request.raw_args.split('/')
        try:
            n_args = len(args)
            if n_args == 2:
                if args[0] == "forms":
                    return put_form(args[1], **vars)
        except Exception as e:
            return dict(error=str(e))
        return dict()
    def DELETE(*args, **vars):
        args = request.raw_args.split('/')
        try:
            n_args = len(args)
            if n_args == 2:
                if args[0] == "action_queue":
                    return delete_action_queue_one(args[1], **vars)
                if args[0] == "networks":
                    return delete_network(args[1], **vars)
                if args[0] == "nodes":
                    return delete_node(args[1], **vars)
                if args[0] == "tags":
                    return del_tag(args[1], **vars)
            if n_args == 3:
                if args[0] == "scheduler" and args[1] == "tasks":
                    return delete_scheduler_task(args[2], **vars)
                if args[0] == "scheduler" and args[1] == "runs":
                    return delete_scheduler_run(args[2], **vars)
            if n_args == 4:
                if args[0] == "tags" and args[2] == "nodes":
                    return tag_node_detach(args[1], args[3], **vars)
                if args[0] == "tags" and args[2] == "services":
                    return tag_service_detach(args[1], args[3], **vars)
        except Exception as e:
            return dict(error=str(e))
        return dict()
    return locals()

def doc():
    all_docs = {}
    all_docs.update(api_action_queue_doc)
    all_docs.update(api_alerts_doc)
    all_docs.update(api_apps_doc)
    all_docs.update(api_arrays_doc)
    all_docs.update(api_filtersets_doc)
    all_docs.update(api_groups_doc)
    all_docs.update(api_ips_doc)
    all_docs.update(api_networks_doc)
    all_docs.update(api_nodes_doc)
    all_docs.update(api_services_doc)
    all_docs.update(api_scheduler_doc)
    all_docs.update(api_tags_doc)
    all_docs.update(api_users_doc)

    s = """
# RESTful API documentation

"""
    actions = [
      "GET",
      "DELETE",
      "POST",
      "PUT",
    ]
    urls = sorted(all_docs.keys())
    s += "-----\n"
    for url in urls:
        l = []
        d = all_docs[url]
        l.append(url)
        for a in actions:
            if a in d:
                l.append("[[``%(a)s``:red #%(anchor)s]]" % dict(a=a, anchor=url+":"+a))
            else:
                l.append("``%(a)s``:grey" % dict(a=a))
        s += " | ".join(l)
        s += "\n"
    s += "-----\n"

    s += """
# Smart queries

Most API urls returning lists accept the ''query'' parameter, which value is a
web2py smart query.

A smart query is a filtering string like:

''os_name=linux and os_release contains 6.1''

Supported operators are:
- =, >, >=, <, <=
- equals, greater than, lesser than
- in aaa,bbb
- not


# Using the API with python

``
#!/usr/bin/python

import requests, json

requests.packages.urllib3.disable_warnings()

host = 'https://%(collector)s'
url = host + '/init/rest/api'

user = "%(email)s"
password = "mypass"
auth = (user, password)
verify=False

print "* post node"
data = {"nodename": "testnode", "model": "x1234", "team_responsible": "myteam"}
r = requests.post(url+"/nodes", data, auth=auth, verify=verify)
print r.content

print "* get node"
r = requests.get(url+"/nodes/testnode?props=nodename,os_name,model,updated",
auth=auth, verify=verify)
print r.content

print "* delete node"
r = requests.delete(url+"/nodes/testnode", auth=auth, verify=verify)
print r.content
``

# API reference

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )
    for url in urls:
        d = all_docs[url]
        s += """
[[%(url)s]]
## ``%(url)s``:black

""" % dict(url=url)
        for a in actions:
            if a not in d:
                continue
            s += """
[[%(url)s:%(a)s]]
## ``%(url)s :: %(a)s``:red

""" % dict(url=url, a=a)
            s += d[a]

    return dict(doc=DIV(MARKMIN(s), _style="padding:1em;text-align:left"))



