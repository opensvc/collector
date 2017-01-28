import gluon.contrib.simplejson as sjson

def form_log(results, ret, action, fmt, d):
    if ret == 0:
        level = "info"
    else:
        level = "error"
    results["log"].append([ret, action, fmt, d])
    _log(action, fmt, d, level=level)
    return results


def ordered_outputs(form_definition):
    l = []
    h = {}

    dest_order = [
     'db',
     'script',
     'rest',
     'workflow',
     'mail',
    ]

    for output in form_definition.get('Outputs', []):
        dest = output.get('Dest')
        if dest not in h:
            h[dest] = [output]
        else:
            h[dest].append(output)

    unclassified = set(h.keys()) - set(dest_order)

    for dest in dest_order + list(unclassified):
        if dest in h:
            l += h[dest]

    return l

def get_form_formatted_data_o(output, form_definition, _d=None):
    if _d is not None:
        return _d
    raise Exception("get_form_formatted_data_o: no form data")

def check_output_condition(output, form, form_definition, _d=None):
    cond = output.get('Condition', 'none')
    if cond == 'none':
        return True
    if cond is None:
        raise Exception("malformed output condition: %s"%cond)
    if output.get('Format') != "dict":
        raise Exception("Output condition can only be set on dict-format output")

    def get_var_val(op):
        l = cond.split(op)
        if len(l) != 2:
            raise Exception("malformed output condition: %s"%cond)
        var = l[0].strip()
        val = l[1].strip()
        if not var.startswith("#") or len(var) < 2:
            raise Exception("malformed output condition: %s"%cond)
        var = var[1:]
        if var not in o:
            if op == "==" and val == "empty":
                pass
            else:
                raise Exception("input id %s is not present in submitted data : %s"%(var, str(o)))
        return var, val

    o = get_form_formatted_data_o(output, form_definition, _d)

    if "==" in cond:
        var, val = get_var_val("==")
        if val == "empty":
            if var not in o or o[val] in (None, "undefined", ""):
                return True
            return False
        if var not in o:
            return False
        if o[var] == val:
            return True
        else:
            return False
    elif "!=" in cond:
        var, val = get_var_val("!=")
        if val == "empty":
            if var in o and o[val] not in (None, "undefined", ""):
                return True
            return False
        if var not in o:
            return True
        if o[var] != val:
            return True
        else:
            return False

    raise Exception("operator is not supported in output condition %s"%cond)

def get_form_formatted_data(output, form_definition, _d=None):
    output_value = get_form_formatted_data_o(output, form_definition, _d)

    if output.get('Type') == "json":
        output_value = sjson.dumps(output_value, default=datetime.datetime.isoformat)

    return output_value

def insert_form_md5(form):
    o = md5()
    o.update(form.form_yaml)
    form_md5 = str(o.hexdigest())

    q = db.forms_revisions.form_md5 == form_md5
    if db(q).select(cacheable=True).first() is not None:
        return form_md5

    db.forms_revisions.insert(
      form_id=form.id,
      form_yaml=form.form_yaml,
      form_folder=form.form_folder,
      form_name=form.form_name,
      form_md5=form_md5
    )
    table_modified("forms_revisions")
    return form_md5

def output_mail(output, form_definition, form, to=None, record_id=None, _d=None, results=None):
    if type(to) in (str, unicode):
        to = [to]

    if to is None:
        to = output.get('To', set([]))

    if len(to) == 0:
        results = form_log(results, 1, "form.submit", "No mail destination", dict())
        return results

    for i, t in enumerate(to):
        if '@' not in t:
            t = email_of(t)
            if t is None:
                continue
            to[i] = t

    if len(to) == 0:
        results = form_log(results, 1, "form.submit", "No mail destination", dict())
        return results

    label = form_definition.get('Label', form.form_name)
    title = label
    try:
        d = get_form_formatted_data_o(output, form_definition, _d)
    except Exception, e:
        results = form_log(results, 1, "form.submit", str(e), dict())
        return results
    try:
        with open("applications/init/static/css/mail.css", "r") as f:
            style = f.read()
    except:
        style = ""

    now_s = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if record_id is not None:
        next = A(
          T("Open the workflow"),
          _href=URL(c="forms", f="workflow", vars={'wfid': record_id}, scheme=True),
        )
    else:
        next = ""

    form_html = PRE(sjson.dumps(_d, indent=4, default=datetime.datetime.isoformat))

    body = BODY(
      P(T("Form submitted on %(date)s by %(submitter)s", dict(date=now_s, submitter=user_name()))),
       form_html,
       next,
    )

    message = """
<html>
 <head>
  <style _type="text/css">
   %(style)s
  </style>
 </head>
 %(body)s
</html>
""" % dict(style=style, body=XML(body))
    mail.send(to=to,
              subject=title.encode("utf-8"),
              message=message)
    _to = str(', '.join(to))
    results = form_log(results, 0, "form.submit", "Mail sent to %(to)s on form %(form_name)s submission.", dict(to=_to, form_name=form.form_name))
    return results

