import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'household_services_platform.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    username = 'homeadmin'
    email = 'admin@homecare.com'
    password = 'Admin@1234'

    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print("Admin already exists!")
    else:
        # Create new superuser
        admin_user = User.objects.create_superuser(username=username, email=email, password=password)
        
        # Set the custom role to ADMIN if the field exists
        if hasattr(admin_user, 'role'):
            admin_user.role = 'ADMIN'
            admin_user.save()
            
        print("Admin created successfully!")

if __name__ == '__main__':
    create_admin()
