from django.shortcuts import HttpResponse
import json

def jResponse(dictResponse):
    return HttpResponse(json.dumps(dictResponse),content_type='application/json')


def jsonForbiddenError(request):
    return jResponse({
        'error' :{
            'code' :403,
            'message' :'Forbidden',
            'reason': 'This ressource is forbiden.'
        }
    })

def jsonUnauthorizedError(request):
    return jResponse({
        'error': {
            'code': 401,
            'message': 'Unauthorized',
            'reason': 'This ressource needs an authentification.'
        }
    })

def jsonUnknownError(request):
    return jResponse({
        'error': {
            'code': 500,
            'message': 'Internal Server Error',
            'reason': 'An unknown error has occured while proceeding the request. Please contact the administrator.'
        }
    })

def jsonBadRequest(request, reason):
    return jResponse({
        'error': {
            'code': 400,
            'message': 'Bad Request',
            'reason': reason
        }
    })


def jsonDone(request):
    return jResponse({
        'message': {
            'code': 200,
            'message': 'Completed',
        }
    })


def jsonNotImplementedError(request):
    return jResponse({
        'message': {
            'code': 501,
            'message': 'Not Implemented',
            'reason':   'Ressource not implemented yet.'
        }
    })


def jsonNotFound(request):
    return jResponse({
        'message': {
            'code': 404,
            'message': 'Not Found',
            'reason': 'Ressource cannot be found.'
        }
    })