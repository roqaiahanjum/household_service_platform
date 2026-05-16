import os
import django
from django.core.files import File

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'household_services_platform.settings')
django.setup()

from services.models import Category

image_map = {
    'Cleaning': r'C:\Users\amani\.gemini\antigravity\brain\80bcbd9c-0fd3-403e-8fd0-e98ab4cc8c5f\cat_cleaning_1778772160649.png',
    'Cooking': r'C:\Users\amani\.gemini\antigravity\brain\80bcbd9c-0fd3-403e-8fd0-e98ab4cc8c5f\cat_cooking_1778772176334.png',
    'Childcare': r'C:\Users\amani\.gemini\antigravity\brain\80bcbd9c-0fd3-403e-8fd0-e98ab4cc8c5f\cat_childcare_1778772199030.png',
    'Nursing': r'C:\Users\amani\.gemini\antigravity\brain\80bcbd9c-0fd3-403e-8fd0-e98ab4cc8c5f\cat_nursing_1778772221657.png',
}

def update_images():
    for name, path in image_map.items():
        try:
            category = Category.objects.get(name=name)
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    # Save the image to the model
                    filename = os.path.basename(path)
                    category.image.save(filename, File(f), save=True)
                print(f"Successfully updated image for {name}")
            else:
                print(f"Error: Image not found at {path}")
        except Category.DoesNotExist:
            print(f"Warning: Category '{name}' not found in database.")

if __name__ == '__main__':
    update_images()
