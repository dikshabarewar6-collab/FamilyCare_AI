"""
Seed data generator and database reset utility for FamilyCare AI demo experience.
Creates a realistic multi-city family: Eleanor Vance (Chicago), Sarah (NYC), David (Seattle).
"""
from datetime import datetime, date, timedelta, time
try:
    from .connection import get_db, Base, ENGINE
    from .models import (
        Family, FamilyMember, CheckInRecord, MedicationReminder, MedicationLog,
        Appointment, CareTask, Notification
    )
except (ImportError, ValueError):
    from database.connection import get_db, Base, ENGINE
    from database.models import (
        Family, FamilyMember, CheckInRecord, MedicationReminder, MedicationLog,
        Appointment, CareTask, Notification
    )

def reset_database():
    """Drop and recreate all tables to start completely fresh."""
    Base.metadata.drop_all(bind=ENGINE)
    Base.metadata.create_all(bind=ENGINE)

def seed_hackathon_demo_data():
    """Populate database with rich, realistic multi-city family care records."""
    reset_database()
    today = date.today()
    now = datetime.now()

    with get_db() as db:
        # 1. Family Unit
        family = Family(
            id=1,
            name="Vance Family Coordination",
            primary_city="Chicago, IL",
            notes="Cross-city elderly care coordination for Eleanor Vance across Chicago, New York, and Seattle."
        )
        db.add(family)
        db.flush()

        # 2. Family Members
        # Grandma Eleanor (Chicago)
        eleanor = FamilyMember(
            id=1,
            family_id=family.id,
            full_name="Eleanor Vance",
            relationship_type="Elderly Parent",
            city="Chicago",
            state="IL",
            phone="+1 (312) 555-0143",
            email="eleanor.vance@example.com",
            is_elderly=True,
            age=78,
            morning_checkin_time="09:00",
            grace_period_minutes=60,
            preferred_hospital="Northwestern Memorial Hospital",
            emergency_contact_name="Sarah Vance",
            emergency_contact_phone="+1 (212) 555-0199",
            care_notes="Mild hypertension, mobility walker for long distances, loves morning garden walks."
        )
        db.add(eleanor)
        db.flush()

        # Daughter Sarah (New York) - Primary Medical Caregiver
        sarah = FamilyMember(
            id=2,
            family_id=family.id,
            full_name="Sarah Vance",
            relationship_type="Primary Caregiver",
            city="New York",
            state="NY",
            phone="+1 (212) 555-0199",
            email="sarah.vance@example.com",
            is_elderly=False,
            age=46,
            care_notes="Manages doctor appointments, specialist calls, and prescription oversight."
        )
        db.add(sarah)

        # Son David (Seattle) - Logistics & Prescriptions
        david = FamilyMember(
            id=3,
            family_id=family.id,
            full_name="David Vance",
            relationship_type="Son",
            city="Seattle",
            state="WA",
            phone="+1 (206) 555-0182",
            email="david.vance@example.com",
            is_elderly=False,
            age=42,
            care_notes="Coordinates monthly grocery deliveries, pharmacy mail orders, and smart home sensors."
        )
        db.add(david)

        # Visiting Nurse Maria (Chicago)
        maria = FamilyMember(
            id=4,
            family_id=family.id,
            full_name="Maria Santos, RN",
            relationship_type="Professional Nurse",
            city="Chicago",
            state="IL",
            phone="+1 (312) 555-0177",
            email="maria.santos@carenetwork.org",
            is_elderly=False,
            age=50,
            care_notes="Bi-weekly wellness check visits, vitals review, physical therapy accompaniment."
        )
        db.add(maria)
        db.flush()

        # Link Eleanor's assigned caregiver to Sarah
        eleanor.assigned_caregiver_id = sarah.id
        db.flush()

        # 3. Check-In Records (Past 30 days)
        moods = ["Good & Peaceful 😊", "Energetic & Ready 🏃", "Good & Peaceful 😊", "Resting Today 🍵", "Good & Peaceful 😊"]
        for i in range(30, 0, -1):
            past_date = today - timedelta(days=i)
            # Create a realistic distribution: mostly checked-in, 1 missed on day 12, 1 late
            if i == 12:
                status = "Missed Check-In"
                actual_time = None
                mood = None
                notes = "Missed check-in window. Sarah followed up via phone; Eleanor was in church."
            elif i == 5:
                status = "Checked In"
                actual_time = datetime.combine(past_date, time(10, 20))  # within grace
                mood = "A Bit Tired 😴"
                notes = "Slept in late due to rain."
            else:
                status = "Checked In"
                base_time = datetime.combine(past_date, time(8, 40))
                actual_time = base_time + timedelta(minutes=(i * 3) % 40)
                mood = moods[i % len(moods)]
                notes = "Woke up well, made chamomile tea."

            rec = CheckInRecord(
                member_id=eleanor.id,
                checkin_date=past_date,
                scheduled_time="09:00",
                actual_checkin_time=actual_time,
                status=status,
                mood=mood,
                notes=notes,
                is_simulated=True
            )
            db.add(rec)

        # Today's check-in (Awaiting check-in for judge to test!)
        today_rec = CheckInRecord(
            member_id=eleanor.id,
            checkin_date=today,
            scheduled_time="09:00",
            status="Awaiting Check-In",
            notes="Morning window active.",
            is_simulated=False
        )
        db.add(today_rec)

        # 4. Medication Reminders
        m1 = MedicationReminder(
            member_id=eleanor.id,
            medication_name="Lisinopril",
            dosage_label="10mg Tablet",
            schedule_time="08:00",
            frequency="Daily",
            instructions="Take with breakfast and a full glass of water for blood pressure regulation.",
            is_active=True
        )
        m2 = MedicationReminder(
            member_id=eleanor.id,
            medication_name="Metformin",
            dosage_label="500mg Extended Release",
            schedule_time="12:30",
            frequency="Daily",
            instructions="Take during lunch to maintain glucose balance.",
            is_active=True
        )
        m3 = MedicationReminder(
            member_id=eleanor.id,
            medication_name="Atorvastatin",
            dosage_label="20mg Tablet",
            schedule_time="20:00",
            frequency="Daily",
            instructions="Take after dinner before bedtime for cholesterol control.",
            is_active=True
        )
        db.add_all([m1, m2, m3])
        db.flush()

        # 5. Medication Logs (Past 14 days)
        for i in range(14, 0, -1):
            past_date = today - timedelta(days=i)
            db.add(MedicationLog(
                reminder_id=m1.id,
                member_id=eleanor.id,
                scheduled_time="08:00",
                log_date=past_date,
                logged_at=datetime.combine(past_date, time(8, 15)),
                status="Taken",
                acknowledgement_note="Acknowledged by Eleanor.",
                is_simulated=True
            ))
            # 1 missed dose on metformin
            status_m2 = "Skipped" if i == 4 else "Taken"
            db.add(MedicationLog(
                reminder_id=m2.id,
                member_id=eleanor.id,
                scheduled_time="12:30",
                log_date=past_date,
                logged_at=datetime.combine(past_date, time(12, 40)) if status_m2 == "Taken" else datetime.combine(past_date, time(14, 0)),
                status=status_m2,
                acknowledgement_note="Felt stomach fullness, skipped with nurse approval." if status_m2 == "Skipped" else "Taken at lunch.",
                is_simulated=True
            ))
            db.add(MedicationLog(
                reminder_id=m3.id,
                member_id=eleanor.id,
                scheduled_time="20:00",
                log_date=past_date,
                logged_at=datetime.combine(past_date, time(20, 10)),
                status="Taken",
                acknowledgement_note="Bedtime routine acknowledged.",
                is_simulated=True
            ))

        # 6. Appointments
        app1 = Appointment(
            member_id=eleanor.id,
            title="Cardiology Routine Follow-Up",
            doctor_name="Dr. Robert Ramirez",
            specialty="Cardiology",
            clinic_name="Northwestern Bluhm Cardiovascular Institute",
            location_address="676 N Saint Clair St, Chicago, IL",
            appointment_datetime=datetime.combine(today + timedelta(days=3), time(10, 30)),
            assigned_caregiver_id=sarah.id,
            transport_notes="Sarah flying in from NYC to accompany Eleanor; cab arranged.",
            notes="Review 3-month blood pressure logs and adjust Lisinopril if necessary."
        )
        app2 = Appointment(
            member_id=eleanor.id,
            title="Comprehensive Eye & Glaucoma Screen",
            doctor_name="Dr. Karen Lee",
            specialty="Ophthalmology",
            clinic_name="Chicago Vision Center",
            location_address="150 E Huron St, Chicago, IL",
            appointment_datetime=datetime.combine(today + timedelta(days=9), time(14, 0)),
            assigned_caregiver_id=maria.id,
            transport_notes="Maria driving Eleanor in clinic van.",
            notes="Annual dilated eye examination."
        )
        app3 = Appointment(
            member_id=eleanor.id,
            title="Physical Therapy & Gait Assessment",
            doctor_name="Dr. Marcus Adams, DPT",
            specialty="Physical Therapy",
            clinic_name="Lakeshore Mobility Rehab",
            location_address="440 N Michigan Ave, Chicago, IL",
            appointment_datetime=datetime.combine(today - timedelta(days=5), time(11, 0)),
            assigned_caregiver_id=maria.id,
            status="Completed",
            transport_notes="Accompanied by Nurse Maria.",
            notes="Mobility score 88/100. Recommended continuing 20-min daily indoor walks."
        )
        db.add_all([app1, app2, app3])

        # 7. Care Tasks
        t1 = CareTask(
            family_id=family.id,
            title="Order Omron Blood Pressure Monitor Replacement Cuff",
            description="Eleanor's current arm cuff is worn out. Order medium/large cuff on Amazon Prime for delivery to Chicago.",
            category="Prescription",
            due_date=today + timedelta(days=1),
            priority="High",
            status="In Progress",
            assigned_member_id=david.id
        )
        t2 = CareTask(
            family_id=family.id,
            title="Restock Organic Oatmeal & Low-Sodium Pantry Staples",
            description="Order Whole Foods delivery to Eleanor's apartment before weekend.",
            category="Groceries",
            due_date=today + timedelta(days=2),
            priority="Medium",
            status="Pending",
            assigned_member_id=sarah.id
        )
        t3 = CareTask(
            family_id=family.id,
            title="Install Non-Slip Bath Grip Handle",
            description="Install bathroom grab bar near walk-in tub for balance assistance.",
            category="Household",
            due_date=today - timedelta(days=2),
            priority="High",
            status="Completed",
            completed_at=datetime.combine(today - timedelta(days=2), time(16, 30)),
            assigned_member_id=maria.id
        )
        t4 = CareTask(
            family_id=family.id,
            title="Verify Medicare Part D Prescription Formulary Coverage",
            description="Check if Atorvastatin tier coverage changes next quarter.",
            category="Administrative",
            due_date=today + timedelta(days=6),
            priority="Low",
            status="Pending",
            assigned_member_id=david.id
        )
        db.add_all([t1, t2, t3, t4])

        # 8. Recent In-App Notifications
        n1 = Notification(
            family_id=family.id,
            member_id=eleanor.id,
            title="☀️ Morning Check-In Window Active",
            message="Eleanor's scheduled check-in window is open (09:00 AM target).",
            category="Check-In",
            priority="Info",
            is_simulated=True,
            created_at=now - timedelta(minutes=45)
        )
        n2 = Notification(
            family_id=family.id,
            member_id=david.id,
            title="Task Assigned: BP Monitor Cuff Replacement",
            message="David Vance assigned to order Omron BP cuff replacement.",
            category="Task",
            priority="Info",
            is_simulated=True,
            created_at=now - timedelta(hours=3)
        )
        n3 = Notification(
            family_id=family.id,
            member_id=sarah.id,
            title="Cardiology Appointment Confirmed",
            message="Dr. Ramirez cardiology consultation scheduled for next week. Sarah assigned companion.",
            category="Appointment",
            priority="Info",
            is_simulated=True,
            created_at=now - timedelta(days=1)
        )
        db.add_all([n1, n2, n3])

    print("Hackathon demo data seeded successfully.")

if __name__ == "__main__":
    seed_hackathon_demo_data()
