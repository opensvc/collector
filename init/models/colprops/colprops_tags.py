tags_cols = [
  'id',
  'tag_name',
  'tag_exclude',
  'tag_created',
]

tags_colprops = {
    'tag_name': HtmlTableColumn(
             table='tags',
             field='tag_name',
            ),
    'tag_created': HtmlTableColumn(
             table='tags',
             field='tag_created',
            ),
    'tag_exclude': HtmlTableColumn(
             table='tags',
             field='tag_exclude',
            ),
    'id': HtmlTableColumn(
             table='tags',
             field='id',
            ),
}

v_tags_colprops = {
    'tag_name': HtmlTableColumn(
             table='v_tags',
             field='tag_name',
            ),
}


