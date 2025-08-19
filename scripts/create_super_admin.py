#!/usr/bin/env python3
"""
Create Super Admin User Script
Run this to create the first super admin user for the system
"""
import sys
import os
import getpass
from datetime import datetime

# Add the parent directory to Python path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import get_db
from backend.db.admin_models import AdminUser, AdminRole
from backend.auth.admin_auth import admin_auth
import uuid


def create_super_admin():
    """Interactive script to create super admin user"""
    
    print("🔐 Lily AI Social Media - Super Admin Creation")
    print("=" * 50)
    print()
    
    # Get database connection
    db = next(get_db())
    
    # Check if any super admin already exists
    existing_super_admin = db.query(AdminUser).filter(AdminUser.is_superuser == True).first()
    if existing_super_admin:
        print(f"⚠️  Super admin already exists: {existing_super_admin.email}")
        choice = input("Do you want to create another super admin? (y/N): ").strip().lower()
        if choice != 'y':
            print("❌ Cancelled super admin creation")
            return
        print()
    
    # Collect admin details
    print("Enter details for the new super admin:")
    print()
    
    while True:
        email = input("📧 Email: ").strip()
        if not email:
            print("❌ Email is required")
            continue
        if "@" not in email:
            print("❌ Please enter a valid email address")
            continue
        
        # Check if admin with this email exists
        existing = db.query(AdminUser).filter(AdminUser.email == email).first()
        if existing:
            print(f"❌ Admin user with email {email} already exists")
            continue
        break
    
    while True:
        username = input("👤 Username: ").strip()
        if not username:
            print("❌ Username is required")
            continue
        if len(username) < 3:
            print("❌ Username must be at least 3 characters")
            continue
        
        # Check if admin with this username exists
        existing = db.query(AdminUser).filter(AdminUser.username == username).first()
        if existing:
            print(f"❌ Admin user with username {username} already exists")
            continue
        break
    
    full_name = input("📝 Full Name (optional): ").strip() or None
    
    # Get password
    while True:
        password = getpass.getpass("🔒 Password: ")
        if not password:
            print("❌ Password is required")
            continue
        if len(password) < 8:
            print("❌ Password must be at least 8 characters")
            continue
        
        confirm_password = getpass.getpass("🔒 Confirm Password: ")
        if password != confirm_password:
            print("❌ Passwords do not match")
            continue
        break
    
    print()
    print("Creating super admin user...")
    
    try:
        # Hash the password
        hashed_password = admin_auth.hash_password(password)
        
        # Create super admin user
        super_admin = AdminUser(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            role=AdminRole.SUPER_ADMIN,
            is_superuser=True,
            is_active=True,
            password_changed_at=datetime.utcnow()
        )
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print()
        print("✅ Super Admin created successfully!")
        print(f"   ID: {super_admin.id}")
        print(f"   Email: {super_admin.email}")
        print(f"   Username: {super_admin.username}")
        print(f"   Role: {super_admin.role.value}")
        print(f"   Created: {super_admin.created_at}")
        print()
        print("🚀 You can now login to the admin panel with these credentials")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Failed to create super admin: {str(e)}")
        return False
    
    finally:
        db.close()
    
    return True


def list_existing_admins():
    """List existing admin users"""
    
    print("📋 Existing Admin Users")
    print("=" * 30)
    
    db = next(get_db())
    
    try:
        admins = db.query(AdminUser).order_by(AdminUser.created_at.desc()).all()
        
        if not admins:
            print("No admin users found")
            return
        
        for admin in admins:
            status = "🟢 Active" if admin.is_active else "🔴 Inactive"
            superuser = " (Super Admin)" if admin.is_superuser else ""
            print(f"• {admin.email} - {admin.role.value}{superuser} {status}")
        
        print(f"\nTotal: {len(admins)} admin users")
        
    except Exception as e:
        print(f"❌ Failed to list admins: {str(e)}")
    
    finally:
        db.close()


def main():
    """Main script function"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_existing_admins()
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage:")
        print("  python create_super_admin.py          # Create new super admin")
        print("  python create_super_admin.py --list   # List existing admins")
        print("  python create_super_admin.py --help   # Show this help")
        return
    
    # Check if database tables exist
    try:
        db = next(get_db())
        db.query(AdminUser).first()
        db.close()
    except Exception as e:
        print("❌ Database not initialized or admin tables missing")
        print("Please run database migrations first:")
        print("  alembic upgrade head")
        return
    
    create_super_admin()


if __name__ == "__main__":
    main()