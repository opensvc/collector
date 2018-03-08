tags_cols = [
  'tag_id',
  'tag_name',
  'tag_exclude',
  'tag_data',
  'tag_created',
]

tags_colprops = {
    'tag_name': HtmlTableColumn(
             table='tags',
             field='tag_name',
            ),
    'tag_data': HtmlTableColumn(
             table='tags',
             field='tag_data',
            ),
    'tag_created': HtmlTableColumn(
             table='tags',
             field='tag_created',
            ),
    'tag_exclude': HtmlTableColumn(
             table='tags',
             field='tag_exclude',
            ),
    'tag_id': HtmlTableColumn(
             table='tags',
             field='tag_id',
            ),
}

v_tags_colprops = {
    'tag_name': HtmlTableColumn(
             table='v_tags',
             field='tag_name',
            ),
}


