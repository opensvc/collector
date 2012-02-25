from gluon.contrib.comet_messaging import comet_send

comet_url = "https://dbopensvc:8889"
comet_key = "magix123"

def _comet_send(msg, group="generic"):
    try:
        comet_send(comet_url, msg, comet_key, group)
    except:
        pass