def output_workflow(output, form_definition, form, _d=None, prev_wfid=None, results=None):
    d = get_form_formatted_data(output, form_definition, _d)

    form_md5 = insert_form_md5(form)

    if output.get('Scripts') is not None:
        if results['returncode'] == 0:
            script_defs = output['Scripts'].get('Success')
        else:
            script_defs = output['Scripts'].get('Error')

        if script_defs is None:
            next_forms = None
            form_assignee = None
        else:
            next_forms = script_defs.get('NextForms')
            form_assignee = script_defs.get('NextAssignee')
    else:
        next_forms = output.get('NextForms')
        form_assignee = output.get('NextAssignee')

    if next_forms is None or len(next_forms) == 0:
        next_id = 0
        status = "closed"
    else:
        next_id = None
        status = "pending"

    now = datetime.datetime.now()

    if prev_wfid is not None and prev_wfid != 'None':
        # workflow continuation
        q = db.forms_store.id == prev_wfid
        prev_wf = db(q).select(cacheable=True).first()
        if prev_wf.form_next_id is not None:
            results = form_log(results, 0, "form.store", "This step is already completed (id=%(id)d)", dict(id=prev_wf.id))
            return results

        if form_assignee is None:
            form_assignee = user_primary_group()
        if form_assignee is None:
            form_assignee = prev_wf.form_submitter
        if form_assignee is None:
            form_assignee = user_name()

        head_id = int(prev_wfid)
        max_iter = 100
        iter = 0
        while iter < max_iter:
            iter += 1
            q = db.forms_store.id == head_id
            row = db(q).select(cacheable=True).first()
            if row is None:
                break
            if row.form_prev_id is None:
                head = row
                break
            head_id = row.form_prev_id

        record_id = db.forms_store.insert(
          form_md5=form_md5,
          form_submitter=user_name(),
          form_assignee=form_assignee,
          form_submit_date=now,
          form_prev_id=prev_wfid,
          form_next_id=next_id,
          form_head_id=head_id,
          form_data=d,
          form_scripts=sjson.dumps(results["outputs"], default=datetime.datetime.isoformat),
        )
        table_modified("forms_store")
        if record_id is not None:
            q = db.forms_store.id == prev_wfid
            db(q).update(form_next_id=record_id)
        if next_id != 0:
            results = form_log(results, 0, "form.store", "Workflow %(head_id)d step %(form_name)s added with id %(id)d",
                        dict(form_name=form.form_name, head_id=head_id, id=record_id))
        else:
            results = form_log(results, 0, "form.store", "Workflow %(head_id)d closed on last step %(form_name)s with id %(id)d",
                        dict(form_name=form.form_name, head_id=head_id, id=record_id))
        q = db.workflows.form_head_id == head_id
        wfrow = db(q).select(cacheable=True).first()
        if wfrow is None:
            # should not happen ... recreate the workflow
            db.workflows.insert(
              status=status,
              form_md5=form_md5,
              steps=iter+1,
              last_assignee=form_assignee,
              last_update=now,
              last_form_id=record_id,
              last_form_name=form.form_name,
              form_head_id=head_id,
              creator=head.form_submitter,
              create_date=head.form_submit_date,
            )
        else:
            db(q).update(
              status=status,
              steps=iter+1,
              last_assignee=form_assignee,
              last_form_id=record_id,
              last_form_name=form.form_name,
              last_update=now,
            )
        table_modified("workflows")
    else:
        # new workflow
        if form_assignee is None:
            form_assignee = user_primary_group()
            if form_assignee is None:
                form_assignee = user_name()
        record_id = db.forms_store.insert(
          form_md5=form_md5,
          form_submitter=user_name(),
          form_assignee=form_assignee,
          form_submit_date=datetime.datetime.now(),
          form_data=d,
          form_scripts=sjson.dumps(results["outputs"], default=datetime.datetime.isoformat),
        )
        table_modified("forms_store")
        if record_id is not None:
            q = db.forms_store.id == record_id
            db(q).update(form_head_id=record_id)
        results = form_log(results, 0, "form.store", "New workflow %(form_name)s created with id %(id)d", dict(form_name=form.form_name, id=record_id))

        db.workflows.insert(
          status=status,
          form_md5=form_md5,
          steps=1,
          last_assignee=form_assignee,
          last_update=now,
          last_form_id=record_id,
          last_form_name=form.form_name,
          form_head_id=record_id,
          creator=user_name(),
          create_date=now,
        )
        table_modified("workflows")

    if next_id != 0 and output.get('Mail', False):
        results = output_mail(output, form_definition, form, to=form_assignee, record_id=record_id, _d=_d, results=results)

    db.commit()
    return results

