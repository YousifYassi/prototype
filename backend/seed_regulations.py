"""
Seed Regulations Data for Ontario Jurisdiction
Based on Ontario Occupational Health and Safety Act
https://www.ontario.ca/laws/statute/90o01
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, init_db
from backend.database import Jurisdiction, Industry, JurisdictionRegulation, ActionSeverity
import json


def seed_jurisdictions(db):
    """Seed jurisdiction data"""
    print("Seeding jurisdictions...")
    
    jurisdictions = [
        {
            "name": "Ontario",
            "code": "ontario",
            "country": "Canada",
            "regulation_url": "https://www.ontario.ca/laws/statute/90o01",
            "description": "Ontario Occupational Health and Safety Act (OHSA)",
            "is_active": True
        },
        {
            "name": "Generic",
            "code": "generic",
            "country": "Global",
            "regulation_url": None,
            "description": "Generic workplace safety standards applicable globally",
            "is_active": True
        }
    ]
    
    created_jurisdictions = {}
    for j_data in jurisdictions:
        existing = db.query(Jurisdiction).filter(Jurisdiction.code == j_data["code"]).first()
        if not existing:
            jurisdiction = Jurisdiction(**j_data)
            db.add(jurisdiction)
            db.commit()
            db.refresh(jurisdiction)
            created_jurisdictions[j_data["code"]] = jurisdiction
            print(f"  Created jurisdiction: {j_data['name']}")
        else:
            created_jurisdictions[j_data["code"]] = existing
            print(f"  Jurisdiction already exists: {j_data['name']}")
    
    return created_jurisdictions


def seed_industries(db):
    """Seed industry data"""
    print("Seeding industries...")
    
    industries = [
        {
            "name": "Food Safety",
            "code": "food_safety",
            "description": "Food service, food processing, restaurants, and food handling facilities",
            "hazard_categories": json.dumps([
                "biological_contamination",
                "cross_contamination",
                "temperature_control",
                "personal_hygiene",
                "food_handling"
            ]),
            "is_active": True
        },
        {
            "name": "Construction",
            "code": "construction",
            "description": "Construction sites, building, renovation, and demolition work",
            "hazard_categories": json.dumps([
                "fall_protection",
                "struck_by",
                "electrical",
                "caught_between",
                "ppe_requirements"
            ]),
            "is_active": True
        },
        {
            "name": "Light Industry",
            "code": "light_industry",
            "description": "Manufacturing, workshops, automotive repair, mechanical work",
            "hazard_categories": json.dumps([
                "machinery_hazards",
                "manual_handling",
                "ppe_requirements",
                "workshop_safety",
                "equipment_operation"
            ]),
            "is_active": True
        },
        {
            "name": "General",
            "code": "general",
            "description": "General workplace safety applicable to all industries",
            "hazard_categories": json.dumps([
                "general_safety",
                "workplace_hazards",
                "emergency_preparedness"
            ]),
            "is_active": True
        }
    ]
    
    created_industries = {}
    for i_data in industries:
        existing = db.query(Industry).filter(Industry.code == i_data["code"]).first()
        if not existing:
            industry = Industry(**i_data)
            db.add(industry)
            db.commit()
            db.refresh(industry)
            created_industries[i_data["code"]] = industry
            print(f"  Created industry: {i_data['name']}")
        else:
            created_industries[i_data["code"]] = existing
            print(f"  Industry already exists: {i_data['name']}")
    
    return created_industries


def seed_ontario_regulations(db, jurisdictions, industries):
    """Seed Ontario-specific regulations for each industry"""
    print("Seeding Ontario regulations...")
    
    ontario = jurisdictions["ontario"]
    
    # Food Safety Regulations
    food_safety = industries["food_safety"]
    food_regulations = [
        {
            "jurisdiction_id": ontario.id,
            "industry_id": food_safety.id,
            "regulation_code": "OHSA_25(2)(h)",
            "title": "Personal Protective Equipment in Food Service",
            "description": "Workers handling food must use proper protective equipment including hairnets, gloves, and appropriate clothing",
            "violation_mapping": json.dumps({
                "no_hair_net": "OHSA_25(2)(h) - Failure to wear required head covering",
                "no_gloves": "OHSA_25(2)(h) - Failure to wear required hand protection",
                "improper_uniform": "OHSA_25(2)(h) - Not wearing appropriate clothing"
            })
        },
        {
            "jurisdiction_id": ontario.id,
            "industry_id": food_safety.id,
            "regulation_code": "OHSA_26(1)",
            "title": "Food Handling and Cross-Contamination Prevention",
            "description": "Proper procedures to prevent cross-contamination between raw and cooked foods",
            "violation_mapping": json.dumps({
                "cross_contamination": "OHSA_26(1) - Unsafe food handling practices",
                "improper_temperature_handling": "OHSA_26(1) - Failure to maintain safe temperatures"
            })
        }
    ]
    
    # Construction Regulations
    construction = industries["construction"]
    construction_regulations = [
        {
            "jurisdiction_id": ontario.id,
            "industry_id": construction.id,
            "regulation_code": "OHSA_26.1(1)",
            "title": "Head Protection on Construction Sites",
            "description": "Every worker on a construction site must wear appropriate head protection (hard hat)",
            "violation_mapping": json.dumps({
                "no_hard_hat": "OHSA_26.1(1) - Failure to wear required head protection",
                "improper_hard_hat": "OHSA_26.1(1) - Wearing damaged or improper head protection"
            })
        },
        {
            "jurisdiction_id": ontario.id,
            "industry_id": construction.id,
            "regulation_code": "OHSA_26.1(2)",
            "title": "Fall Protection Equipment",
            "description": "Workers at risk of falling must use proper fall protection equipment including safety harnesses",
            "violation_mapping": json.dumps({
                "no_safety_harness": "OHSA_26.1(2) - Failure to use fall protection equipment",
                "unsafe_scaffolding": "OHSA_26.1(2) - Unsafe elevated work platform"
            })
        },
        {
            "jurisdiction_id": ontario.id,
            "industry_id": construction.id,
            "regulation_code": "OHSA_26.1(3)",
            "title": "High Visibility Clothing",
            "description": "Workers must wear high visibility vests or clothing in traffic areas or where visibility is reduced",
            "violation_mapping": json.dumps({
                "no_high_visibility_vest": "OHSA_26.1(3) - Failure to wear required high visibility clothing"
            })
        }
    ]
    
    # Light Industry Regulations
    light_industry = industries["light_industry"]
    light_industry_regulations = [
        {
            "jurisdiction_id": ontario.id,
            "industry_id": light_industry.id,
            "regulation_code": "OHSA_25(1)(a)",
            "title": "Eye Protection in Workshops",
            "description": "Workers must wear appropriate eye protection when operating machinery or when there is a risk of eye injury",
            "violation_mapping": json.dumps({
                "no_safety_glasses": "OHSA_25(1)(a) - Failure to wear required eye protection",
                "improper_eye_protection": "OHSA_25(1)(a) - Wearing inadequate eye protection"
            })
        },
        {
            "jurisdiction_id": ontario.id,
            "industry_id": light_industry.id,
            "regulation_code": "OHSA_25(1)(c)",
            "title": "Clothing Around Machinery",
            "description": "Workers must not wear loose clothing, jewelry, or have long hair unsecured near moving machinery",
            "violation_mapping": json.dumps({
                "loose_clothing_near_machinery": "OHSA_25(1)(c) - Wearing loose clothing near machinery",
                "unsecured_hair": "OHSA_25(1)(c) - Long hair not secured near machinery",
                "jewelry_near_machinery": "OHSA_25(1)(c) - Wearing jewelry near machinery"
            })
        },
        {
            "jurisdiction_id": ontario.id,
            "industry_id": light_industry.id,
            "regulation_code": "OHSA_25(2)(d)",
            "title": "Manual Handling and Lifting",
            "description": "Proper lifting techniques and mechanical aids must be used to prevent musculoskeletal injuries",
            "violation_mapping": json.dumps({
                "improper_lifting": "OHSA_25(2)(d) - Unsafe manual handling practices",
                "overloading": "OHSA_25(2)(d) - Lifting excessive weight without assistance"
            })
        }
    ]
    
    all_regulations = food_regulations + construction_regulations + light_industry_regulations
    
    for reg_data in all_regulations:
        existing = db.query(JurisdictionRegulation).filter(
            JurisdictionRegulation.jurisdiction_id == reg_data["jurisdiction_id"],
            JurisdictionRegulation.industry_id == reg_data["industry_id"],
            JurisdictionRegulation.regulation_code == reg_data["regulation_code"]
        ).first()
        
        if not existing:
            regulation = JurisdictionRegulation(**reg_data)
            db.add(regulation)
            print(f"  Created regulation: {reg_data['regulation_code']} - {reg_data['title']}")
        else:
            print(f"  Regulation already exists: {reg_data['regulation_code']}")
    
    db.commit()


def seed_action_severities(db, jurisdictions, industries):
    """Seed severity levels for unsafe actions"""
    print("Seeding action severities...")
    
    ontario = jurisdictions["ontario"]
    
    # Food Safety Action Severities
    food_safety = industries["food_safety"]
    food_severities = [
        {"action_name": "no_hair_net", "severity_level": 3, "notification_priority": "high", 
         "description": "Not wearing required hair covering in food preparation area"},
        {"action_name": "no_gloves", "severity_level": 3, "notification_priority": "high",
         "description": "Not wearing gloves when handling ready-to-eat food"},
        {"action_name": "cross_contamination", "severity_level": 5, "notification_priority": "urgent",
         "description": "Risk of cross-contamination between raw and cooked foods"},
        {"action_name": "improper_temperature_handling", "severity_level": 4, "notification_priority": "urgent",
         "description": "Food stored or handled at unsafe temperatures"},
    ]
    
    # Construction Action Severities
    construction = industries["construction"]
    construction_severities = [
        {"action_name": "no_hard_hat", "severity_level": 4, "notification_priority": "urgent",
         "description": "Not wearing required hard hat on construction site"},
        {"action_name": "no_safety_harness", "severity_level": 5, "notification_priority": "urgent",
         "description": "Working at height without fall protection equipment"},
        {"action_name": "unsafe_scaffolding", "severity_level": 5, "notification_priority": "urgent",
         "description": "Using damaged or improperly erected scaffolding"},
        {"action_name": "no_high_visibility_vest", "severity_level": 3, "notification_priority": "high",
         "description": "Not wearing high visibility clothing in traffic or low visibility areas"},
    ]
    
    # Light Industry Action Severities
    light_industry = industries["light_industry"]
    light_industry_severities = [
        {"action_name": "no_safety_glasses", "severity_level": 3, "notification_priority": "high",
         "description": "Not wearing required eye protection near machinery"},
        {"action_name": "loose_clothing_near_machinery", "severity_level": 5, "notification_priority": "urgent",
         "description": "Wearing loose clothing near moving machinery - entanglement risk"},
        {"action_name": "improper_lifting", "severity_level": 2, "notification_priority": "normal",
         "description": "Using incorrect lifting technique or lifting excessive weight"},
    ]
    
    severity_mappings = [
        (food_safety.id, food_severities),
        (construction.id, construction_severities),
        (light_industry.id, light_industry_severities)
    ]
    
    for industry_id, severities in severity_mappings:
        for sev_data in severities:
            existing = db.query(ActionSeverity).filter(
                ActionSeverity.action_name == sev_data["action_name"],
                ActionSeverity.jurisdiction_id == ontario.id,
                ActionSeverity.industry_id == industry_id
            ).first()
            
            if not existing:
                severity = ActionSeverity(
                    action_name=sev_data["action_name"],
                    jurisdiction_id=ontario.id,
                    industry_id=industry_id,
                    severity_level=sev_data["severity_level"],
                    default_severity=True,
                    description=sev_data["description"],
                    notification_priority=sev_data["notification_priority"]
                )
                db.add(severity)
                print(f"  Created severity: {sev_data['action_name']} (Level {sev_data['severity_level']})")
            else:
                print(f"  Severity already exists: {sev_data['action_name']}")
    
    db.commit()


def main():
    """Main seeding function"""
    print("=" * 60)
    print("Seeding Regulations Database")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Seed data
        jurisdictions = seed_jurisdictions(db)
        industries = seed_industries(db)
        seed_ontario_regulations(db, jurisdictions, industries)
        seed_action_severities(db, jurisdictions, industries)
        
        print("\n" + "=" * 60)
        print("Database seeding completed successfully!")
        print("=" * 60)
        
        # Print summary
        print(f"\nJurisdictions: {db.query(Jurisdiction).count()}")
        print(f"Industries: {db.query(Industry).count()}")
        print(f"Regulations: {db.query(JurisdictionRegulation).count()}")
        print(f"Action Severities: {db.query(ActionSeverity).count()}")
        
    except Exception as e:
        print(f"\nError seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

