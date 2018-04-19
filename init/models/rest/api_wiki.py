
class rest_get_wikis(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display wiki by node name.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/wiki",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/wiki",
          tables=["v_wiki_events"],
          desc=desc,
          orderby=~db.v_wiki_events.id,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.v_wiki_events.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_get_wiki(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a wiki page.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/wiki/node1",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/wiki/<id>",
          tables=["v_wiki_events"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.v_wiki_events.id == id
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_post_wikis(rest_post_handler):
    def __init__(self):
        desc = [
          "Insert a wiki page revision.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST -d tag_name=foo https://%(collector)s/init/rest/api/wiki",
        ]
        rest_post_handler.__init__(
          self,
          path="/wiki",
          tables=["wiki_pages"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if 'name' not in vars:
            raise HTTP(400, "the name property is mandatory")
        name = vars['name']

        if 'body' not in vars:
            raise HTTP(400, "the body property is mandatory")
        body = vars['body']

        id = db.wiki_pages.insert(
            name=name,
            title=vars.get("title", ""),
            author=auth.user.id,
            saved_on=request.now,
            body=body
        )

        _log('wiki.create',
             "wiki '%(wiki_id)s' created",
             dict(wiki_id=id),
        )
        return dict(info="wiki '%(wiki_id)d' created" % dict(wiki_id=id))

