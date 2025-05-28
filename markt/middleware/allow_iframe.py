class AllowIframeForMediaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/media/') and request.path.endswith('.pdf'):
            response['X-Frame-Options'] = 'ALLOWALL'  # o 'SAMEORIGIN' si tu front y back comparten dominio
        return response
