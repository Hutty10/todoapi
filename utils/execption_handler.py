from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    # import pdb;pdb.set_trace()
    handlers = {
        'ValidationError': _handle_generic_error,
        'Http404': _handle_generic_error,
        'PermissionDenied': _handle_generic_error,
        'NotFound': _handle_generic_error,
        'NotAuthenticated': _handle_authentication_error,
    }

    if response is not None:
        response.data['status_code'] = response.status_code

    exception_class = exc.__class__.__name__
    # exc_list = str(exc).split('DETAIL: ')
    # return Response({'error': exc_list[-1]})
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    return response

def _handle_authentication_error(exc, context, response):
    response.data = {
        'error': 'please login to proceed',
        'status_code': response.status_code
    }
    return response

def _handle_generic_error(exc, context, response):
    return response