class table_networks(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)

        # from models/colprops/
        self.cols = networks_cols
        self.colprops = networks_colprops

        self.csv_limit = 30000

        for c in self.cols:
            self.colprops[c].table = 'networks'

        self.ajax_col_values = 'ajax_networks_col_values'

@auth.requires_login()
def ajax_networks_col_values():
    table_id = request.vars.table_id
    t = table_networks(table_id, 'ajax_networks')
    col = request.args[0]
    o = db.networks[col]
    q = q_filter(group_field=db.networks.team_responsible)
    for f in t.cols:
        q = _where(q, 'networks', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_networks():
    table_id = request.vars.table_id
    t = table_networks(table_id, 'ajax_networks')

    o = t.get_orderby(default=~db.networks.name)
    q = q_filter(group_field=db.networks.team_responsible)
    for f in set(t.cols):
        q = _where(q, 'networks', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_limit = 10000
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=True)
        return t.table_lines_data(n, html=False)


@auth.requires_login()
def networks():
    t = SCRIPT(
          """table_networks("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def networks_load():
    return networks()["table"]


#
# network segments
#
class table_network_segments(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)

        self.cols = [
            "seg_id",
            "seg_type",
            "seg_begin",
            "seg_end",
            "net_id",
            "name",
            "pvid",
            "network",
            "broadcast",
            "netmask",
            "gateway",
            "begin",
            "end",
            "prio",
            "team_responsible",
            "comment",
            "updated",
        ]
        self.colprops = {
            "seg_id": HtmlTableColumn(
                table="network_segments",
                field="id",
            ),
            "net_id": HtmlTableColumn(
                table="network_segments",
                field="net_id",
            ),
            "seg_type": HtmlTableColumn(
                table="network_segments",
                field="seg_type",
            ),
            "seg_begin": HtmlTableColumn(
                table="network_segments",
                field="seg_begin",
            ),
            "seg_end": HtmlTableColumn(
                table="network_segments",
                field="seg_end",
            ),
            "pvid": HtmlTableColumn(
                table="networks",
                field="pvid",
            ),
            "begin": HtmlTableColumn(
                table="networks",
                field="begin",
            ),
            "end": HtmlTableColumn(
                table="networks",
                field="end",
            ),
            "gateway": HtmlTableColumn(
                table="networks",
                field="gateway",
            ),
            "prio": HtmlTableColumn(
                table="networks",
                field="prio",
            ),
            "comment": HtmlTableColumn(
                table="networks",
                field="comment",
            ),
            "name": HtmlTableColumn(
                table="networks",
                field="name",
            ),
            "network": HtmlTableColumn(
                table="networks",
                field="network",
            ),
            "broadcast": HtmlTableColumn(
                table="networks",
                field="broadcast",
            ),
            "netmask": HtmlTableColumn(
                table="networks",
                field="netmask",
            ),
            "team_responsible": HtmlTableColumn(
                table="networks",
                field="team_responsible",
            ),
            "updated": HtmlTableColumn(
                table="networks",
                field="updated",
            ),
        }

        self.csv_limit = 30000

        self.ajax_col_values = 'ajax_network_segments_col_values'

@auth.requires_login()
def ajax_network_segments_col_values():
    table_id = request.vars.table_id
    t = table_network_segments(table_id, 'ajax_network_segments')
    col = request.args[0]
    o = db.network_segments[col]
    q = q_filter(group_field=db.networks.team_responsible)
    q &= db.networks.id == db.network_segments.net_id
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_network_segments():
    table_id = request.vars.table_id
    t = table_network_segments(table_id, 'ajax_network_segments')

    o = ~db.network_segments.seg_begin
    q = q_filter(group_field=db.networks.team_responsible)
    q &= db.networks.id == db.network_segments.net_id
    for f in set(t.cols):
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_limit = 10000
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=True)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def network_segments():
    t = SCRIPT(
          """table_network_segments("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def network_segments_load():
    return network_segments()["table"]

