def task_rq(rqueues, getfn, app="feed"):
    import traceback
    log = logging.getLogger("web2py.app.%s.task_rq" % app)
    l = None
    while True:
        try:
            l = rconn.blpop(rqueues)
            args = json.loads(l[1])
            fn = getfn(l[0])
            fn(*args)
            db.commit()
        except KeyboardInterrupt:
            log.info("keyboard interrupt")
            break
        except Exception as e:
            if "server has gone away" in str(e) or "Lost connection" in str(e):
                try:
                    log.info("reconnect db")
                    db._adapter.close()
                    db._adapter.reconnect()
                    fn(*args)
                except Exception as _e:
                    log.error(_e, exc_info=True)
                    log.error(str(l))
            else:
                db.commit()
                log.error(e, exc_info=True)
                log.error(str(l))

