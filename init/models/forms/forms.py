
def convert_val(val, t):
     if t == 'string':
         val = str(val)
     elif t == 'text':
         val = str(val)
     elif t == 'string or integer':
         try:
             val = int(val)
         except:
             val = str(val)
     elif t == 'integer':
         try:
             val = int(val)
         except:
             if val != "":
                 raise Exception("Error converting to integer")
     elif t == "list of string":
         l = val.split(',')
         val = map(lambda x: x.strip(), l)
     elif t == "size":
         val = val.strip()
         if len(val) < 2:
             raise Exception("Error converting size. Too short.")
         i = 0
         while val[i].isdigit():
             i += 1
             continue
         unit = val[i:]
         try:
             val = int(val[0:i])
         except:
             raise Exception("Error converting size. Error converting to integer")
         if unit in ("K", "k", "KB"):
             val = val * 1024
         elif unit == "Kib":
             val = val * 1000
         elif unit in ("M", "m", "MB"):
             val = val * 1024 * 1024
         elif unit == "Pib":
             val = val * 1000 * 1000
         elif unit in ("G", "g", "GB"):
             val = val * 1024 * 1024 * 1024
         elif unit == "Gib":
             val = val * 1000 * 1000 * 1000
         elif unit in ("P", "p", "PB"):
             val = val * 1024 * 1024 * 1024 * 1024
         elif unit == "Pib":
             val = val * 1000 * 1000 * 1000 * 1000
         else:
             raise Exception("Error converting size. Unknown unit.")
     return val

def ordered_outputs(data):
    l = []
    h = {}

    dest_order = [
     'db',
     'compliance variable',
     'script',
     'workflow',
     'compliance fix',
     'mail',
    ]

    for output in data.get('Outputs', []):
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

def forms_xid(id=None):
    xid = "forms_"
    if request.vars.form_xid is not None:
        xid += request.vars.form_xid + '_'
    if id is not None:
        xid += str(id)
    return xid

def validate_input_value(val):
    if val is None:
        return False
    if type(val) in (str, unicode) and val in ("", "undefined"):
        return False
    return True

