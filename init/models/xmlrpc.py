import datetime

def value_wrap(a):
    return "%(a)s=values(%(a)s)"%dict(a=a)

def quote_wrap(x):
    if isinstance(x, (int, long, float, complex)):
        return x
    elif isinstance(x, datetime.datetime):
        return "'%s'"%str(x)
    elif isinstance(x, (str, unicode)):
        if len(x) == 0:
            return "''"
        elif x[0] == "'" and x[-1] == "'":
            return x
        elif x[0] == '"' and x[-1] == '"':
            return x
        else:
            return "'%s'"%x.replace("'", '"')
    raise Exception("quote_wrap: unhandled type %s"%str(x.__class__))

def insert_multiline(table, vars, valsl):
    value_wrap = lambda a: "%(a)s=values(%(a)s)"%dict(a=a)
    line_wrap = lambda x: "(%(x)s)"%dict(x=','.join(map(quote_wrap, x)))
    upd = map(value_wrap, vars)
    lines = map(line_wrap, valsl)
    sql="""insert delayed into %s (%s) values %s on duplicate key update %s""" % (table, ','.join(vars), ','.join(lines), ','.join(upd))
    db.executesql(sql)
    db.commit()

def generic_insert(table, vars, vals):
    if len(vals) == 0:
        return
    elif isinstance(vals[0], list):
        insert_multiline(table, vars, vals)
    else:
        insert_multiline(table, vars, [vals])


