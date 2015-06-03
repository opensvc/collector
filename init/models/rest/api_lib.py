def check_privilege(priv):
    ug = user_groups()
    if 'Manager' in ug:
        return
    if priv not in ug:
        raise Exception("Not authorized: user has no %s privilege" % priv)

def props_to_cols(props, tables=[], blacklist=[]):
    if props is None:
        if len(tables) == 1:
            table = tables[0]
            cols = []
            for p in set(db[table].fields) - set(blacklist):
                cols.append(db[table][p])
            return cols
        else:
            cols = []
            for table in tables:
                for p in set(db[table].fields) - set(blacklist):
                    cols.append(db[table][p])
            return cols
    cols = []
    for p in props.split(","):
        v = p.split(".")
        if len(v) == 1 and len(tables) == 1:
            v = [tables[0], p]
        cols.append(db[v[0]][v[1]])
    return cols