def get_form_formatted_data_o(output, data, _d=None):
    if _d is not None:
        return _d

    if 'Template' in output:
        output_value = output['Template']
        for input in data['Inputs']:
            val = request.vars.get(forms_xid(input['Id'])+'_0')
            if val is None:
                val = ""
            output_value = output_value.replace('%%'+input['Id']+'%%', str(val))
    elif output.get('Type') in ("json", "object"):
        if output.get('Format') == "list":
            l = []
            input = data['Inputs'][0]
            for v in sorted(request.vars.keys()):
                if not v.startswith(forms_xid(input['Id'])):
                    continue
                val = request.vars.get(v)
                if len(str(val)) == 0:
                    if input.get('Mandatory', False):
                        raise Exception(T("Input '%(input)s' is mandatory", dict(input=input.get('Id'))))
                    continue
                try:
                    val = convert_val(val, input['Type'])
                except Exception, e:
                    raise Exception(T(str(e)))
                if validate_input_value(val):
                    l.append(val)
            output_value = l
        elif output.get('Format') == "dict":
            h = {}
            for input in data['Inputs']:
                key = input.get('Key')
                if key is None:
                    key = input.get('Id')
                if key is None:
                    continue
                if key in h and h[key] not in (None, "", "undefined"):
                    # multiple inputs with the same key
                    continue
                val = request.vars.get(forms_xid(input['Id'])+'_0')
                if val is None:
                    if input.get('Mandatory', False):
                        raise Exception(T("Input '%(input)s' is mandatory", dict(input=input.get('Id'))))
                    continue
                if len(str(val)) == 0:
                    if input.get('Mandatory', False):
                        raise Exception(T("Input '%(input)s' is mandatory", dict(input=input.get('Id'))))
                    continue
                try:
                    val = convert_val(val, input['Type'])
                except Exception, e:
                    raise Exception(T(str(e)))
                if validate_input_value(val):
                    h[key] = val
                    h[input['Id']] = val
            output_value = h
        elif output.get('Format') == "list of dict":
            h = {}
            idxs = []
            for v in sorted(request.vars.keys()):
                for input in data['Inputs']:
                    if not v.startswith(forms_xid(input['Id'])):
                        continue
                    idx = v.replace(forms_xid(input['Id'])+'_', '')
                    try:
                        int(idx)
                    except:
                        # wrong input, with same prefix.
                        continue
                    if idx not in h:
                        h[idx] = {}
                        idxs.append(idx)

                    key = input.get('Key')
                    if key is None:
                        key = input.get('Id')
                    if key is None:
                        continue
                    if key in h[idx] and h[idx][key] not in (None, "", "undefined"):
                        # multiple inputs with the same key
                        continue

                    val = request.vars.get(v)
                    if len(str(val)) == 0:
                        if 'Mandatory' in input and input['Mandatory']:
                            raise Exception(T("Input '%(input)s' is mandatory (instance %(inst)s)", dict(input=input.get('Id'), inst=idx)))
                    try:
                        val = convert_val(val, input.get('Type', 'string'))
                    except Exception, e:
                        raise Exception(T(str(e)))
                    if validate_input_value(val):
                        h[idx][key] = val
                        h[idx][input['Id']] = val
            output_value = [h[i] for i in idxs]
        elif output.get('Format') == "dict of dict":
            h = {}
            for v in request.vars.keys():
                for input in data['Inputs']:
                    if not v.startswith(forms_xid(input['Id'])):
                        continue
                    idx = v.replace(forms_xid(input['Id'])+'_', '')
                    if idx not in h:
                        h[idx] = {}

                    key = input.get('Key')
                    if key is None:
                        key = input.get('Id')
                    if key is None:
                        continue
                    if key in h[idx] and h[idx][key] not in (None, "", "undefined"):
                        # multiple inputs with the same key
                        continue

                    val = request.vars.get(v)
                    if len(str(val)) == 0:
                        if 'Mandatory' in input and input['Mandatory']:
                            raise Exception(T("Input '%(input)s' is mandatory (instance %(inst)s)", dict(input=input.get('Id'), inst=idx)))
                        continue
                    try:
                        val = convert_val(val, input['Type'])
                    except Exception, e:
                        raise Exception(T(str(e)))
                    if validate_input_value(val):
                        h[idx][key] = val
                        h[idx][input['Id']] = val
            if 'Key' not in output:
                raise Exception(T("'Key' must be defined in form Output of 'dict of dict' format"))
            k = output['Key']
            _h = {}
            for idx, d in h.items():
                if k not in d:
                    continue
                _k = d[k]
                if not output.get('EmbedKey', True):
                    del(d[k])
                _h[_k] = d
            output_value = _h
        else:
            raise Exception(T("Unknown output format: %(fmt)s", dict(fmt=output.get('Format', 'none'))))
    else:
        raise Exception(T("Output must have a Template or Type must be json."))

    return output_value

def check_output_condition(output, form, data, _d=None):
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

    o = get_form_formatted_data_o(output, data, _d)

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

def get_form_formatted_data(output, data, _d=None):
    output_value = get_form_formatted_data_o(output, data, _d)

    if output.get('Type') == "json":
        output_value = json.dumps(output_value)

    return output_value

def fmt_action(nodename, svcname, action, action_type="push", mod=[], modset=[]):
    base_cmd = ['compliance', action]
    if len(mod) > 0:
        base_cmd += ['--module', ','.join(mod)]
    if len(modset) > 0:
        base_cmd += ['--moduleset', ','.join(modset)]
    if action_type == "pull":
        return ' '.join(cmd)

    if svcname is None or svcname == "":
        _cmd = ["/opt/opensvc/bin/nodemgr"]
    else:
        _cmd = ["/opt/opensvc/bin/svcmgr", "-s", svcname]

    cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                  '-o', 'ForwardX11=no',
                  '-o', 'PasswordAuthentication=no',
                  '-o', 'ConnectTimeout=5',
#                  '-t',
           'opensvc@'+nodename,
           '--',
           'sudo'] + _cmd + base_cmd
    return ' '.join(cmd)

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

