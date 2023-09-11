class RequestService:

    def set_info(self, request, app_name, username):
        setattr(request, "username", username)
        setattr(request, "application", app_name)

    def get_info(self, request):
        if hasattr(request, "username") and hasattr(request, "application"):
            return getattr(request, "application"), getattr(request, "username")
        else:
            return None, None
