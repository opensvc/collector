def enqueue_async_task(fn, args=[], kwargs={}):
    rconn.rpush("osvc:q:async", json.dumps({
        "fn": fn,
        "args": args,
        "kwargs": kwargs,
        "auth": auth_dump(),
    }))

def task_rq(rqueues, getfn, app="feed"):
    import time
    import socket

    log = logging.getLogger("web2py.app.%s.task_rq" % app)
    db.executesql("set wait_timeout=1200")

    def reconnect():
        try:
            db.executesql("select 1")
        except Exception as exc:
            db._adapter.close()
            db._adapter.reconnect()
            db.executesql("select 1")
            log.info("db reconnected")

    l = None
    while True:
        try:
            reconnect()
        except KeyboardInterrupt:
            log.info("keyboard interrupt")
            break
        except Exception as exc:
            log.warning("db is not usable: %s", exc)
            time.sleep(1)
        try:
            l = rconn.blpop(rqueues, timeout=20)
            if l is None:
                continue
            data = json.loads(l[1])
            if isinstance(data, (list, tuple)):
                args = data
                kwargs = {}
                fn = getfn(l[0])
            elif isinstance(data, dict) and getfn is None:
                args = data.get("args", [])
                kwargs = data.get("kwargs", {})
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
            fn(*args, **kwargs)
            db.commit()
        except KeyboardInterrupt:
            log.info("keyboard interrupt")
            break
        except socket.error as exc:
            log.error("%s", exc)
            time.sleep(1)
        except Exception as exc:
            log.error(exc, exc_info=True)
            log.error(str(exc))

