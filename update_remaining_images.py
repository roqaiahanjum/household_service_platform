import os
from django.core.files import File
from services.models import Service

def main():
    updates = [
        {
            'name': 'Kitchen Deep Clean',
            'image_path': r'C:\Users\amani\.gemini\antigravity\brain\0b0fea9a-8986-4b88-8cc9-8e4e33e451b8\kitchen_deep_clean_1778927002517.png',
            'filename': 'kitchen_deep_clean.png'
        },
        {
            'name': 'Party Catering',
            'image_path': r'C:\Users\amani\.gemini\antigravity\brain\0b0fea9a-8986-4b88-8cc9-8e4e33e451b8\party_catering_1778927018125.png',
            'filename': 'party_catering.png'
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
    main()
