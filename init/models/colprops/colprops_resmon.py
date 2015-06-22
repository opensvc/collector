resmon_colprops = {
    'rid': HtmlTableColumn(
             title='Resource id',
             table='resmon',
             field='rid',
             img='svc',
             display=True,
            ),
    'res_desc': HtmlTableColumn(
             title='Description',
             field='res_desc',
             img='svc',
             display=True,
            ),
    'res_status': HtmlTableColumn(
             title='Status',
             field='res_status',
             img='svc',
             display=True,
             _class="status",
            ),
    'res_log': HtmlTableColumn(
             title='Log',
             field='res_log',
             img='svc',
             display=True,
            ),
    'changed': HtmlTableColumn(
             title='Last change',
             field='changed',
             img='time16',
             display=True,
             _class='datetime_no_age',
            ),
    'updated': HtmlTableColumn(
             title='Updated',
             field='updated',
             img='time16',
             display=True,
             _class='datetime_status',
            )
}


