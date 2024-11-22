from datapunt_api.serializers import LinksField

class HTTPSLinksField(LinksField):
    def get_url(self, obj, view_name, request, format):
        url = super().get_url(obj, view_name, request, format)
        if url.startswith('http://') and not url.startswith('http://localhost'):
            # Only modify external URLs, not internal ones
            url = 'https://' + url[7:]
        return url