def output_db(output, form_definition, _d=None, results=None):
    output['Type'] = 'object'
    output['Format'] = 'dict'
    d = get_form_formatted_data(output, form_definition, _d)
    if 'Table' not in output:
        results = form_log(results, 1, "form.submit", "Table must be set in db type Output", dict())
        return results
    table = output['Table']
    if table not in db:
        results = form_log(results, 1, "form.submit", "Table %(t)s not found", dict(t=table))
        return results

    # purge keys not present in table as columns
    keys = d.keys()
    for key in keys:
        if key not in db[table]:
            del(d[key])

    try:
        db[table].insert(**d)
        table_modified(table)
        results = form_log(results, 0, "form.submit", "Data inserted in database table", dict())
    except Exception, e:
        results = form_log(results, 1, "form.submit", "Data insertion in database table error: %(err)s", dict(err=str(e)))
    return results

def output_rest(output, form_definition, _d=None, results=None):
    import re

    d = get_form_formatted_data(output, form_definition, _d)
    action = output.get("Handler")
    url = output.get("Function")
    mangler = output.get("Mangle")
    output_id = output.get("Id")
    wait = output.get("WaitResult", 0)

    results = form_log(results,
      0,
      "form.submit",
      "%(output_id)s: rest %(action)s %(url)s",
      dict(
        output_id=output_id,
        action=action,
        url=url,
      )
    )
    update_results(results)

    if url is None:
        raise Exception("Function must be defined in a rest output")
    if action not in ("GET", "POST", "DELETE", "PUT"):
        raise Exception("Handler must be set to either GET, POST, DELETE or PUT in a rest output")

    def get_val(d, v):
        """
          Return the nested dict key value for key formatted as a.b.c
          Example:
            >>> d = {
              "a": {
                "b": {
                  "c": "foo"
                }
              }
            }
            >>> get_val(d, "a.b.c")
            foo
        """
        if type(v) == str:
            v = v.split(".")
        for key in v:
            if key not in d:
                raise ValueError
            if len(v) == 1:
                return d[key]
            return get_val(d[key], v[1:])

    def mangle(mangler, _d):
        """
          Run the mangler script in a nodejs vm
        """
        import tempfile
        f = tempfile.NamedTemporaryFile()
        fname = f.name
        s = """var mangle = %(mangler)s; var out = mangle(%(data)s, %(results)s); console.log(JSON.stringify(out));""" % dict(
          mangler=mangler,
          data=sjson.dumps(_d, default=datetime.datetime.isoformat),
          results=sjson.dumps(results["outputs"], default=datetime.datetime.isoformat),
        )
        f.write(s)
        f.flush()
        nodejs = config_get("nodejs", "/usr/bin/nodejs")
        vm2 = config_get("vm2", "/usr/local/bin/vm2")
        cmd = [nodejs, vm2, fname]
        import subprocess
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        f.close()
        l = [ line for line in out.split("\n") if "[vm] " not in line and line != ""]
        if len(l) == 0:
            raise Exception(out)
        return json.loads('\n'.join(l))

    #
    # prepare the rest url and args
    # args in the context contains the url path elements with references
    # substituted.
    #
    # ex:
    # url  = "/arrays/#id/diskgroups/#id/quotas"
    # =>
    # url  = "/arrays/554/diskgroups/2525/quotas"
    # args = ['arrays', 554, 'diskgroups', 2525, 'quotas']
    #
    args = []
    for s in url.rstrip("/").split("/"):
        if s == "":
            continue
        if s.startswith("#"):
            k = s.lstrip("#")
            val = str(get_val(_d, k))
            url = url.replace(s, val)
            args.append(val)
        else:
            args.append(s)

    # mangle the form data if a mangler is defined
    if mangler is None:
        vars = _d
    else:
        vars = mangle(mangler, _d)

    if type(vars) == str:
        raise Exception("The mangler must not return a str")

    # find the rest handler and execute the call
    handler = get_handler(action, url)

    for k in handler.props_blacklist:
        if k in vars:
            del(vars[k])

    # keep only keys specified by "Keys", if defined
    if len(output.get("Keys", [])) > 0:
        retain_keys = output.get("Keys")
        for k in list(vars.keys()):
            if k not in retain_keys:
                del(vars[k])

    def run_handler(args, vars, url, wait):
        if action == "GET" and wait:
            import time
            while wait > 0:
                db.commit()
                jd = _run_handler(args, vars, url)
                if "data" in jd and len(jd["data"]) > 0:
                    return jd
                wait -= 1
                time.sleep(1)
        else:
            return _run_handler(args, vars, url)
        raise Exception("Timed out waiting for a result")

    def _run_handler(args, vars, url):
        if type(vars) == list:
            return handler.handle_list(vars, url, {})
        else:
            return handler.handle(*args, **vars)

    results = form_log(results,
      0,
      "form.submit",
      "%(output_id)s: request data:\n%(data)s",
      dict(
        output_id=output_id,
        data=sjson.dumps(vars, indent=4, default=datetime.datetime.isoformat),
      )
    )
    update_results(results)

    try:
        jd = run_handler(args, vars, url, wait)
        if output_id and "data" in jd:
            results["outputs_order"].append(output_id)
            results["outputs"][output_id] = jd["data"]
    except Exception as e:
        results = form_log(results,
          1,
          "form.submit",
          "%(output_id)s: error:\n%(result)s",
          dict(
            output_id=output_id,
            result=str(e),
          )
        )
    return results

