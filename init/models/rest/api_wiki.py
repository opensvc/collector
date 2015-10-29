from gluon.dal import smart_query

class rest_get_wiki(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display wiki by node name.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/wiki/%(node)s",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/wiki/<id>",
          tables=["v_wiki_events"],
          desc=desc,
          orderby=~db.v_wiki_events.saved_on,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.v_wiki_events.name == id
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_post_wiki(rest_post_handler):
    def __init__(self):
        desc = [
          "Insert a wiki.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST -d tag_name=foo https://%(collector)s/init/rest/api/wiki/%(node)s",
        ]
        rest_post_handler.__init__(
          self,
          path="/wiki/<id>",
          tables=["wiki_pages"],
          desc=desc,
          examples=examples
        )

    def handler(self, id, **vars):
        #check_privilege("TagManager")
        if 'body' not in vars:
            raise Exception({"error": "the body property is mandatory"})
        body = vars['body']

        db.wiki_pages.insert(
        name=id,
        title='',
        author=auth.user.id,
        saved_on=request.now,
        body=body
        )

        q = db.wiki_pages.name==id
        
        data = db(q).select().first()
        _log('wiki.create',
             "wiki '%(wiki_id)s' created",
             dict(wiki_id=data.id),
            )
        return dict(info="wiki created", data=data)