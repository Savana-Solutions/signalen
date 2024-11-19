# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2020 - 2021 Vereniging van Nederlandse Gemeenten, Gemeente Amsterdam
from glob import glob
from os import path

import logging
import zipfile
import io
import os
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.renderers import BaseRenderer
from rest_framework.viewsets import ViewSet

from signals.apps.api.generics.permissions import SIAPermissions, SIAReportPermissions
from signals.auth.backend import JWTAuthBackend

logger = logging.getLogger(__name__)


class PassthroughRenderer(BaseRenderer):
    """
        Return data as-is. View should supply a Response.
    """
    media_type = ''
    format = ''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class PrivateCsvViewSet(ViewSet):
    """
    Private ViewSet to retrieve generated csv files
    https://stackoverflow.com/a/51936269
    """

    authentication_classes = (JWTAuthBackend, )
    permission_classes = (SIAPermissions & SIAReportPermissions, )

    def list(self, request):
        if not settings.DWH_MEDIA_ROOT:
            raise NotFound(detail='Unconfigured Csv location', code=status.HTTP_404_NOT_FOUND)

        now = timezone.now()
        src_folder = f'{settings.DWH_MEDIA_ROOT}/{now:%Y}/{now:%m}/{now:%d}'

        if not os.path.exists(src_folder):
            raise NotFound(detail='Incorrect Csv folder', code=status.HTTP_404_NOT_FOUND)

        csv_files = [f for f in os.listdir(src_folder) if f.endswith('.csv')]

        if not csv_files:
            raise NotFound(detail='No Csv files in folder', code=status.HTTP_404_NOT_FOUND)

        # Create a ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for csv_filename in csv_files:
                file_path = os.path.join(src_folder, csv_filename)
                zip_file.write(file_path, csv_filename)

        # Prepare the response
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename=csv_files_{now:%Y%m%d}.zip'

        return response

    def _path_leaf(self, file_name):
        head, tail = path.split(file_name)
        return tail or path.basename(head)
