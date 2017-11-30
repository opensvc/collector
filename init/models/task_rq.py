def enqueue_async_task(fn, args=[], kwargs={}):
    rconn.rpush("osvc:q:async", json.dumps({
        "fn": fn,
        "args": args,
        "auth": auth_dump(),
    }))

def task_rq(rqueues, getfn, app="feed"):
    import socket

    def db_disconnect_handler():
        try:
            db._adapter.close()
            db._adapter.reconnect()
            log.info("reconnected db")
            fn(*args)
            db.commit()
        except Exception as _e:
            log.error(_e, exc_info=True)
            log.error(str(l))

    def error_handler(e):
        s = str(e)
        if "server has gone away" in s or "Lost connection" in s or "socket.error" in s:
            db_disconnect_handler()
        else:
            log.error(e, exc_info=True)
            log.error(str(l))

    log = logging.getLogger("web2py.app.%s.task_rq" % app)
    l = None
    while True:
        try:
            l = rconn.blpop(rqueues, timeout=20)
            if l is None:
                continue
            data = json.loads(l[1])
            if isinstance(data, (list, tuple)):
                args = data
                fn = getfn(l[0])
            elif isinstance(data, dict) and getfn is None:
                args = data["args"]
                fn = globals()[data["fn"]]
                authdump = data.get("authdump")
                if authdump:
                    global auth
                    auth = Storage(authdump)
                    auth.user = Storage(auth.user)
                else:
                    auth = Storage()
                    auth.user = Storage()
            else:
                log.error("invalid entry: %s", str(data))
                continue
            fn(*args)
            db.commit()
        except KeyboardInterrupt:
            log.info("keyboard interrupt")
            break
        except socket.error:
            db_disconnect_handler()
        except Exception as exc:
            error_handler(exc)

