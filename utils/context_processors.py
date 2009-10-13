import logging


def appname(request):
    parts = request.path.split('/')
    while parts and not parts[0]:
        parts.pop(0)
    if not parts:
        parts.append('welcome')
    logging.debug('appname %s', parts[0])
    return {'appname': parts[0]}
