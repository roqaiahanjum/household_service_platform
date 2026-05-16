import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'household_services_platform.settings')
django.setup()

from services.models import Service, Category

def update_prices():
    prices = {
        "Cleaning": 99.00,
        "Dishwashing": 79.00,
        "Kitchen Cleaning": 149.00,
        "Bathroom Cleaning": 99.00,
        "Laundry": 129.00,
        "Fan Cleaning": 49.00
    }
    
    # Ensure a category exists for these
    cat, _ = Category.objects.get_or_create(name="Cleaning")
    
    for name, price in prices.items():
        # Using get_or_create to ensure the services exist with the correct prices
        service, created = Service.objects.get_or_create(
            name=name,
            defaults={
                'category': cat,
                'description': f"Professional {name.lower()} service.",
                'price_per_unit': price,
                'unit_name': 'hour'
            }
        )
        if not created:
            service.price_per_unit = price
            service.save()
            print(f"Updated '{service.name}' to {price}")
        else:
            print(f"Created '{service.name}' with price {price}")
            
if __name__ == "__main__":
    update_prices()
