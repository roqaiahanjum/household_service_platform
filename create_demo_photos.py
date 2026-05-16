import os
import django
from django.core.files.base import ContentFile
import urllib.request

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'household_services_platform.settings')
django.setup()

from bookings.models import Booking, WorkPhoto
from accounts.models import User

def get_image_content(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return response.read()

def main():
    # Get any completed bookings, or just the first few bookings and set them to completed
    bookings = Booking.objects.all()[:3]
    if not bookings:
        print("No bookings found to attach demo photos to.")
        return

    # Sample images
    before_url = "https://images.unsplash.com/photo-1584622781564-1d987f7333c1?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" # Dirty room
    after_url = "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" # Clean room
    
    print("Downloading sample images...")
    before_content = get_image_content(before_url)
    after_content = get_image_content(after_url)
    
    provider = User.objects.filter(role=User.Role.WORKER).first()
    if not provider:
        print("No provider found. Creating dummy provider...")
        provider = User.objects.create_user(
            username='demoprovider',
            email='provider@demo.com',
            password='password123',
            role=User.Role.WORKER,
            first_name='Demo',
            last_name='Worker'
        )
        from accounts.models import WorkerProfile
        WorkerProfile.objects.create(user=provider, skills='Cleaning')
        
    print("Creating demo photos...")
    for idx, booking in enumerate(bookings):
        booking.status = 'COMPLETED'
        booking.has_photos = True
        booking.photos_approved = True
        booking.worker = provider
        booking.save()
        
        photo, created = WorkPhoto.objects.get_or_create(booking=booking, provider=provider)
        if created or not photo.before_photo:
            photo.before_photo.save(f'demo_before_{idx}.jpg', ContentFile(before_content), save=False)
            photo.after_photo.save(f'demo_after_{idx}.jpg', ContentFile(after_content), save=False)
            photo.caption = f"Deep cleaned and organized the space. Amazing transformation!"
            photo.is_approved = True
            photo.save()
            print(f"Created photo for booking {booking.id}")
        else:
            print(f"Photo already exists for booking {booking.id}")

if __name__ == '__main__':
    main()