def ajax_custo_form_submit(output, data):
    # logging buffer
    log = []

    rset_name = request.vars.rset_name

    # target selectors
    if request.vars.svcname is not None:
        rset_name = "svc."+request.vars.svcname
    elif request.vars.nodename is not None:
        rset_name = "node."+request.vars.nodename
    elif request.vars.rset is not None:
        rset_name = request.vars.rset

    if request.vars.var_id is not None:
        q = db.comp_rulesets_variables.id == request.vars.var_id
        q &= db.comp_rulesets_variables.ruleset_id == db.comp_rulesets.id
        var = db(q).select(cacheable=True).first()
        if var is None:
            log.append((1, "", "Specified variable not found (id=%(id)s)", dict(id=request.vars.var_id)))
            return log
        var_name = var.comp_rulesets_variables.var_name
        var_class = var.comp_rulesets_variables.var_class
        rset_name = var.comp_rulesets.ruleset_name

    if rset_name is None:
        log.append((1, "", "No ruleset name specified. Skip compliance variable creation", dict()))
        return dict(log=log, err="break")

    # validate privs
    groups = []
    common_groups = []
    if request.vars.nodename is not None:
        q = db.nodes.nodename == request.vars.nodename
        q &= db.nodes.team_responsible == db.auth_group.role
        node = db(q).select(db.auth_group.id, cacheable=True).first()
        if node is None:
            log.append((1, "", "Unknown specified node %(nodename)s", dict(nodename=nodename)))
            return log
        groups = [node.id]
        if len(groups) == 0:
            log.append((1, "", "Specified node %(nodename)s has no responsible group", dict(nodename=nodename)))
            return log
        common_groups = set(user_group_ids()) & set(groups)
        if len(common_groups) == 0:
            log.append((1, "", "You are not allowed to create or modify a ruleset for the node %(node)s", dict(nodename=nodename)))
            return log
    elif request.vars.svcname is not None:
        q = db.services.svc_name == request.vars.svcname
        svc = db(q).select(cacheable=True).first()
        if svc is None:
            log.append((1, "", "Unknown specified service %(svcname)s", dict(svcname=svcname)))
            return log
        q &= db.services.svc_app == db.apps.app
        q &= db.apps.id == db.apps_responsibles.app_id
        rows = db(q).select(cacheable=True)
        groups = map(lambda x: x.apps_responsibles.group_id, rows)
        if len(groups) == 0:
            log.append((1, "", "Specified service %(svcname)s has no responsible groups", dict(svcname=svcname)))
            return log
        common_groups = set(user_group_ids()) & set(groups)
        if len(common_groups) == 0:
            log.append((1, "", "You are not allowed to create or modify a ruleset for the service %(svcname)s", dict(svcname=svcname)))
            return log
    elif request.vars.rset is not None:
        q = db.comp_rulesets.ruleset_name == request.vars.rset
        rset = db(q).select(cacheable=True).first()
        if rset is None:
            log.append((1, "", "Unknown specified ruleset %(rset)s", dict(rset=request.vars.rset)))
            return log
        q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
        q &= db.comp_ruleset_team_responsible.group_id == db.auth_group.id
        rows = db(q).select(cacheable=True)
        groups = map(lambda x: x.auth_group.id, rows)
        common_groups = set(user_group_ids()) & set(groups)
        if len(common_groups) == 0:
            log.append((1, "", "You are not allowed to create or modify the ruleset %(rset)s", dict(rset=rset_name)))
            return log

    # create ruleset
    q = db.comp_rulesets.ruleset_name == rset_name
    rset = db(q).select(cacheable=True).first()
    if rset is None:
        db.comp_rulesets.insert(ruleset_name=rset_name,
                                ruleset_type="explicit",
                                ruleset_public="T")
        table_modified("comp_rulesets")
        log.append((0, "compliance.ruleset.add", "Added explicit published ruleset '%(rset_name)s'", dict(rset_name=rset_name)))
        rset = db(q).select(cacheable=True).first()
        for gid in common_groups:
            db.comp_ruleset_team_responsible.insert(
              ruleset_id=rset.id,
              group_id=gid
            )
            db.comp_ruleset_team_publication.insert(
              ruleset_id=rset.id,
              group_id=gid
            )
            table_modified("comp_ruleset_team_responsible")
            log.append((0, "compliance.ruleset.group.attach", "Added group %(gid)d to ruleset '%(rset_name)s' responsibles", dict(gid=gid, rset_name=rset_name)))
            table_modified("comp_ruleset_team_publication")
            log.append((0, "compliance.ruleset.group.attach", "Added group %(gid)d to ruleset '%(rset_name)s' publication", dict(gid=gid, rset_name=rset_name)))
    if rset is None:
        log.append((1, "", "error fetching %(rset_name)s ruleset", dict(rset_name=rset_name)))
        return log

    if request.vars.var_id is None:
        if 'Class' in output:
            var_class = output['Class']
        else:
            var_class = 'raw'

        if request.vars.var_name is not None:
            var_name_prefix = request.vars.var_name
        elif 'Prefix' in output:
            var_name_prefix = output['Prefix']
        else:
            var_name_prefix = '_'.join((output.get('Class', 'noclass'), str(rset.id), ''))
            #log.append((1, "", "No variable name specified.", dict()))
            #return log

        q = db.comp_rulesets_variables.ruleset_id == rset.id
        q &= db.comp_rulesets_variables.var_name.like(var_name_prefix+'%')
        var_name_suffixes = map(lambda x: x.var_name.replace(var_name_prefix, ''), db(q).select(cacheable=True))
        i = 0
        while True:
            _i = str(i)
            if _i not in var_name_suffixes: break
            i += 1
        var_name = var_name_prefix + _i
    try:
        var_value = get_form_formatted_data(output, data)
    except Exception, e:
        log.append((1, "compliance.ruleset.variable.change", str(e), dict()))
        return log

    q = db.comp_rulesets_variables.ruleset_id == rset.id
    q &= db.comp_rulesets_variables.var_name == var_name
    n = db(q).count()

    if n == 0 and request.vars.var_id is not None:
        log.append((1, "compliance.ruleset.variable.change", "%(var_class)s' variable '%(var_name)s' does not exist in ruleset %(rset_name)s or invalid attempt to edit a variable in a parent ruleset", dict(var_class=var_class, var_name=var_name, rset_name=rset_name)))
        return log

    q &= db.comp_rulesets_variables.var_value == var_value
    n = db(q).count()
    __var_id = request.vars.var_id

    if n > 0:
        log.append((1, "compliance.ruleset.variable.add", "'%(var_class)s' variable '%(var_name)s' already exists with the same value in the ruleset '%(rset_name)s': cancel", dict(var_class=var_class, var_name=var_name, rset_name=rset_name)))
    else:
        q = db.comp_rulesets_variables.ruleset_id == rset.id
        q &= db.comp_rulesets_variables.var_name == var_name
        # ownership check
        var_rows = db(q).select(cacheable=True)
        n = len(var_rows)
        owned = True
        if "Manager" not in user_groups():
            q1 = db.comp_ruleset_team_responsible.ruleset_id == rset.id
            q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
            if db(q&q1).count() == 0:
                owned = False
        if n == 0:
            __var_id = db.comp_rulesets_variables.insert(
              ruleset_id=rset.id,
              var_name=var_name,
              var_value=var_value,
              var_class=var_class,
              var_author=user_name(),
              var_updated=datetime.datetime.now(),
            )
            table_modified("comp_rulesets_variables")
            log.append((0, "compliance.ruleset.variable.add", "Added '%(var_class)s' variable '%(var_name)s' to ruleset '%(rset_name)s' with value:\n%(var_value)s", dict(var_class=var_class, var_name=var_name, rset_name=rset_name, var_value=var_value)))
        elif not owned:
            if n == 1:
                log.append((1, "compliance.ruleset.variable.change", "Change '%(var_class)s' variable '%(var_name)s' in ruleset '%(rset_name)s' aborted: not owner", dict(var_class=var_class, var_name=var_name, rset_name=rset_name)))
            else:
                log.append((1, "compliance.ruleset.variable.add", "Add '%(var_class)s' variable '%(var_name)s' in ruleset '%(rset_name)s' aborted: not owner", dict(var_class=var_class, var_name=var_name, rset_name=rset_name)))
        elif n == 1:
            __var_id = var_rows.first().id
            db(q).update(
              var_value=var_value,
              var_class=var_class,
              var_author=user_name(),
              var_updated=datetime.datetime.now(),
            )
            table_modified("comp_rulesets_variables")
            log.append((0, "compliance.ruleset.variable.change", "Modified '%(var_class)s' variable '%(var_name)s' in ruleset '%(rset_name)s' with value:\n%(var_value)s", dict(var_class=var_class, var_name=var_name, rset_name=rset_name, var_value=var_value)))
        else:
            log.append((1, "compliance.ruleset.variable.change", "More than one variable found matching '%(var_name)s' in ruleset '%(rset_name)s'. Skip edition.", dict(var_name=var_name, rset_name=rset_name)))

    if request.vars.nodename is not None or request.vars.svcname is not None:
        modset_ids = []
        if 'Modulesets' in data:
            q = db.comp_moduleset.modset_name.belongs(data['Modulesets'])
            rows = db(q).select(db.comp_moduleset.id, cacheable=True)
            modset_ids = map(lambda x: x.id, rows)

        rset_ids = []
        if 'Rulesets' in data:
            q = db.comp_rulesets.ruleset_name.belongs(data['Rulesets'])
            q &= db.comp_rulesets.ruleset_type == "explicit"
            q &= db.comp_rulesets.ruleset_public == True
            rows = db(q).select(db.comp_rulesets.id, cacheable=True)
            rset_ids = map(lambda x: x.id, rows) + [rset.id]

        if request.vars.nodename is not None:
            # check node_team_responsible_id ?
            try:
                log += internal_comp_attach_modulesets(node_names=[request.vars.nodename],
                                       modset_ids=modset_ids)
            except ToolError:
                pass
            try:
                log += internal_comp_attach_rulesets(node_names=[request.vars.nodename],
                                              ruleset_ids=rset_ids)
            except ToolError:
                pass

        if request.vars.svcname is not None:
            # check svc_team_responsible_id ?
            try:
                log += internal_comp_attach_svc_modulesets(svc_names=[request.vars.svcname],
                                                  modset_ids=modset_ids,
                                                  slave=True)
            except ToolError:
                pass
            try:
                log += internal_comp_attach_svc_rulesets(svc_names=[request.vars.svcname],
                                                ruleset_ids=rset_ids,
                                                slave=True)

            except ToolError:
                pass

    return dict(log=log, var_id=__var_id)

