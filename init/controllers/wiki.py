from gluon.contrib.markdown import WIKI

def _get_pages(page_name, limitby=(0,1)):
    qset=db(db.wiki_pages.name==page_name)
    pages = qset.select(orderby=~db.wiki_pages.saved_on,limitby=limitby)
    if pages and pages.first().name!=page_name: raise HTTP(404)
    return pages

@auth.requires_login()
def wiki_page_log(page_name):
    pages = _get_pages(page_name, limitby=(0,5))
    l = []
    for p in pages:
        l.append(TR(TD(p.saved_on), TD(user_fullname(p.author))))
    return SPAN(T('Last five changes:'), TABLE(*l))

@auth.requires_login()
def ajax_wiki_save():
    id = request.args[0]
    page_name = request.args[1]
    body = request.vars['wiki_e_body_'+id]
    db.wiki_pages.insert(
        name=page_name,
        title='',
        author=auth.user.id,
        saved_on=request.now,
        body=body
    )
    return _ajax_wiki(id, page_name)

@auth.requires_login()
def ajax_wiki():
    id = request.args[0]
    page_name = request.args[1]
    return _ajax_wiki(id, page_name)

@auth.requires_login()
def _ajax_wiki(id, page_name):
    page = _get_pages(page_name).first()
    if page is None:
        return wiki_edit(id, page_name)
    wiki = DIV(
             DIV(
               WIKI(page.body),
               HR(),
               A(
                 T('Edit'),
                 _onclick="show_eid('wiki_e_%(id)s');hide_eid('wiki_v_%(id)s')"%dict(id=id),
               ),
               BR(),
               wiki_page_log(page_name),
               _id='wiki_v_%(id)s'%dict(id=id),
             ),
             DIV(
               wiki_edit(id, page_name),
               _id='wiki_e_%(id)s'%dict(id=id),
               _class='hidden',
             ),
           )
    return wiki

@auth.requires_login()
def wiki_edit(id, page_name):
    old_page = _get_pages(page_name).first()
    if old_page:
        body = old_page.body
    else:
        body = ''
    form = DIV(
             TEXTAREA(
               value=body,
               _type='text',
               _cols=100,
               _id='wiki_e_body_%(id)s'%dict(id=id),
             ),
             BR(),
             A(
               T('Save'),
               _onclick="ajax('%(url)s',['wiki_e_body_%(id)s'], '%(id)s')"%dict(
                 id=id,
                 url=URL(r=request, c='wiki', f='ajax_wiki_save',
                         args=[id, page_name]),
               ),
             ),
             ' ',
             A(
               T('Help'),
               _onclick="ajax('%(url)s',[], 'wiki_e_syntax_%(id)s')"%dict(
                 id=id,
                 url=URL(r=request, c='wiki', f='ajax_wiki_syntax'),
               ),
             ),
             DIV(
               _id='wiki_e_syntax_%(id)s'%dict(id=id),
             ),
           )
    return form

@auth.requires_login()
def ajax_wiki_syntax():
    return DIV(
             H2(T("Headers:")),
             PRE("""Section Header
==============

Subsection Header
-----------------"""),
             H2(T("Lists:")),
             PRE("""- A bullet list item

- Second item

  - A sub item

- Third item
1) An enumerated list item

2) Second item

   a) Sub item

      i) Sub-sub item

3) Third item
#) Another enumerated list item

#) Second item"""),
            H2(T("Named links:")),
            PRE("""A sentence with links to Wikipedia_ and the `Linux kernel archive`_.

.. _Wikipedia: http://www.wikipedia.org/
.. _Linux kernel archive: http://www.kernel.org/"""),
            H2(T("Anonymous links:")),
            PRE("""Another sentence with an `anonymous link to the Python website`__.

__ http://www.python.org/
"""),
          )