def output_script(output, form_definition, _d=None, results=None):
    import os
    import subprocess
    d = get_form_formatted_data(output, form_definition, _d)
    path = output.get('Path')
    output_id = output.get("Id", path)

    if path is None:
        results = form_log(results, 1, "form.submit", "Path must be set in script type Output", dict())
        results['returncode'] += 1
        results["outputs"][output_id] = {
          'path': path,
          'returncode': 1,
          'stdout': "",
          'stderr': "Path must be set in script type Output",
        }
        return results
    elif not os.path.exists(path):
        results = form_log(results, 1, "form.submit", "Script %(path)s does not exists", dict(path=path))
        results['returncode'] += 1
        results["output"][output_id] = {
          'path': path,
          'returncode': 1,
          'stdout': "",
          'stderr': "Script %(path)s does not exists"%dict(path=path),
        }
        return results

    try:
        p = subprocess.Popen([path, d], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        out, err = p.communicate()
    except Exception as e:
        results = form_log(results, 1, "form.submit", "Script %(path)s execution error: %(err)s", dict(path=path, err=str(e)))
        results['returncode'] += 1
        results["output"][output_id] = {
          'path': path,
          'returncode': 1,
          'stdout': "",
          'stderr': "Script %(path)s execution error: %(err)s" % dict(path=path, err=str(e))
        }
        return results

    results['returncode'] += p.returncode
    results["output"][output_id] = {
      'path': path,
      'returncode': p.returncode,
      'stdout': out,
      'stderr': err,
    }
    msg = out
    if len(err) > 0:
        msg += err

    if p.returncode != 0:
        results = form_log(results, 1, "form.submit", "Script %(path)s returned with error:\n%(err)s", dict(path=path, err=msg))
    else:
        results = form_log(results, 0, "form.submit", "Script %(path)s returned on success:\n%(out)s", dict(path=path, out=msg))

    return results

def workflow_continuation(form, prev_wfid):
    import yaml
    form_definition = yaml.load(form.form_yaml)

    for output in form_definition.get('Outputs', []):
        if output.get('Dest') == 'workflow':
            if prev_wfid is not None and prev_wfid != 'None':
                # workflow continuation
                q = db.forms_store.id == prev_wfid
                prev_wf = db(q).select(cacheable=True).first()
                if prev_wf.form_next_id is not None:
                    return True
    return False

def update_results(results):
    q = db.form_output_results.id == results["results_id"]
    db(q).update(
        results=sjson.dumps(results, default=datetime.datetime.isoformat)
    )
    db.commit()
    ws_send("form_output_results_change", {"results_id": results["results_id"]})

def form_submit(form, _d=None, prev_wfid=None):
    """
      Used by the PUT /forms/<id> handler to perform the server-side outputs
    """
    results = {
        "log": [],
        "outputs_order": [],
        "outputs": {},
        "returncode": 0,
        "status": "QUEUED",
    }
    authdump = {
        "user_id": auth.user_id,
        "user": dict(auth.user)
    }

    if workflow_continuation(form, prev_wfid):
        results["log"].append((1, "form.store",  "This step is already completed (id=%(id)d)", dict(id=prev_wfid)))
        return results

    results["results_id"] = db.form_output_results.insert(
        user_id=auth.user_id if auth.user_id > 0 else None,
        node_id=auth.user.node_id if "node_id" in auth.user else None,
        results=sjson.dumps(results, default=datetime.datetime.isoformat)
    )

    # load form definition from yaml
    import yaml
    form_definition = yaml.load(form.form_yaml)

    if form_definition.get("Async", False):
        rconn.rpush("osvc:q:form_submit", json.dumps([
            form.id,
            _d,
            prev_wfid,
            results,
            authdump,
        ]))
        return results
    else:
        return _form_submit(form.id, _d=_d, prev_wfid=prev_wfid, results=results)

def _form_submit(form_id, _d=None, prev_wfid=None, results=None, authdump=None):
    from gluon.storage import Storage
    import yaml

    # restore auth
    if authdump:
        global auth
        auth = Storage(authdump)
        auth.user = Storage(auth.user)

    # load form definition from yaml
    form = db.forms[form_id]
    form_definition = yaml.load(form.form_yaml)

    results["status"] = "RUNNING"
    update_results(results)

    # assign missing output ids
    for idx, output in enumerate(form_definition.get("Outputs", [])):
        if "Id" in output:
            continue
        form_definition["Outputs"][idx]["Id"] = "output-%d" % idx

    for output in ordered_outputs(form_definition):
        try:
            chkcond = check_output_condition(output, form, form_definition, _d)
        except Exception as e:
            results = form_log(results, 1, "form.submit", str(e), dict())
            update_results(results)
            continue

        if not chkcond:
            continue

        dest = output.get('Dest')

        try:
            if dest == "db":
                results = output_db(output, form_definition, _d=_d,
                                    results=results)
            elif dest == "script":
                results = output_script(output, form_definition, _d=_d,
                                        results=results)
            elif dest == "rest":
                results = output_rest(output, form_definition, _d=_d,
                                      results=results)
            elif dest == "mail":
                results = output_mail(output, form_definition, form, _d=_d,
                                      results=results)
            elif dest == "workflow":
                results = output_workflow(output, form_definition, form, _d=_d,
                                          prev_wfid=prev_wfid, results=results)
        except Exception, e:
            results = form_log(results, 1, "form.submit", str(e), dict())
            update_results(results)
            break

        update_results(results)

    results["status"] = "COMPLETED"
    update_results(results)
    return results

def lib_forms_add_default_team_responsible(form_name):
    q = db.forms.form_name == form_name
    form_id = db(q).select()[0].id
    group_id = user_default_group_id()
    db.forms_team_responsible.insert(form_id=form_id, group_id=group_id)
    table_modified("forms_team_responsible")

def lib_forms_add_default_team_publication(form_name):
    q = db.forms.form_name == form_name
    form_id = db(q).select()[0].id
    group_id = user_default_group_id()
    db.forms_team_publication.insert(form_id=form_id, group_id=group_id)
    table_modified("forms_team_publication")


