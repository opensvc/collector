networks_cols = [
  'id',
  'name',
  'pvid',
  'network',
  'broadcast',
  'netmask',
  'gateway',
  'begin',
  'end',
  'prio',
  'team_responsible',
  'comment',
  'updated'
]

networks_colprops = {
    'id': HtmlTableColumn(
             field='id',
            ),
    'pvid': HtmlTableColumn(
             field='pvid',
            ),
    'begin': HtmlTableColumn(
             field='begin',
            ),
    'end': HtmlTableColumn(
             field='end',
            ),
    'gateway': HtmlTableColumn(
             field='gateway',
            ),
    'prio': HtmlTableColumn(
             field='prio',
            ),
    'comment': HtmlTableColumn(
             field='comment',
            ),
    'name': HtmlTableColumn(
             field='name',
            ),
    'network': HtmlTableColumn(
             field='network',
            ),
    'broadcast': HtmlTableColumn(
             field='broadcast',
            ),
    'netmask': HtmlTableColumn(
             field='netmask',
            ),
    'team_responsible': HtmlTableColumn(
             field='team_responsible',
            ),
    'updated': HtmlTableColumn(
             field='updated',
            ),
}

