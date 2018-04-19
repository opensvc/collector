
class rest_get_links(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Get links.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/links",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/links",
          tables=["links"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.links.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_get_link(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Return a link.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/link/md5",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/links/<id>",
          tables=["links"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.links.link_md5 == id

        # Update consultation timestamp
        db(db.links.link_md5 == id).update(
          link_last_consultation_date=request.now,
          link_access_counter=db.links.link_access_counter+1
        )

        self.set_q(q)
        return self.prepare_data(**vars)

class rest_post_link(rest_post_handler):
    def __init__(self):
        desc = [
          "Insert a link.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST -d tag_name=foo https://%(collector)s/init/rest/api/link",
        ]
        rest_post_handler.__init__(
          self,
          path="/links",
          tables=["links"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if 'fn' not in vars:
            raise HTTP(400, "the fn property is mandatory")
        fn = vars['fn']

        param = vars.get("param")
        if param:
            param = json.dumps(param)
        else:
            param = ""

        title_args = vars.get("title_args")
        if param:
            title_args = json.dumps(title_args)
        else:
            title_args = ""

        import hashlib
        hash = hashlib.md5()
        hash.update(fn)
        hash.update(param)

        md5id =hash.hexdigest()

        #Check if md5 already exist
        if not db(db.links.link_md5==md5id).select():
            id = db.links.insert(
                link_function=fn,
                link_title=vars.get("title", ""),
                link_title_args=title_args,
                link_parameters=param,
                link_creation_user_id=auth.user.id,
                link_creation_date=request.now,
                link_last_consultation_date=request.now,
                link_md5=md5id,
                link_access_counter=0
            )

            _log('link.add',
                "link '%(link_md5)s' created",
                dict(link_md5=md5id),
            )
        return dict(link_id="%(link_id)s" % dict(link_id=md5id))
