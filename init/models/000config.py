config = local_import('config', reload=True)

def config_get(param, default=None):
    if not hasattr(config, param):
        return default
    return getattr(config, param)
