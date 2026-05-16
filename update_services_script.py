import os
import shutil
from django.core.files import File
from services.models import Category, Service

def main():
    services_data = [
        {
            'name': 'Full Home Cleaning',
            'desc': 'Professional deep cleaning for every room in your house.',
            'price': 1500.00,
            'unit': 'visit',
            'cat_name': 'Cleaning',
            'image_path': r'C:\Users\amani\.gemini\antigravity\brain\0b0fea9a-8986-4b88-8cc9-8e4e33e451b8\cleaning_service_1778926555166.png',
            'filename': 'cleaning.png'
        },
        {
            'name': 'Daily Meal Prep',
            'desc': 'Healthy and delicious home-cooked meals prepared by a personal chef.',
            'price': 2000.00,
            'unit': 'visit',
            'cat_name': 'Cooking',
            'image_path': r'C:\Users\amani\.gemini\antigravity\brain\0b0fea9a-8986-4b88-8cc9-8e4e33e451b8\cooking_service_1778926572358.png',
            'filename': 'cooking.png'
        },
        {
            'name': 'Babysitting',
            'desc': 'Safe, engaging, and compassionate childcare for your little ones.',
            'price': 500.00,
            'unit': 'hour',
            'cat_name': 'Childcare',
            'image_path': r'C:\Users\amani\.gemini\antigravity\brain\0b0fea9a-8986-4b88-8cc9-8e4e33e451b8\child_care_service_1778926587914.png',
            'filename': 'childcare.png'
        },
        {
            'name': 'Elderly Care',
            'desc': 'Compassionate and respectful assistance with daily living for the elderly.',
            'price': 800.00,
            'unit': 'day',
            'cat_name': 'Nursing',
            'image_path': r'C:\Users\amani\.gemini\antigravity\brain\0b0fea9a-8986-4b88-8cc9-8e4e33e451b8\elder_care_service_1778926610047.png',
            'filename': 'eldercare.png'
        },
        {
            'name': 'Post-Surgical Care',
            'desc': 'Professional home nursing and medical assistance in a comfortable setting.',
            'price': 1000.00,
            'unit': 'day',
            'cat_name': 'Nursing',
            'image_path': r'C:\Users\amani\.gemini\antigravity\brain\0b0fea9a-8986-4b88-8cc9-8e4e33e451b8\home_nursing_service_1778926629113.png',
            'filename': 'homenursing.png'
        }
    ]

    for item in services_data:
        # Get or create category
        cat, _ = Category.objects.get_or_create(name=item['cat_name'], defaults={'description': f'{item["cat_name"]} services'})
        
        # Get or create service
        service, created = Service.objects.get_or_create(
            name=item['name'],
            defaults={
                'category': cat,
                'description': item['desc'],
                'price_per_unit': item['price'],
                'unit_name': item['unit']
            }
        )
        
        # Update existing service if needed
        if not created:
            service.category = cat
            service.description = item['desc']
            service.price_per_unit = item['price']
            service.unit_name = item['unit']

        # Add image
        if os.path.exists(item['image_path']):
            with open(item['image_path'], 'rb') as f:
                service.image.save(item['filename'], File(f), save=True)
            print(f"Updated {item['name']} with image.")
        else:
            print(f"Image not found: {item['image_path']}")
        
        service.save()

if __name__ == '__main__':
    main()
