#!/usr/bin/python

from __future__ import print_function
import sys
import os
import MySQLdb
import re

web2py_d = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(web2py_d)

from gluon.validators import CRYPT

if len(sys.argv) != 2:
    print(sys.argv[0], "<new password>", file=sys.stderr)
    sys.exit(1)

new_password = sys.argv[1]

def get_conn():
    try:
        from applications.init.modules.config import dbopensvc_password
    except:
        dbopensvc_password = "opensvc"

    try:
        conn = MySQLdb.connect(host="127.0.0.1",
                               user="root",
                               passwd=dbopensvc_password,
                               db="opensvc")
    except MySQLdb.Error as e:
        print("Error %d: %s" % (e.args[0], e.args[1]))
        return
    return conn

def chpw_web2py():
    fpath = os.path.join(web2py_d, "parameters_443.py")
    s = str(CRYPT()(new_password)[0])
    with open(fpath, "w") as f:
        f.write('password="'+s+'"')
    print("web2py password changed")

def chpw_db():
    conn = get_conn()
    if conn is None:
        sys.exit(1)
    cursor = conn.cursor()
    cursor.execute("""select Host, User, Password from mysql.user where User in ("opensvc", "pdns", "root", "readonly") """)
    todo = []
    while (1):
        row = cursor.fetchone()
        if row is None:
            break
        host, user, pw = row
        todo.append("""SET PASSWORD FOR '%s'@'%s' = PASSWORD("%s") """ % (user, host, new_password))

    for cmd in todo:
        print(cmd)
        cursor.execute(cmd)

    conn.close()

def chpw_app():
    cf = os.path.join(web2py_d, "applications", "init", "modules", "config.py")
    with open(cf, "r") as f:
        lines = f.read().split("\n")
    found_dbopensvc_password = False
    found_dbdns_password = False
    found_dbro_password = False
    for i, line in enumerate(lines):
        if re.match(r'^\s*dbopensvc_password\s*=', line):
            print("change dbopensvc_password parameter in", cf)
            found_dbopensvc_password = True
            lines[i] = 'dbopensvc_password = "%s"' % new_password
        if re.match(r'^\s*dbdns_password\s*=', line):
            print("change dbdns_password parameter in", cf)
            found_dbdns_password = True
            lines[i] = 'dbdns_password = "%s"' % new_password
        if re.match(r'^\s*dbro_password\s*=', line):
            print("change dbro_password parameter in", cf)
            found_dbro_password = True
            lines[i] = 'dbro_password = "%s"' % new_password
    if not found_dbopensvc_password:
        print("append dbopensvc_password parameter to", cf)
        lines.append('dbopensvc_password = "%s"' % new_password)
    if not found_dbdns_password:
        print("append dbdns_password parameter to", cf)
        lines.append('dbdns_password = "%s"' % new_password)
    if not found_dbro_password:
        print("append dbro_password parameter to", cf)
        lines.append('dbro_password = "%s"' % new_password)
    print("rewrite", cf)
    with open(cf, "w") as f:
        f.write("\n".join(lines))
    print("reload uwsgi")
    os.system("pkill -1 -o uwsgi")

def chpw_actiond():
    cf = os.path.join(web2py_d, "applications", "init", "actiond", "config.py")
    if not os.path.exists(cf):
        open(cf, 'a').close()
    with open(cf, "r") as f:
        lines = f.read().split("\n")
    found_dbopensvc_password = False
    for i, line in enumerate(lines):
        if re.match(r'^\s*dbopensvc_password\s*=', line):
            print("change dbopensvc_password parameter in", cf)
            found_dbopensvc_password = True
            lines[i] = 'dbopensvc_password = "%s"' % new_password
    if not found_dbopensvc_password:
        print("append dbopensvc_password parameter to", cf)
        lines.append('dbopensvc_password = "%s"' % new_password)
    print("rewrite", cf)
    with open(cf, "w") as f:
        f.write("\n".join(lines))
        if lines[-1] != "":
            f.write("\n")
    print("reload actiond")
    os.system("/etc/init.d/actiond restart")

chpw_web2py()
chpw_db()
chpw_app()
chpw_actiond()

