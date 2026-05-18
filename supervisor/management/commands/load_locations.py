from django.core.management.base import BaseCommand
from supervisor.models.localisation import Localisation

class Command(BaseCommand):
    help = 'Load sample locations into the Localisation table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sample',
            action='store_true',
            help='Load sample Tunisia locations'
        )

    def handle(self, *args, **options):
        if options['sample']:
            # Sample Tunisia locations (gouvernorat, delegation, localite)
            sample_locations = [
                {
                    'gouvernorat_libelle': 'Sfax',
                    'delegation_libelle': 'Sfax Ville',
                    'localite_libelle': 'Sfax',
                    'latitude': 34.7406,
                    'longitude': 10.7603
                },
                {
                    'gouvernorat_libelle': 'Sfax',
                    'delegation_libelle': 'Menzel Chaker',
                    'localite_libelle': 'Menzel Chaker',
                    'latitude': 34.5231,
                    'longitude': 10.4542
                },
                {
                    'gouvernorat_libelle': 'Sfax',
                    'delegation_libelle': 'Thala',
                    'localite_libelle': 'Thala',
                    'latitude': 35.4267,
                    'longitude': 8.7131
                },
                {
                    'gouvernorat_libelle': 'Gafsa',
                    'delegation_libelle': 'Gafsa',
                    'localite_libelle': 'Gafsa',
                    'latitude': 34.4269,
                    'longitude': 8.7842
                },
                {
                    'gouvernorat_libelle': 'Tataouine',
                    'delegation_libelle': 'Tataouine',
                    'localite_libelle': 'Tataouine',
                    'latitude': 33.3157,
                    'longitude': 10.4547
                },
            ]
            
            created_count = 0
            for loc_data in sample_locations:
                try:
                    loc, created = Localisation.objects.get_or_create(
                        gouvernorat_libelle=loc_data['gouvernorat_libelle'],
                        delegation_libelle=loc_data['delegation_libelle'],
                        localite_libelle=loc_data['localite_libelle'],
                        defaults={
                            'latitude': loc_data.get('latitude'),
                            'longitude': loc_data.get('longitude'),
                        }
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Created: {loc}')
                        )
                    else:
                        self.stdout.write(f'- Already exists: {loc}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Error: {loc_data["localite_libelle"]} - {e}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Successfully created {created_count} locations')
            )
        else:
            count = Localisation.objects.count()
            self.stdout.write(f'Current locations in database: {count}')
            self.stdout.write('\nUsage: python manage.py load_locations --sample')
