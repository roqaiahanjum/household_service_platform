import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'household_services_platform.settings')
django.setup()

from core.models import Review

def run():
    Review.objects.all().delete()
    
    reviews = [
        {"customer_name": "Rahul Sharma", "city": "Belagavi", "rating": 5, "text": "Excellent cleaning service. The team was very professional and thorough.", "service_name": "Deep Cleaning"},
        {"customer_name": "Priya Patil", "city": "Belagavi", "rating": 5, "text": "Very reliable cooking service. The cook is punctual and makes delicious local food.", "service_name": "Daily Cooking"},
        {"customer_name": "Amit Desai", "city": "Belagavi", "rating": 4, "text": "Good nursing care for my father. The staff is polite and well-trained.", "service_name": "Elder Care"},
        {"customer_name": "Sneha Joshi", "city": "Belagavi", "rating": 5, "text": "Fantastic deep cleaning! My house looks brand new.", "service_name": "Deep Cleaning"},
        {"customer_name": "Kiran Kulkarni", "city": "Belagavi", "rating": 5, "text": "The baby sitter is wonderful. She handles my toddler with such care.", "service_name": "Child Care"},
        {"customer_name": "Ravi Kumar", "city": "Belagavi", "rating": 4, "text": "Prompt and efficient service. Very satisfied.", "service_name": "Plumbing"},
        {"customer_name": "Anjali Mehta", "city": "Belagavi", "rating": 5, "text": "Great experience overall. Transparent pricing and good quality.", "service_name": "Electrical Help"},
    ]

    for data in reviews:
        Review.objects.create(**data)
    
    print("Added 7 demo reviews successfully.")

if __name__ == '__main__':
    run()
