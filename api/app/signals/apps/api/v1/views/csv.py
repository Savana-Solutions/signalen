import glob
import os

from django.conf import settings
from django.http import FileResponse
from django.utils import timezone
from rest_framework import renderers, status, viewsets
from rest_framework.exceptions import NotFound

from signals.apps.api.generics.permissions import SIAPermissions, SIAReportPermissions
from signals.auth.backend import JWTAuthBackend


class PassthroughRenderer(renderers.BaseRenderer):
    """
        Return data as-is. View should supply a Response.
    """
    media_type = ''
    format = ''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class PrivateCsvViewSet(viewsets.ViewSet):
    """
    V1 private ViewSet to retrieve generated csv files
    https://stackoverflow.com/a/51936269
    """

    authentication_classes = (JWTAuthBackend, )
    permission_classes = (SIAPermissions & SIAReportPermissions, )

    def list(self, detail=True, renderer_classes=(PassthroughRenderer,)):
        if not settings.DWH_MEDIA_ROOT:
            raise NotFound(detail='Unconfigured Csv location', code=status.HTTP_404_NOT_FOUND)

        now = timezone.now()
        src_folder = f'{settings.DWH_MEDIA_ROOT}/{now:%Y}/{now:%m}/{now:%d}'

        if not os.path.exists(src_folder):
            raise NotFound(detail='Incorrect Csv folder', code=status.HTTP_404_NOT_FOUND)

        list_of_files = glob.glob(f'{src_folder}/*.zip', recursive=True)
        latest_file = None if not list_of_files else max(list_of_files, key=os.path.getctime)

        if not latest_file:
            raise NotFound(detail='No Csv files in folder', code=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            open(latest_file, 'rb'),
            as_attachment=True,
            filename=self._path_leaf(latest_file)
        )

    def _path_leaf(self, path):
        head, tail = os.path.split(path)
        return tail or os.path.basename(head)
