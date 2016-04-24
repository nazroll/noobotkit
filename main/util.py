import flask


###############################################################################
# Request Parameters
###############################################################################
def param(name, cast=None):
    value = None
    if flask.request.json:
        return flask.request.json.get(name, None)

    if value is None:
        value = flask.request.args.get(name, None)
    if value is None and flask.request.form:
        value = flask.request.form.get(name, None)

    if cast and value is not None:
        if cast is bool:
            return value.lower() in ['true', 'yes', 'y', '1', '']
        if cast is list:
            return value.split(',') if len(value) > 0 else []
        return cast(value)
    return value


###############################################################################
# JSON Response Helpers
###############################################################################
def jsonpify(*args, **kwargs):
    if param('callback'):
        content = '%s(%s)' % (
            param('callback'), flask.jsonify(*args, **kwargs).data,
        )
        mimetype = 'application/javascript'
        return flask.current_app.response_class(content, mimetype=mimetype)
    return flask.jsonify(*args, **kwargs)