def mail_form(output, data, form, to=None, record_id=None, _d=None):
    if to is None:
        to = output.get('To', set([]))

    if len(to) == 0:
        return [(1, "form.submit", "No mail destination", dict())]

    if '@' not in to:
        to = email_of(to)

    if to is None:
        return [(1, "form.submit", "No mail destination", dict())]

    if type(to) in (str, unicode):
        to = [to]

    label = data.get('Label', form.form_name)
    title = label
    try:
        d = get_form_formatted_data_o(output, data, _d)
    except Exception, e:
        return [(1, "form.submit", str(e), dict())]
    try:
        with open("applications/init/static/mail.css", "r") as f:
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

    body = BODY(
      P(T("Form submitted on %(date)s by %(submitter)s", dict(date=now_s, submitter=user_name()))),
      _ajax_forms_inputs(
         _mode="showdetailed",
         form=form,
         form_output=output,
         showexpert=True,
         current_values=d,
       ),
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
    return [(0, "form.submit", "Mail sent to %(to)s on form %(form_name)s submission." , dict(to=_to, form_name=form.form_name))]

def form_submit(form, data,
                _d=None,
                var_id=None, prev_wfid=None,
                svcname=None, nodename=None):
    log = []
    __var_id = var_id
    _scripts = {'returncode': 0}
    for output in data.get('Outputs', []):
        if output.get('Dest') == 'workflow':
            if prev_wfid is not None and prev_wfid != 'None':
                # workflow continuation
                q = db.forms_store.id == prev_wfid
                prev_wf = db(q).select(cacheable=True).first()
                if prev_wf.form_next_id is not None:
                    log.append((1, "form.store",  "This step is already completed (id=%(id)d)", dict(id=prev_wf.id)))
                    return log

    record_id = None
    for output in ordered_outputs(data):
        try:
            chkcond = check_output_condition(output, form, data, _d)
        except Exception as e:
            log.append((1, "form.submit", str(e), dict()))
            continue
        if not chkcond:
            continue
        dest = output.get('Dest')
        if dest == "db":
            output['Type'] = 'object'
            output['Format'] = 'dict'
            try:
                d = get_form_formatted_data(output, data, _d)
            except Exception, e:
                log.append((1, "form.submit", str(e), dict()))
                break
            if 'Table' not in output:
                log.append((1, "form.submit", "Table must be set in db type Output", dict()))
                continue
            table = output['Table']
            if table not in db:
                log.append((1, "form.submit", "Table %(t)s not found", dict(t=table)))
                continue

            # purge keys not present in table as columns
            keys = d.keys()
            for key in keys:
                if key not in db[table]:
                    del(d[key])

            try:
                db[table].insert(**d)
                table_modified(table)
                log.append((0, "form.submit", "Data inserted in database table", dict()))
            except Exception, e:
                log.append((1, "form.submit", "Data insertion in database table error: %(err)s", dict(err=str(e))))
        elif dest == "compliance fix":
            if record_id is None:
                log.append((1, "form.submit", "Can not execute the 'compliance fix' without a valid workflow", dict()))
                continue
            modsets = data.get("Modulesets", [])
            if len(modsets) == 0:
                log.append((1, "form.submit", "'Modulesets' must be specified in the form definition for the 'compliance fix' output", dict()))
                continue
            vals = []
            vars = ['nodename', 'svcname', 'action_type', 'command', 'user_id', 'form_id']
            if __var_id is not None:
                q = db.comp_rulesets_variables.id == __var_id
                q &= db.comp_rulesets_variables.ruleset_id == db.comp_rulesets.id
                if "Manager" not in user_groups():
                    q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
                    q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
                row = db(q).select(db.comp_rulesets.ruleset_name, cacheable=True).first()
                if row is None:
                    log.append((1, "form.submit", "Unable to retrieve compliance variable %(var_id)s ruleset name", dict(var_id=__var_id)))
                    continue
                rset_name = row.ruleset_name
                if rset_name.startswith('svc.'):
                    svcname = rset_name.replace('svc.', '')
                elif rset_name.startswith('node.'):
                    nodename = rset_name.replace('node.', '')
                else:
                    log.append((1, "form.submit", "Unable to deduce service or nodename from ruleset name %(rset_name)s", dict(rset_name=rset_name)))
                    continue
            if nodename is None and svcname is None:
                log.append((1, "form.submit", "No nodename nor svcname specified to 'compliance fix' output handler", dict()))
                continue
            nodes = [nodename]
            if nodename is None and svcname is not None:
                q = db.svcmon.mon_svcname == svcname
                rows = db(q).select(db.svcmon.mon_nodname, cacheable=True)
                if len(rows) == 0:
                    log.append((1, "form.submit", "No nodes found running service %(svcname)s", dict(svcname=svcname)))
                    continue
                nodes = [r.mon_nodname for r in rows]

            _scripts['async'] = len(nodes)
            q = db.forms_store.id == record_id
            db(q).update(form_scripts=json.dumps(_scripts))

            for nodename in nodes:
                q = db.nodes.nodename == nodename
                row = db(q).select(db.nodes.os_name, db.nodes.fqdn, cacheable=True).first()
                if row is None:
                    log.append((1, "form.submit", "No asset information found for node %(nodename)s", dict(nodename=nodename)))
                    continue
                if row.fqdn is not None and len(row.fqdn) > 0:
                    node = row.fqdn
                else:
                    node = nodename


                if row.os_name == "Windows":
                    action_type = "pull"
                else:
                    action_type = "push"

                vals.append([nodename,
                             svcname,
                             action_type,
                             fmt_action(node,
                                        svcname,
                                        "check",
                                        action_type,
                                        modset=modsets),
                             str(auth.user_id),
                             str(record_id)
                            ])

            purge_action_queue()
            generic_insert('action_queue', vars, vals)
            action_q_event()
            log.append((0, "form.submit", "Compliance fix commands queued for asynchronous execution on %(nodes)s", dict(nodes=', '.join(nodes))))

            from subprocess import Popen
            import sys
            actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
            process = Popen([sys.executable, actiond])
            process.communicate()
        elif dest == "script":
            import os
            import subprocess
            try:
                d = get_form_formatted_data(output, data, _d)
            except Exception, e:
                log.append((1, "form.submit", str(e), dict()))
                break
            path = output.get('Path')
            if path is None:
                log.append((1, "form.submit", "Path must be set in script type Output", dict()))
                _scripts['returncode'] += 1
                _scripts[path] = {
                  'path': path,
                  'returncode': 1,
                  'stdout': "",
                  'stderr': "Path must be set in script type Output",
                }
                continue
            if not os.path.exists(path):
                log.append((1, "form.submit", "Script %(path)s does not exists", dict(path=path)))
                _scripts['returncode'] += 1
                _scripts[path] = {
                  'path': path,
                  'returncode': 1,
                  'stdout': "",
                  'stderr': "Script %(path)s does not exists"%dict(path=path),
                }
                continue
            try:
                p = subprocess.Popen([path, d], stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
                out, err = p.communicate()
            except Exception as e:
                log.append((1, "form.submit", "Script %(path)s execution error: %(err)s", dict(path=path, err=str(e))))
                _scripts['returncode'] += 1
                _scripts[path] = {
                  'path': path,
                  'returncode': 1,
                  'stdout': "",
                  'stderr': "Script %(path)s execution error: %(err)s "%dict(path=path, err=str(e))
                }
                continue

            _scripts['returncode'] += p.returncode
            _scripts[path] = {
              'path': path,
              'returncode': p.returncode,
              'stdout': out,
              'stderr': err,
            }
            msg = out
            if len(err) > 0:
                msg += err
            if p.returncode != 0:
                log.append((1, "form.submit", "Script %(path)s returned with error:\n%(err)s", dict(path=path, err=msg)))
                continue
            log.append((0, "form.submit", "script %(path)s returned on success:\n%(out)s", dict(path=path, out=msg)))
        elif dest == "mail":
            log += mail_form(output, data, form, _d=_d)
        elif dest == "workflow":
            try:
                d = get_form_formatted_data(output, data, _d)
            except Exception, e:
                log.append((1, "form.submit", str(e), dict()))
                break

            form_md5 = insert_form_md5(form)

            if output.get('Scripts') is not None:
                if _scripts['returncode'] == 0:
                    script_defs = output['Scripts'].get('Success')
                else:
                    script_defs = output['Scripts'].get('Error')

                if 'async' in _scripts:
                    next_forms = ['to be determined']
                    form_assignee = None
                elif script_defs is None:
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
                    log.append((0, "form.store",
                                "This step is already completed (id=%(id)d)",
                                dict(id=prev_wf.id)))
                    continue

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
                  form_scripts=json.dumps(_scripts),
                  form_var_id=__var_id,
                )
                table_modified("forms_store")
                if record_id is not None:
                    q = db.forms_store.id == prev_wfid
                    db(q).update(form_next_id=record_id)
                if next_id != 0:
                    log.append((0, "form.store", "Workflow %(head_id)d step %(form_name)s added with id %(id)d",
                                dict(form_name=form.form_name, head_id=head_id, id=record_id)))
                else:
                    log.append((0, "form.store", "Workflow %(head_id)d closed on last step %(form_name)s with id %(id)d",
                                dict(form_name=form.form_name, head_id=head_id, id=record_id)))
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
                  form_scripts=json.dumps(_scripts),
                  form_var_id=__var_id,
                )
                table_modified("forms_store")
                if record_id is not None:
                    q = db.forms_store.id == record_id
                    db(q).update(form_head_id=record_id)
                log.append((0, "form.store", "New workflow %(form_name)s created with id %(id)d", dict(form_name=form.form_name, id=record_id)))

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
                log += mail_form(output, data, form, to=form_assignee, record_id=record_id, _d=_d)

            db.commit()

        elif dest == "compliance variable":
            r = ajax_custo_form_submit(output, data)
            if type(r) == dict:
                __log = r.get("log")
                __err = r.get("err")
                __var_id = r.get("var_id")
            else:
                __log = r
                __err = None
                __var_id = var_id
            log += __log
            if __err == "break":
                break

        elif dest == "compliance variable delete":
            if __var_id is not None:
                q = db.comp_rulesets_variables.id == __var_id
                skip = False
                if "Manager" not in user_groups():
                    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
                    q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
                    if db(q&q1).count() == 0:
                        skip = True
                if not skip:
                    db(q).delete()
                    table_modified("comp_rulesets_variables")
                    log.append((0, "", "Compliance variable %(id)s deleted", dict(id=__var_id)))
                else:
                    log.append((0, "", "Compliance variable %(id)s not deleted: not owner", dict(id=__var_id)))

    for ret, action, fmt, d in log:
        _log(action, fmt, d)

    return log

