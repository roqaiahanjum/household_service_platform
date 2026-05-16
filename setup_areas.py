import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'household_services_platform.settings')
django.setup()

from core.models import Area

def main():
    areas = [
        "Tilakwadi",
        "Hindwadi",
        "Camp Area",
        "Shahapur",
        "Vadgaon",
        "Angol",
        "Udyambag",
        "Club Road",
        "Khanapur Road",
        "Nehru Nagar"
    ]
    
    for area_name in areas:
        area, created = Area.objects.get_or_create(
            name=area_name,
            defaults={'description': f'Local area in Belagaum: {area_name}'}
        )
        if created:
            print(f"Created Area: {area_name}")
        else:
            print(f"Area already exists: {area_name}")

if __name__ == '__main__':
    main()
