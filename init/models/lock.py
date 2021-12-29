import time
import uuid


def lock_key(name):
    return "osvc:lock:%s" % name


def acquire_lock(name, timeout=10):
    lock_name = lock_key(name)
    lock_id = "%s:%s" % (uuid.uuid4(), time.time())
    while True:
        if rconn.set(lock_name, lock_id, ex=timeout, nx=True):
            return lock_id
        time.sleep(0.1)


def release_lock(name, lock_id):
    lock_name = lock_key(name)
    if rconn.get(lock_name) == lock_id:
        rconn.delete(lock_name)
