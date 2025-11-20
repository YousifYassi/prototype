"""
Database Migration Script for Jurisdiction and Industry Features
Adds new tables and migrates existing data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database import (
    SessionLocal, init_db, 
    User, Project, Jurisdiction, Industry, VideoProcessing
)
import json


def run_migration():
    """Run the database migration"""
    print("=" * 60)
    print("DATABASE MIGRATION: Jurisdiction and Industry Support")
    print("=" * 60)
    
    # Initialize database with new schema
    print("\nStep 1: Creating new tables...")
    init_db()
    print("[OK] Tables created/verified")
    
    db = SessionLocal()
    
    try:
        # Step 2: Check if generic jurisdiction and industry exist
        print("\nStep 2: Checking for generic jurisdiction and industry...")
        generic_jurisdiction = db.query(Jurisdiction).filter(
            Jurisdiction.code == "generic"
        ).first()
        
        generic_industry = db.query(Industry).filter(
            Industry.code == "general"
        ).first()
        
        if not generic_jurisdiction:
            print("   Creating generic jurisdiction...")
            generic_jurisdiction = Jurisdiction(
                name="Generic",
                code="generic",
                country="Global",
                regulation_url=None,
                description="Generic workplace safety standards applicable globally",
                is_active=True
            )
            db.add(generic_jurisdiction)
            db.commit()
            db.refresh(generic_jurisdiction)
            print("   [OK] Generic jurisdiction created")
        else:
            print("   [OK] Generic jurisdiction already exists")
        
        if not generic_industry:
            print("   Creating general industry...")
            generic_industry = Industry(
                name="General",
                code="general",
                description="General workplace safety applicable to all industries",
                hazard_categories=json.dumps([
                    "general_safety",
                    "workplace_hazards",
                    "emergency_preparedness"
                ]),
                is_active=True
            )
            db.add(generic_industry)
            db.commit()
            db.refresh(generic_industry)
            print("   [OK] General industry created")
        else:
            print("   [OK] General industry already exists")
        
        # Step 3: Migrate existing users to have a default project
        print("\nStep 3: Migrating existing users...")
        users = db.query(User).all()
        migrated_count = 0
        
        for user in users:
            # Check if user already has a project
            existing_project = db.query(Project).filter(
                Project.user_id == user.id
            ).first()
            
            if not existing_project:
                # Create default project for user
                default_project = Project(
                    user_id=user.id,
                    name="Default Project",
                    jurisdiction_id=generic_jurisdiction.id,
                    industry_id=generic_industry.id,
                    min_severity_alert=1
                )
                db.add(default_project)
                db.commit()
                db.refresh(default_project)
                migrated_count += 1
                print(f"   [OK] Created default project for user {user.email}")
        
        print(f"\n[OK] Created default projects for {migrated_count} users")
        
        # Step 4: Summary
        print("\n" + "=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Jurisdictions: {db.query(Jurisdiction).count()}")
        print(f"Industries: {db.query(Industry).count()}")
        print(f"Projects: {db.query(Project).count()}")
        print(f"Users: {db.query(User).count()}")
        print(f"Videos: {db.query(VideoProcessing).count()}")
        print(f"Videos with projects: {db.query(VideoProcessing).filter(VideoProcessing.project_id != None).count()}")
        print("=" * 60)
        print("[OK] Migration completed successfully!")
        print("\nNext steps:")
        print("1. Run: python backend/seed_regulations.py")
        print("2. Restart the backend server")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()

