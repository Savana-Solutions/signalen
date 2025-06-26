# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2019 - 2021 Gemeente Amsterdam
import copy

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.contrib.gis.gdal import CoordTransform, SpatialReference

from signals.apps.signals.models.mixins import CreatedUpdatedModel
from signals.apps.signals.utils.location import AddressFormatter

STADSDEEL_VIDYADHAR_NAGAR = 'vidyadhar-nagar'
STADSDEEL_JHOTWARA = 'jhotwara'
STADSDEEL_SANGANER = 'sanganer'
STADSDEEL_BAGRU = 'bagru'
STADSDEEL_MALVIYA_NAGAR = 'malviya-nagar'

STADSDELEN = (
    (STADSDEEL_VIDYADHAR_NAGAR, 'Vidyadhar Nagar'),
    (STADSDEEL_JHOTWARA, 'Jhotwara'),
    (STADSDEEL_SANGANER, 'Sanganer'),
    (STADSDEEL_BAGRU, 'Bagru'),
    (STADSDEEL_MALVIYA_NAGAR, 'Malviya Nagar'),
)

AREA_STADSDEEL_TRANSLATION = {
    'vidyadhar-nagar': STADSDEEL_VIDYADHAR_NAGAR,
    'jhotwara': STADSDEEL_JHOTWARA,
    'sanganer': STADSDEEL_SANGANER,
    'bagru': STADSDEEL_BAGRU,
    'malviya-nagar': STADSDEEL_MALVIYA_NAGAR,
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
