from datapunt_api.serializers import LinksField
from rest_framework.reverse import reverse

class HTTPSLinksField(LinksField):
    def get_url(self, obj, view_name, request, format):
        kwargs = getattr(self, 'kwargs', None)
        if kwargs is None:
            kwargs = {'pk': obj.pk} if hasattr(obj, 'pk') else {}

        url = reverse(view_name, kwargs=kwargs, request=request, format=format)
        
        if url.startswith('http://') and 'localhost' not in url:
            # Convert http to https for all non-localhost URLs
            url = 'https://' + url[7:]
        return url