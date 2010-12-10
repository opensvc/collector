def tool_search():
    result_id = 'search_result'
    d = DIV(
          SPAN(
            _style='padding-right: 0.5em',
          ),
          INPUT(
            _id='search',
            _onKeyUp="""show_result('%(url)s', '%(id)s')"""%dict(
                id=result_id,
                url=URL(r=request, c='ajax_search', f='ajax_search'),
              ),
          ),
          DIV(
            'foo',
            _name=result_id,
            _id=result_id,
            _class='white_float',
            _style='max-width:50%;display:none',
          ),
          _class='search',
        )
    return d
