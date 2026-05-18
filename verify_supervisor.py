#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from supervisor.models.supervisor import Supervisor
from django.contrib.auth.hashers import check_password

# Check if visor1 exists
try:
    supervisor = Supervisor.objects.get(username='visor1')
    print(f"✓ Supervisor found: {supervisor}")
    print(f"  - Email: {supervisor.email}")
    print(f"  - Username: {supervisor.username}")
    print(f"  - Password (hashed): {supervisor.password[:50]}...")
    print(f"  - Django User linked: {supervisor.user}")
    
    if supervisor.user:
        print(f"  - Django User ID: {supervisor.user.id}")
        print(f"  - Django User active: {supervisor.user.is_active}")
    else:
        print("  ✗ WARNING: No Django User linked!")
        
except Supervisor.DoesNotExist:
    print("✗ Supervisor 'visor1' not found in database")
    print("\nAvailable supervisors:")
    for s in Supervisor.objects.all():
        print(f"  - {s.username} ({s.email})")
except Exception as e:
    print(f"✗ Error: {e}")
