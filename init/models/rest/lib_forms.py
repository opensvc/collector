import gluon.contrib.simplejson as sjson
from applications.init.modules import gittrack;

def form_log(output_id, results, ret, action, fmt, d):
    if ret == 0:
        level = "info"
    else:
        level = "error"
    if output_id not in results["log"]:
        results["log"][output_id] = []
    results["log"][output_id].append([ret, fmt, d])
    try:
        _log(action, fmt, d, level=level)
    except AttributeError:
        # before auth restore
        pass
    return results

def form_get_val(d, v):
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
        >>> form_get_val(d, "a.b.c")
        foo
    """
    if type(v) in (str, unicode):
        v = v.split(".")
    for key in v:
        if key not in d:
            raise ValueError(key)
        if len(v) == 1:
            return d[key]
        return form_get_val(d[key], v[1:])

def form_rest_args(url, _d):
    #
    # prepare the rest url and args
    # args in the context contains the url path elements with references
    # substituted.
    #
    # ex:
    # url  = "/arrays/#id/diskgroups/#id/quotas"
    # =>
    # args = ['arrays', 554, 'diskgroups', 2525, 'quotas']
    #
    args = []
    for s in url.rstrip("/").split("/"):
        if s == "":
            continue
        if s.startswith("#"):
            k = s.lstrip("#")
            val = str(form_get_val(_d, k))
            args.append(val)
        else:
            args.append(s)
    return args

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
    output_id = output.get("Id")
    if type(to) in (str, unicode):
        to = [to]

    if to is None:
        to = output.get('To', set([]))

    if len(to) == 0:
        results = form_log(output_id, results, 1, "form.submit", "No mail destination", dict())
        return results

    for i, t in enumerate(to):
        if '@' not in t:
            t = email_of(t)
            if t is None:
                continue
            to[i] = t

    if len(to) == 0:
        results = form_log(output_id, results, 1, "form.submit", "No mail destination", dict())
        return results

    label = form_definition.get('Label', form.form_name)
    title = label
    try:
        d = get_form_formatted_data_o(output, form_definition, _d)
    except Exception, e:
        results = form_log(output_id, results, 1, "form.submit", str(e), dict())
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
    results = form_log(output_id, results, 0, "form.submit", "Mail sent to %(to)s on form %(form_name)s submission.", dict(to=_to, form_name=form.form_name))
    return results

def output_workflow(output, form_definition, form, _d=None, prev_wfid=None, results=None):
    output_id = output.get("Id")
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
            results = form_log(output_id, results, 0, "form.store", "This step is already completed (id=%(id)d)", dict(id=prev_wf.id))
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
          results_id=results["results_id"],
        )
        table_modified("forms_store")
        if record_id is not None:
            q = db.forms_store.id == prev_wfid
            db(q).update(form_next_id=record_id)
        if next_id != 0:
            results = form_log(output_id, results, 0, "form.store", "Workflow %(head_id)d step %(form_name)s added with id %(id)d",
                        dict(form_name=form.form_name, head_id=head_id, id=record_id))
        else:
            results = form_log(output_id, results, 0, "form.store", "Workflow %(head_id)d closed on last step %(form_name)s with id %(id)d",
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
          results_id=results["results_id"],
        )
        table_modified("forms_store")
        if record_id is not None:
            q = db.forms_store.id == record_id
            db(q).update(form_head_id=record_id)
        results = form_log(output_id, results, 0, "form.store", "New workflow %(form_name)s created with id %(id)d", dict(form_name=form.form_name, id=record_id))

        wfid = db.workflows.insert(
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
	results["outputs"][output_id] = {"workflow_id": wfid, "head_form_id": record_id}
	update_results(results)

    if next_id != 0 and output.get('Mail', False):
        results = output_mail(output, form_definition, form, to=form_assignee, record_id=record_id, _d=_d, results=results)

    db.commit()
    return results

def output_db(output, form_definition, _d=None, results=None):
    output_id = output.get("Id")
    output['Type'] = 'object'
    output['Format'] = 'dict'
    d = get_form_formatted_data(output, form_definition, _d)
    if 'Table' not in output:
        results = form_log(output_id, results, 1, "form.submit", "Table must be set in db type Output", dict())
        return results
    table = output['Table']
    if table not in db:
        results = form_log(output_id, results, 1, "form.submit", "Table %(t)s not found", dict(t=table))
        return results

    # purge keys not present in table as columns
    keys = d.keys()
    for key in keys:
        if key not in db[table]:
            del(d[key])

    try:
        db[table].insert(**d)
        table_modified(table)
        results = form_log(output_id, results, 0, "form.submit", "Data inserted in database table", dict())
    except Exception, e:
        results = form_log(output_id, results, 1, "form.submit", "Data insertion in database table error: %(err)s", dict(err=str(e)))
    return results

def output_rest(output, form_definition, _d=None, results=None):
    import re

    d = get_form_formatted_data(output, form_definition, _d)
    action = output.get("Handler")
    url = output.get("Function")
    mangler = output.get("Mangle")
    output_id = output.get("Id")
    wait = output.get("WaitResult", 0)

    results = form_log(output_id, results,
      0,
      "form.submit",
      "rest %(action)s %(url)s",
      dict(
        action=action,
        url=url,
      )
    )
    update_results(results)

    if url is None:
        raise Exception("Function must be defined in a rest output")
    if action not in ("GET", "POST", "DELETE", "PUT"):
        raise Exception("Handler must be set to either GET, POST, DELETE or PUT in a rest output")

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
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        f.close()
        l = [ line for line in out.split("\n") if "[vm] " not in line and line != ""]
        if len(l) == 0:
            raise Exception(out)
        return json.loads('\n'.join(l))

    args = form_rest_args(url, _d)

    # mangle the form data if a mangler is defined
    if mangler is None:
        vars = _d
    else:
        vars = mangle(mangler, _d)

    if type(vars) == str:
        raise Exception("The mangler must not return a str")

    if not args[0].startswith("http"):
        # find the rest handler and execute the call
        handler = get_handler(action, url)

        for k in handler.props_blacklist:
            if k in vars:
                del(vars[k])

    # keep only keys specified by "Keys", if defined
    retain_keys = output.get("Keys")
    if retain_keys and isinstance(retain_keys, list):
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
        if args[0].startswith("http"):
            return handle_external(args, vars)
        if type(vars) == list:
            return handler.handle_list(vars, url, {})
        else:
            return handler.handle(*args, **vars)

    def handle_external(args, vars):
        args.insert(1, "")
        url = "/".join(args)
        import requests
        if action == "GET":
            result = requests.get(url, data=vars)
        elif action == "POST":
            result = requests.post(url, data=vars)
        elif action == "DELETE":
            result = requests.delete(url, data=vars)
        elif action == "PUT":
            result = requests.put(url, data=vars)
        return result.json()

    if output.get("LogRequestData", True) == True:
        results["request_data"][output_id] = vars

    update_results(results)

    def post_run(jd, results):
        if "info" in jd:
            if isinstance(jd["info"], list):
                for line in jd["info"]:
                    results["log"][output_id].append((0, line, {}))
            elif len(jd["info"]) > 0:
                results["log"][output_id].append((0, jd["info"], {}))
        if "error" in jd:
            results["returncode"] += 1
            if isinstance(jd["error"], list):
                for line in jd["error"]:
                    results["log"][output_id].append((1, line, {}))
            elif isinstance(jd["error"], (dict, pydal.objects.Row)):
                if isinstance(jd["error"], pydal.objects.Row):
                    d = jd["error"].as_dict()
                else:
                    d = jd["error"]
                for key, val in d.items():
                    results["log"][output_id].append((1, key+": "+str(val), {}))
            elif len(jd["error"]) > 0:
                results["log"][output_id].append((1, jd["error"], {}))

        if "data" not in jd:
            return results

        results["outputs"][output_id] = jd["data"]

        if output.get("WaitResult", 0) > 0:
            if isinstance(jd["data"], list):
                for entry in jd["data"]:
                    results = _post_run(entry, results)
            elif isinstance(jd["data"], dict):
                results = _post_run(jd["data"], results)

        return results

    def _post_run(entry, results):
        if "ret" in entry and entry["ret"] != 0:
            results["returncode"] += 1
        if "stderr" in entry and len(entry["stderr"]) > 0:
            results["log"][output_id].append((1, entry["stderr"], {}))
        return results

    try:
        jd = run_handler(args, vars, url, wait)
        results = post_run(jd, results)
    except Exception as e:
        results = form_log(output_id, results,
          1,
          "form.submit",
          "error:\n%(result)s",
          dict(
            result=str(e),
          )
        )
        results["returncode"] += 1
    return results

def output_script(output, form_definition, _d=None, results=None):
    import os
    import subprocess
    d = get_form_formatted_data(output, form_definition, _d)
    path = output.get('Path')
    output_id = output.get("Id", path)

    if path is None:
        results = form_log(output_id, results, 1, "form.submit", "Path must be set in script type Output", dict())
        results['returncode'] += 1
        return results
    elif not os.path.exists(path):
        results = form_log(output_id, results, 1, "form.submit", "Script %(path)s does not exists", dict(path=path))
        results['returncode'] += 1
        return results

    out = []
    err = []
    import select
    try:
        s_results = sjson.dumps(results, default=datetime.datetime.isoformat)
        proc = subprocess.Popen(["stdbuf", "-o0", "-e0", "-i0",
                                 path, d, output_id, s_results],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                bufsize=1)
        while True:
            reads = [proc.stdout.fileno(), proc.stderr.fileno()]
            ret = select.select(reads, [], [])

            for fd in ret[0]:
                if fd == proc.stdout.fileno():
                    read = proc.stdout.readline()
                    results = form_log(output_id, results, 0, "form.submit", read, {})
                    out.append(read)
                if fd == proc.stderr.fileno():
                    read = proc.stderr.readline()
                    results = form_log(output_id, results, 1, "form.submit", read, {})
                    err.append(read)
                update_results(results, reload_outputs=True)
            if proc.poll() != None:
                break
        proc.wait()

        # read data liggering in fds
        for read in proc.stdout.readlines():
            results = form_log(output_id, results, 0, "form.submit", read, {})
            out.append(read)
        for read in proc.stderr.readlines():
            results = form_log(output_id, results, 1, "form.submit", read, {})
            err.append(read)
        update_results(results)
    except Exception as e:
        results = form_log(output_id, results, 1, "form.submit", "Script %(path)s execution error: %(err)s", dict(path=path, err=str(e)))
        results['returncode'] += 1
        return results

    results['returncode'] += proc.returncode

    if proc.returncode != 0:
        results = form_log(output_id, results, 1, "form.submit", "Script returned error code %(ret)s", dict(ret=str(proc.returncode)))

    return results

def workflow_continuation(form, prev_wfid):
    if form["id"] < 0:
        return False
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

def update_results(results, reload_outputs=False):
    q = db.form_output_results.id == results["results_id"]
    if reload_outputs:
        row = db(q).select().first()
        current = sjson.loads(row.results)
        results["outputs"].update(current["outputs"])

    def dbdo():
        db(q).update(
            results=sjson.dumps(results, default=datetime.datetime.isoformat)
        )
        db.commit()

    try:
        dbdo()
    except Exception as exc:
        s = str(exc).lower()
        if "server has gone away" in s or "Lost connection" in s or "socket.error" in s:
            db._adapter.close()
            db._adapter.reconnect()
            dbdo()
        raise
    ws_send("form_output_results_change", {"results_id": results["results_id"]})

def validate_data(form_definition, data):
    if isinstance(data, dict):
        _validate_data(form_definition, data)
    elif isinstance(data, list):
        for _data in data:
            _validate_data(form_definition, _data)

def _validate_data(form_definition, data):
    for _input in form_definition.get("Inputs"):
        validate_input_data(form_definition, data, _input)

def validate_input_data(form_definition, data, _input):
    input_id = _input.get("Id")
    val = data.get(input_id)

    if val is None:
        if _input.get("Mandatory", False):
            raise HTTP(400, "Missing value for mandatory input '%s'" % input_id)
        return

    #
    # val can be a list (ex: checklist inputs)
    # factorize the code by considering val is [val] when val is not already a list
    #
    if type(val) != list:
        vals = [val]
    else:
        vals = val

    #
    # Validate input keys
    #
    key_defs = _input.get("Keys", [])
    for key_def in key_defs:
        key, val = key_def.split("=", 1)
        key = key.strip()
        val = form_dereference(val.strip(), data)
        if key not in data:
            raise HTTP(400, "missing key '%s', from input %s" % (key, input_id))
        if "#" not in val and val != data[key]:
            # verify the submitted key value is aligned with the forced value in the form definition
            raise HTTP(400, "unallowed key value '%s=%s', expecting '%s', from input %s" % (key, str(data[key]), str(val), input_id))

    #
    # Validate strict candidates in static input
    #
    if _input.get("Candidates") and _input.get("StrictCandidates"):
        candidate_vals = []
        for candidate in _input.get("Candidates"):
            if isinstance(candidate, dict) and "Value" in candidate:
                candidate_vals.append(candidate["Value"])
            else:
                candidate_vals.append(candidate)
        for val in vals:
            if val not in candidate_vals:
                raise HTTP(400, "Input '%s' value '%s' not in allowed candidates" % (input_id, str(val)))

    #
    # Validate dynamic input
    #
    key = None

    # Look for the input_id key in the keys first as they are added last to the
    # data
    for key_def in key_defs:
        _key, _val = key_def.split("=", 1)
        _key = _key.strip()
        if _key == input_id:
            key = _val.strip()

    # Fallback to the "Value" input property value.
    if key is None:
        key = _input.get("Value")

    fn = _input.get("Function")
    if fn is not None and key is not None:
        fn = form_dereference(fn, data)
        if fn.startswith("/"):
            handler = get_handler("GET", fn)
            args = form_rest_args(fn, data)
            kwargs = {}
            for entry in _input.get("Args", []):
                entry = form_dereference(entry, data)
                idx = entry.index("=")
                kwargs[entry[:idx].strip()] = entry[idx+1:].strip()
            for kwarg, _val in kwargs.items():
                kwargs[kwarg] = form_dereference(_val, data)
            candidates = handler.handle(*args, **kwargs)["data"]
            key = key.lstrip("#")
            try:
                candidates = [form_get_val(candidate, key) for candidate in candidates]
            except ValueError:
                raise HTTP(400, "Key '%s' not in candidates" % key)
            for val in vals:
                try:
                    int_val = int(val)
                except ValueError:
                    int_val = val
                if val not in candidates and int_val not in candidates and unicode(val) not in candidates:
                    raise HTTP(400, "Input '%s' value '%s' not in allowed candidates %s obtained from %s" % (input_id, str(val), str(candidates), "/"+"/".join(args)))

def form_dereference(s, data, prefix=""):
    for key in sorted(data.keys(), reverse=True):
        val = data[key]
        if isinstance(val, dict):
            s = form_dereference(s, val, prefix=prefix+key+".")
        else:
            try:
                s = s.replace("#"+prefix+key, unicode(val))
            except Exception as e:
                raise Exception("Dereference '%s' error: %s, data: %s" % (key, str(e), str(data)))
    return s

def form_submit(form, _d=None, prev_wfid=None):
    """
      Used by the PUT /forms/<id> handler to perform the server-side outputs
    """
    try:
        # reconnect if needed
        db.commit()
    except:
        pass

    results = {
        "outputs_order": [],
        "request_data": {},
        "outputs": {},
        "log": {},
        "returncode": 0,
        "status": "QUEUED",
    }
    authdump = auth_dump()

    if workflow_continuation(form, prev_wfid):
        results["log"].append((1, "form.store",  "This step is already completed (id=%(id)d)", dict(id=prev_wfid)))
        return results

    # load form definition from yaml
    if "form_yaml" in form:
        import yaml
        form_definition = yaml.load(form.form_yaml)
    else:
        form_definition = form["form_definition"]

    validate_data(form_definition, _d)

    results["results_id"] = db.form_output_results.insert(
        user_id=auth.user_id if auth.user_id > 0 else None,
        node_id=auth.user.node_id if "node_id" in auth.user else None,
        svc_id=auth.user.svc_id if "svc_id" in auth.user else None,
        results=sjson.dumps(results, default=datetime.datetime.isoformat)
    )

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
    try:
        results = __form_submit(form_id, _d=_d, prev_wfid=prev_wfid, results=results, authdump=authdump)
    except Exception as exc:
        if "server has gone away" in str(exc).lower():
            # let task_rq manage reconnect
            raise
        results["status"] = "COMPLETED"
        if "Lost connection" not in str(exc):
            results["returncode"] += 1
            form_log("", results, 1, "form.submit", str(exc), {})
    finally:
        results["status"] = "COMPLETED"
    update_results(results)
    return results

def __form_submit(form_id, _d=None, prev_wfid=None, results=None, authdump=None):
    from gluon.storage import Storage
    import yaml

    # restore auth
    if authdump:
        global auth
        auth = Storage(authdump)
        auth.user = Storage(auth.user)

    # load form definition from yaml
    if form_id < 0:
        form = get_internal_form(form_id)
        form_definition = form.form_definition
    else:
        form = db.forms[form_id]
        form_definition = yaml.load(form.form_yaml)

    results["status"] = "RUNNING"
    update_results(results)

    # assign missing output ids
    for idx, output in enumerate(form_definition.get("Outputs", [])):
        if "Id" in output:
            continue
        form_definition["Outputs"][idx]["Id"] = "output-%d" % idx

    for output in form_definition.get('Outputs', []):
        output_id = output.get("Id")
        results["log"][output_id] = []
        results["outputs_order"].append(output_id)
        if output.get("SkipOnErrors", False) and results["returncode"] != 0:
            results = form_log(output_id, results, 1, "form.submit",
                               "%(output_id)s: skip (previous output error)",
                               {"output_id": output.get("Id")})
            update_results(results)
            continue

        try:
            chkcond = check_output_condition(output, form, form_definition, _d)
        except Exception as e:
            results = form_log(output_id, results, 1, "form.submit", str(e), dict())
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
            results = form_log(output_id, results, 1, "form.submit", str(e), dict())
            results["returncode"] += 1
            break

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

def lib_form_add_to_git(form_id, yaml):
    o = gittrack.gittrack(otype='forms')
    r = o.commit(form_id, yaml, author=user_name(email=True))

def lib_form_revision(form_id, cid):
    o = gittrack.gittrack(otype='forms')
    data = o.lstree_data(cid, form_id)
    oid = data[0]["oid"]
    return {"data": o.show_file_unvalidated(cid, oid, form_id)}

def lib_form_revisions(form_id):
    o = gittrack.gittrack(otype='forms')
    r = o.timeline([form_id])
    return {"data": r}

def lib_form_diff(form_id, cid, other=None):
    o = gittrack.gittrack(otype='forms')
    if other:
        r = o.diff_cids(form_id, cid, other, filename="forms")
    else:
        r = o.show(cid, form_id, numstat=True)
    return {"data": r}

def lib_form_rollback(form_id, cid):
    o = gittrack.gittrack(otype='forms')
    r = o.rollback(form_id, cid, author=user_name(email=True))
    row = db(db.forms.id == form_id).select().first()
    here_d = os.path.dirname(__file__)
    collect_d = os.path.join(here_d, '..', 'private', 'forms')
    with open (collect_d+"/"+form_id+"/forms", "r") as myfile:
        data=myfile.readlines()
    row.update_record(form_yaml=''.join(data))
