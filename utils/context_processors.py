def appname(request):
    parts = request.path.split('/')
    while parts and not parts[0]:
        parts.pop(0)
    if not parts:
        parts.append('welcome')
    return {'appname': parts[0]}
