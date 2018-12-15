import json, falcon


class CorsMiddleware(object):
    """Implements (partially) the Cross Origin Resource Sharing specification
    Link: http://www.w3.org/TR/cors/
    """

    __author__ = "Luis Benitez"
    __license__ = "MIT"

    ALLOWED_ORIGINS = ['*']

    def process_resource(self, req, resp, resource, stuff):
        origin = req.get_header('Origin')
        if origin:
            # If there is no Origin header, then it is not a valid CORS request
            acrm = req.get_header('Access-Control-Request-Method')
            acrh = req.get_header('Access-Control-Request-Headers')
            if req.method == 'OPTIONS' and acrm and acrh:
                # Method is OPTIONS & ACRM & ACRH Headers => This is a preflight request
                # TODO Validate ACRM & ACRH

                # Set ACAH to echo ACRH
                resp.set_header('Access-Control-Allow-Headers', acrh)

                # Optionally set ACMA
                # resp.set_header('Access-Control-Max-Age', '60')

                # Find implemented methods
                allowed_methods = []
                for method in falcon.HTTP_METHODS:
                    allowed_method = getattr(resource, 'on_' + method.lower(), None)
                    if allowed_method:
                        allowed_methods.append(method)
                # Fill ACAM
                resp.set_header('Access-Control-Allow-Methods', ','.join(sorted(allowed_methods)))

    def process_response(self, req, resp, resource):
        origin = req.get_header('Origin')
        if origin:
            # If there is no Origin header, then it is not a valid CORS request
            if '*' in self.ALLOWED_ORIGINS:
                resp.set_header('Access-Control-Allow-Origin', '*')
            elif origin in self.ALLOWED_ORIGINS:
                resp.set_header('Access-Control-Allow-Origin', origin)


class RequireJSON(object):
  def process_request(self, req, resp):
    if not req.client_accepts_json:
      raise falcon.HTTPNotAcceptable('This API only supports responses encoded as JSON.', href='http://docs.examples.com/api/json')
    if req.method in ('POST', 'PUT', 'PATCH'):
      if 'application/json' not in req.content_type:
        raise falcon.HTTPUnsupportedMediaType('This API only supports requests encoded as JSON.', href='http://docs.examples.com/api/json')


class JSONTranslator(object):
  def process_request(self, req, resp):
    if req.content_length in (None, 0):
      return
    body = req.stream.read()
    if not body:
      raise falcon.HTTPBadRequest('Empty request body', 'A valid JSON document is required.')
    try:
      req.context['data'] = json.loads(body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
      raise falcon.HTTPError(falcon.HTTP_753, 'Malformed JSON', 'Could not decode the request body. The JSON was incorrect or not encoded as UTF-8.')
  def process_response(self, req, resp, resource):
    if 'result' not in req.context:
      return
    resp.body = json.dumps(req.context['result'])

