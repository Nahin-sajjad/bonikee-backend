def error_message_response(error_message, response, status):
    response.data = error_message
    response.status_code = status
    return response
