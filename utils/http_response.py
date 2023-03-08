import json

from django.http import HttpResponse

from utils.constants import HttpResponseMsg, HttpStatusCode


def send_http_response(data=None, status=HttpStatusCode['SUCCESS'], err_msg=None):
    response = dict(
        status=status,
        response=HttpResponseMsg['SUCCESS'],
        data=data,
        err_msg=err_msg
    )
    print(response)
    if status not in [HttpStatusCode['SUCCESS'], HttpStatusCode['SUCCESS_CREATE']]:
        response['response'] = HttpResponseMsg['FAILED']
    return HttpResponse(json.dumps(response), status=response['status'])
