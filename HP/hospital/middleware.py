from django.core.cache import cache
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response.setdefault('X-Content-Type-Options', 'nosniff')
        response.setdefault('Referrer-Policy', 'same-origin')
        response.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        response.setdefault('Cross-Origin-Opener-Policy', 'same-origin')
        response.setdefault('X-Frame-Options', 'DENY')
        if not response.get('Content-Security-Policy'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
        return response


class LoginRateLimitMiddleware(MiddlewareMixin):
    """Rate limit simples para /login/ sem depender de pacote externo."""
    LIMIT = 8
    WINDOW = 15 * 60

    def _key(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown')).split(',')[0].strip()
        return f'shine:login:{ip}'

    def process_request(self, request):
        if request.path == '/login/' and request.method == 'POST':
            key = self._key(request)
            if int(cache.get(key, 0)) >= self.LIMIT:
                return HttpResponse('Muitas tentativas de login. Aguarde alguns minutos e tente novamente.', status=429)
        return None

    def process_response(self, request, response):
        if request.path == '/login/' and request.method == 'POST':
            key = self._key(request)
            if response.status_code in {301, 302}:
                cache.delete(key)
            else:
                cache.set(key, int(cache.get(key, 0)) + 1, self.WINDOW)
        return response
