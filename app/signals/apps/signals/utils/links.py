from datapunt_api.serializers import LinksField
from rest_framework.reverse import reverse

class HTTPSLinksField(LinksField):
    def get_url(self, obj, view_name, request, format):
        kwargs = getattr(self, 'kwargs', None)
        if kwargs is None:
            # If the view name contains 'public' and the object has a uuid, use that
            if 'public' in view_name and hasattr(obj, 'uuid'):
                kwargs = {'uuid': obj.uuid}
            else:
                kwargs = {'pk': obj.pk} if hasattr(obj, 'pk') else {}

        url = reverse(view_name, kwargs=kwargs, request=request, format=format)
        
        if url.startswith('http://') and 'localhost' not in url:
            # Convert http to https for all non-localhost URLs
            url = 'https://' + url[7:]
        return url