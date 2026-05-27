import csv
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from myapp.models import IMURecord

class Command(BaseCommand):
    help = 'Import IMU data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        with open(options['csv_file'], newline='') as f:
            reader = csv.DictReader(f)
            records = []
            for row in reader:
                records.append(IMURecord(
                    timestamp=parse_datetime(row['timestamp']),
                    ax_mg=int(row['ax_mg']),
                    ay_mg=int(row['ay_mg']),
                    az_mg=int(row['az_mg']),
                    gx_dps=int(row['gx_dps']),
                    gy_dps=int(row['gy_dps']),
                    gz_dps=int(row['gz_dps']),
                    activity=row['activity'].strip(),
                ))
            IMURecord.objects.bulk_create(records)
            self.stdout.write(f'Imported {len(records)} records.')