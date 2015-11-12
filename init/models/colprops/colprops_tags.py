tags_cols = [
  'id',
  'tag_name',
  'tag_exclude',
  'tag_created',
]

tags_colprops = {
    'tag_name': HtmlTableColumn(
             title='Tag name',
             table='tags',
             field='tag_name',
             img='tag16',
             display=True,
            ),
    'tag_created': HtmlTableColumn(
             title='Tag created',
             table='tags',
             field='tag_created',
             img='time16',
             display=True,
             _class='datetime_no_age',
            ),
    'tag_exclude': HtmlTableColumn(
             title='Tag exclude',
             table='tags',
             field='tag_exclude',
             img='tag16',
             display=True,
             _class='tag_exclude',
            ),
    'id': HtmlTableColumn(
             title='Id',
             table='tags',
             field='id',
             img='tag16',
             display=False,
            ),
}

v_tags_colprops = {
    'tag_name': HtmlTableColumn(
             title='Tag name',
             table='v_tags',
             field='tag_name',
             img='tag16',
             display=True,
            ),
}


