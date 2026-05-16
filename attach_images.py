import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'household_services_platform.settings')
django.setup()

from services.models import Service

def attach_images():
    updates = [
        {
            'name': 'Dishwashing',
            'image_path': r'C:\Users\amani\.gemini\antigravity\brain\8b730c43-0ff8-4ff2-963e-cbd305cb59d5\dishwashing_1778933316205.png',
            'filename': 'dishwashing.png'
        },
        {
            'name': 'Kitchen Cleaning',
            'image_path': r'C:\Users\amani\.gemini\antigravity\brain\8b730c43-0ff8-4ff2-963e-cbd305cb59d5\kitchen_cleaning_1778933334799.png',
            'filename': 'kitchen_cleaning.png'
        },
        {
            'name': 'Bathroom Cleaning',
            'image_path': r'C:\Users\amani\.gemini\antigravity\brain\8b730c43-0ff8-4ff2-963e-cbd305cb59d5\bathroom_cleaning_1778933354310.png',
            'filename': 'bathroom_cleaning.png'
        },
        {
            'name': 'Laundry',
            'image_path': r'C:\Users\amani\.gemini\antigravity\brain\8b730c43-0ff8-4ff2-963e-cbd305cb59d5\laundry_1778933376439.png',
            'filename': 'laundry.png'
        },
        {
            'name': 'Fan Cleaning',
            'image_path': r'C:\Users\amani\.gemini\antigravity\brain\8b730c43-0ff8-4ff2-963e-cbd305cb59d5\fan_cleaning_1778933395998.png',
            'filename': 'fan_cleaning.png'
        }
    ]

    for item in updates:
        try:
            service = Service.objects.get(name=item['name'])
            if os.path.exists(item['image_path']):
                with open(item['image_path'], 'rb') as f:
                    service.image.save(item['filename'], File(f), save=True)
                print(f"Successfully added image for {item['name']}.")
            else:
                print(f"Image not found at path: {item['image_path']}")
        except Service.DoesNotExist:
            print(f"Service {item['name']} not found.")

if __name__ == '__main__':
    attach_images()
