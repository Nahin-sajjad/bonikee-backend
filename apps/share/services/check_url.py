def check_url(request):
    # Get the host from the request
    host = request.META.get("HTTP_HOST", "")

    # Check if the host contains "localhost:3000" or "dev.bonikee.com"
    if "localhost:3000" in host:
        return "localhost:3000"
    elif "dev.bonikee.com" in host:
        return "dev.bonikee.com"
