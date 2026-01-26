import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    try:
        # Use create_superuser if it exists on custom manager, else manual
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='admin')
        print("Superuser 'admin' created with password 'admin123'")
    except Exception as e:
        print(f"Error creating superuser: {e}")
else:
    print("Superuser 'admin' already exists")
