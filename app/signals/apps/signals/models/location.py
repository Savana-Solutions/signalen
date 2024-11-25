# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2019 - 2021 Gemeente Amsterdam
import copy

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.contrib.gis.gdal import CoordTransform, SpatialReference

from signals.apps.signals.models.mixins import CreatedUpdatedModel
from signals.apps.signals.utils.location import AddressFormatter

STADSDEEL_BERGHEM = 'berghem'
STADSDEEL_CKM = 'ckm'
STADSDEEL_GEFFEN = 'geffen'
STADSDEEL_HERPEN = 'herpen'
STADSDEEL_LITH = 'lith'
STADSDEEL_MHM = 'mhm'
STADSDEEL_NW = 'nw'
STADSDEEL_OIJEN_TEEFFELEN = 'oijen-teeffelen'
STADSDEEL_OSS_ZUID = 'oss-zuid'
STADSDEEL_RAVENSTEIN = 'ravenstein'
STADSDEEL_RUWAARD = 'ruwaard'
STADSDEEL_SCHADEWIJK = 'schadewijk'

STADSDELEN = (
    (STADSDEEL_BERGHEM, 'Berghem'),
    (STADSDEEL_CKM, 'CKM'),
    (STADSDEEL_GEFFEN, 'Geffen'),
    (STADSDEEL_HERPEN, 'Herpen'),
    (STADSDEEL_LITH, 'Lith'),
    (STADSDEEL_MHM, 'MHM'),
    (STADSDEEL_NW, 'NW'),
    (STADSDEEL_OIJEN_TEEFFELEN, 'Oijen-Teeffelen'),
    (STADSDEEL_OSS_ZUID, 'Oss-Zuid'),
    (STADSDEEL_RAVENSTEIN, 'Ravenstein'),
    (STADSDEEL_RUWAARD, 'Ruwaard'),
    (STADSDEEL_SCHADEWIJK, 'Schadewijk'),
)

AREA_STADSDEEL_TRANSLATION = {
    'berghem': STADSDEEL_BERGHEM,
    'ckm': STADSDEEL_CKM,
    'geffen': STADSDEEL_GEFFEN,
    'herpen': STADSDEEL_HERPEN,
    'lith': STADSDEEL_LITH,
    'mhm': STADSDEEL_MHM,
    'nw': STADSDEEL_NW,
    'oijen-teeffelen': STADSDEEL_OIJEN_TEEFFELEN,
    'oss-zuid': STADSDEEL_OSS_ZUID,
    'ravenstein': STADSDEEL_RAVENSTEIN,
    'ruwaard': STADSDEEL_RUWAARD,
    'schadewijk': STADSDEEL_SCHADEWIJK,
}


class Location(CreatedUpdatedModel):
    """All location related information."""

    _signal = models.ForeignKey(
        'signals.Signal', related_name='locations',
        null=False, on_delete=models.CASCADE
    )

    geometrie = models.PointField(name='geometrie')
    stadsdeel = models.CharField(null=True, max_length=20, choices=STADSDELEN)
    area_type_code = models.CharField(null=True, max_length=256)
    area_code = models.CharField(null=True, max_length=256)
    area_name = models.CharField(null=True, max_length=256)  # used for sorting BE-166

    # we do NOT use foreign key, since we update
    # buurten as external data in a seperate process
    buurt_code = models.CharField(null=True, max_length=4)
    address = models.JSONField(null=True)
    address_text = models.CharField(null=True, max_length=256, editable=False)
    created_by = models.EmailField(null=True, blank=True)

    extra_properties = models.JSONField(null=True)
    bag_validated = models.BooleanField(default=False)

    history_log = GenericRelation('history.Log', object_id_field='object_pk')

    @property
    def short_address_text(self):
        # openbare_ruimte huisnummerhuiletter-huisnummer_toevoeging
        return AddressFormatter(address=self.address).format('O hlT') if self.address else ''

    def save(self, *args, **kwargs):
        # Set address_text
        self.address_text = AddressFormatter(address=self.address).format('O hlT p W') if self.address else ''
        super().save(*args, **kwargs)

    def get_rd_coordinates(self):
        to_transform = copy.deepcopy(self.geometrie)
        to_transform.transform(
            CoordTransform(
                SpatialReference(4326),  # WGS84
                SpatialReference(28992)  # RD
            )
        )
        return to_transform

    def get_description(self) -> str:
        """
        Description is used for logging a description of a location in the history log.
        """
        if self.stadsdeel:
            description = f'Stadsdeel: {self.get_stadsdeel_display()}'
        else:
            description = ''

        if self.address:
            address_formatter = AddressFormatter(address=self.address)
            description = f'{description}\n' \
                          f'{address_formatter.format("O hlT")}\n' \
                          f'{address_formatter.format("W")}'
        else:
            description = f'{description}Locatie is gepind op de kaart\n' \
                          f'{self.geometrie[0]}, {self.geometrie[1]}'

        return description
