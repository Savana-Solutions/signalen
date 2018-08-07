import csv
import tempfile
import os
import json

from django.core.files.storage import default_storage

from signals.models import Signal, Location, Reporter, Category, Status


def create_signals_csv(directory):
    """Create CSV file with all `Signal` objects.

    :param directory: Path to dir for saving the CSV filea
    :returns: Path to CSV file
    """
    with open(os.path.join(directory, 'signals.csv'), 'w') as csv_file:
        writer = csv.writer(csv_file)

        # Writing the header to the CSV file.
        writer.writerow([
            'id',
            'signal_uuid',
            'source',
            'text',
            'text_extra',
            'location_id',
            'status_id',
            'category_id',
            'reporter_id',
            'incident_date_start',
            'incident_date_end',
            'created_at',
            'updated_at',
            'operational_date',
            'expire_date',
            'image',
            'upload',
            'extra_properties',
        ])

        # Writing all `Signal` objects to the CSV file.
        for signal in Signal.objects.all():
            writer.writerow([
                signal.pk,
                signal.signal_id,
                signal.source,
                signal.text,
                signal.text_extra,
                signal.location_id,
                signal.status_id,
                signal.category_id,
                signal.reporter_id,
                signal.incident_date_start,
                signal.incident_date_end,
                signal.created_at,
                signal.updated_at,
                signal.operational_date,
                signal.expire_date,
                signal.image,
                signal.upload,
                json.dumps(signal.extra_properties),
            ])

    return csv_file.name


def create_locations_csv(directory):
    """Create CSV file with all `Location` objects.

    :param directory: Path to dir for saving the CSV filea
    :returns: Path to CSV file
    """
    with open(os.path.join(directory, 'locations.csv'), 'w') as csv_file:
        writer = csv.writer(csv_file)

        # Writing the header to the CSV file.
        writer.writerow([
            'id',
            '_signal_id',
            'lat',
            'lng',
            'stadsdeel',
            'buurt_code',
            'address',
            'address_text',
            'created_at',
            'updated_at',
            'extra_properties',
        ])

        # Writing all `Location` objects to the CSV file.
        for location in Location.objects.all():
            writer.writerow([
                location.pk,
                location._signal_id,
                location.geometrie.x,
                location.geometrie.y,
                location.get_stadsdeel_display(),
                location.buurt_code,
                json.dumps(location.address),
                location.address_text,
                location.created_at,
                location.updated_at,
                json.dumps(location.extra_properties),
            ])

    return csv_file.name


def create_reporters_csv(directory):
    """Create CSV file with all `Reporter` objects.

    :param directory: Path to dir for saving the CSV filea
    :returns: Path to CSV file
    """
    with open(os.path.join(directory, 'reporters.csv'), 'w') as csv_file:
        writer = csv.writer(csv_file)

        # Writing the header to the CSV file.
        writer.writerow([
            'id',
            '_signal_id',
            'email',
            'phone',
            'remove_at',
            'created_at',
            'updated_at',
            'extra_properties',
        ])

        # Writing all `Reporter` objects to the CSV file.
        for reporter in Reporter.objects.all():
            writer.writerow([
                reporter.pk,
                reporter._signal_id,
                reporter.email,
                reporter.phone,
                reporter.remove_at,
                reporter.created_at,
                reporter.updated_at,
                json.dumps(reporter.extra_properties),
            ])

    return csv_file.name


def create_categories_csv(directory):
    """Create CSV file with all `Category` objects.

    :param directory: Path to dir for saving the CSV filea
    :returns: Path to CSV file
    """
    with open(os.path.join(directory, 'categories.csv'), 'w') as csv_file:
        writer = csv.writer(csv_file)

        # Writing the header to the CSV file.
        writer.writerow([
            'id',
            '_signal_id',
            'main',
            'sub',
            'department',
            'priority',
            'ml_priority',
            'ml_cat',
            'ml_prob',
            'ml_cat_all',
            'ml_cat_all_prob',
            'ml_sub_cat',
            'ml_sub_prob',
            'ml_sub_all',
            'ml_sub_all_prob',
            'created_at',
            'updated_at',
            'extra_properties',
        ])

        # Writing all `Category` objects to the CSV file.
        for category in Category.objects.all():
            writer.writerow([
                category.pk,
                category._signal_id,
                category.main,
                category.sub,
                category.department,
                category.priority,
                category.ml_priority,
                category.ml_cat,
                category.ml_prob,
                category.ml_cat_all,
                category.ml_cat_all_prob,
                category.ml_sub_cat,
                category.ml_sub_prob,
                category.ml_sub_all,
                category.ml_sub_all_prob,
                category.created_at,
                category.updated_at,
                json.dumps(category.extra_properties),
            ])

    return csv_file.name


def create_statuses_csv(directory):
    """Create CSV file with all `Status` objects.

    :param directory: Path to dir for saving the CSV filea
    :returns: Path to CSV file
    """
    with open(os.path.join(directory, 'statuses.csv'), 'w') as csv_file:
        writer = csv.writer(csv_file)

        # Writing the header to the CSV file.
        writer.writerow([
            'id',
            '_signal_id',
            'text',
            'user',
            'target_api',
            'state',
            'extern',
            'created_at',
            'updated_at',
            'extra_properties',
        ])

        # Writing all `Status` objects to the CSV file.
        for status in Status.objects.all():
            writer.writerow([
                status.pk,
                status._signal_id,
                status.text,
                status.user,
                status.target_api,
                status.get_state_display(),
                status.extern,
                status.created_at,
                status.updated_at,
                json.dumps(status.extra_properties),
            ])

    return csv_file.name


def save_csv_to_object_store(csv_file):
    """Save given CSV file to objectstore.

    :param csv_file:
    :returns:
    """
    # default_storage =
    pass


def handle():
    tmp_dir = tempfile.mkdtemp()
    signals_csv_file = create_signals_csv(tmp_dir)
    save_csv_to_object_store(signals_csv_file)