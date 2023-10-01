import threading

# Create a thread-local storage for the request object
request_local = threading.local()


# Middleware to set the request object in the thread-local storage
class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store the request object in the thread-local storage
        request_local.request = request
        response = self.get_response(request)
        return response

