from apps.clients.models import DomainModel


def get_client_login_url(tenant, protocol):
    domain = DomainModel.objects.get(tenant=tenant).domain
    if "localhost" in domain:
        if len(domain.split(".")) <= 1:
            login_url = f"{protocol}://{domain}:3000/auth/user-login"
        else:
            login_url = f"{protocol}://{domain}:3000/auth/user-login"
    else:
        if len(domain.split(".")) <= 1:
            login_url = f"{protocol}://{domain}/auth/user-login"
        else:
            login_url = f"{protocol}://{domain}/auth/user-login"
    return login_url
