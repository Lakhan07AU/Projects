"""Database seed: demo users, wards, roads, repair teams, cost rates and
100+ synthetic potholes. Only fake data is used - no real personal info."""
from __future__ import annotations

import math
import random
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.enums import PotholeStatus, Priority, Role, Severity
from app.core.security import hash_password
from app.db.database import SessionLocal, init_db
from app.db.models import (
    CostRate,
    Pothole,
    Repair,
    RepairTeam,
    RoadSegment,
    Ward,
    User,
)
from app.services.cost_estimator import calculate_repair_area, estimate_cost
from app.services.seed_data import SEED_COST_RATES

settings = get_settings()

DEMO_USERS = [
    {"name": "Aarav Citizen", "email": "citizen@roadguard.demo", "phone": "9000000001",
     "password": "demo1234", "role": Role.CITIZEN},
    {"name": "Priya Official", "email": "official@roadguard.demo", "phone": "9000000002",
     "password": "demo1234", "role": Role.GOVERNMENT_OFFICIAL},
    {"name": "Admin", "email": "admin@roadguard.demo", "phone": "9000000003",
     "password": "demo1234", "role": Role.ADMIN},
    {"name": "Team Alpha", "email": "team@roadguard.demo", "phone": "9000000004",
     "password": "demo1234", "role": Role.REPAIR_TEAM},
]

WARDS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
ROADS = [
    ("MG Road", "NH-48", "NH"), ("Station Road", "SH-4", "SH"), ("Old Bazaar Road", "MDR-12", "MDR"),
    ("Lake View Road", "MDR-15", "MDR"), ("Temple Street", "MDR-17", "MDR"), ("College Road", "SH-8", "SH"),
    ("Ring Road", "NH-44", "NH"), ("Market Street", "MDR-21", "MDR"), ("Park Avenue", "MDR-24", "MDR"),
    ("Railway Road", "SH-9", "SH"), ("Gandhi Chowk Road", "MDR-28", "MDR"), ("Airport Road", "NH-58", "NH"),
]

TEAMS = [
    {"name": "Team Alpha", "contact": "9800000001", "manager_name": "Rakesh Kumar", "city": "Cityville", "ward": "1-5"},
    {"name": "Team Beta", "contact": "9800000002", "manager_name": "Sunita Devi", "city": "Cityville", "ward": "6-10"},
    {"name": "Team Gamma", "contact": "9800000003", "manager_name": "Imran Shaikh", "city": "Cityville", "ward": "11-20"},
]

CENTER_LAT, CENTER_LON = 28.6139, 77.2090  # demo city centre


def seed(db: Session, potholes: int = 120) -> None:
    init_db()

    # Users
    for u in DEMO_USERS:
        if not db.query(User).filter(User.email == u["email"]).first():
            db.add(User(
                name=u["name"], email=u["email"], phone=u["phone"],
                hashed_password=hash_password(u["password"]), role=u["role"],
            ))

    # Wards
    ward_objs = {}
    for w in WARDS:
        ward = db.query(Ward).filter(Ward.name == w).first()
        if not ward:
            ward = Ward(name=w, city="Cityville", district="Demo District", state="Demo State")
            db.add(ward)
        ward_objs[w] = ward

    # Road segments
    road_objs = {}
    for name, number, rclass in ROADS:
        seg = db.query(RoadSegment).filter(RoadSegment.name == name).first()
        if not seg:
            seg = RoadSegment(name=name, road_number=number, road_class=rclass,
                              ward_id=ward_objs[random.choice(WARDS)].id, length_km=round(random.uniform(1.2, 6.0), 2))
            db.add(seg)
        road_objs[name] = seg

    # Repair teams
    team_objs = {}
    for t in TEAMS:
        team = db.query(RepairTeam).filter(RepairTeam.name == t["name"]).first()
        if not team:
            team = RepairTeam(**t)
            db.add(team)
        team_objs[team.name] = team

    # Cost rates
    for cr in SEED_COST_RATES:
        if not db.query(CostRate).filter(CostRate.rate_key == cr["rate_key"]).first():
            db.add(CostRate(
                rate_key=cr["rate_key"], name=cr["name"], unit=cr["unit"], value=cr["value"],
                description=cr["description"], effective_date=datetime.utcnow(),
            ))
    db.flush()

    # Potholes
    rng = random.Random(42)
    existing_count = db.execute(select(func.count()).select_from(Pothole)).scalar_one()
    statuses = [
        PotholeStatus.SUBMITTED, PotholeStatus.PENDING_VERIFICATION, PotholeStatus.VERIFIED,
        PotholeStatus.PRIORITIZED, PotholeStatus.ASSIGNED, PotholeStatus.IN_PROGRESS,
        PotholeStatus.COMPLETED, PotholeStatus.CLOSED, PotholeStatus.CITIZEN_VERIFICATION,
    ]
    created = 0
    for i in range(potholes):
        code = f"PTH-{existing_count + i + 1:06d}"
        if db.query(Pothole).filter(Pothole.pothole_code == code).first():
            continue
        ward = rng.choice(WARDS)
        road_name, road_num, rclass = rng.choice(ROADS)
        lat = CENTER_LAT + rng.uniform(-0.05, 0.05)
        lon = CENTER_LON + rng.uniform(-0.05, 0.05)
        area = round(rng.uniform(0.4, 12.0), 2)
        severity_roll = rng.random()
        severity = (
            Severity.CRITICAL if severity_roll > 0.85 else
            Severity.HIGH if severity_roll > 0.6 else
            Severity.MEDIUM if severity_roll > 0.3 else Severity.LOW
        )
        status = rng.choice(statuses)
        repair_area = calculate_repair_area(area, db)
        cost = estimate_cost(repair_area, db)["total"]
        report_count = rng.randint(1, 48)
        created_at = datetime.utcnow() - timedelta(days=rng.randint(0, 120))

        p = Pothole(
            pothole_code=code, latitude=lat, longitude=lon,
            geometry=f"POINT({lon} {lat})",
            city="Cityville", district="Demo District", state="Demo State",
            ward=ward, road=road_name, ward_id=ward_objs[ward].id, road_id=road_objs[road_name].id,
            severity=severity,
            severity_score=rng.uniform(10, 95),
            confidence=round(rng.uniform(0.6, 0.98), 3),
            estimated_area=area, repair_area=repair_area, estimated_cost=cost,
            priority=rng.choice(list(Priority)),
            priority_score=rng.uniform(20, 95),
            status=status, report_count=report_count, source="SEED",
            created_at=created_at, updated_at=created_at,
        )
        if status in (PotholeStatus.CLOSED, PotholeStatus.COMPLETED, PotholeStatus.CITIZEN_VERIFICATION):
            p.actual_cost = cost * rng.uniform(0.9, 1.2)
            p.after_image = ""
        db.add(p)
        db.flush()
        created += 1

        if status in (PotholeStatus.ASSIGNED, PotholeStatus.IN_PROGRESS,
                      PotholeStatus.COMPLETED, PotholeStatus.CLOSED,
                      PotholeStatus.CITIZEN_VERIFICATION):
            team = rng.choice(list(team_objs.values()))
            assigned_at = created_at + timedelta(days=2)
            completion = assigned_at + timedelta(days=rng.randint(3, 21)) if status not in (
                PotholeStatus.ASSIGNED, PotholeStatus.IN_PROGRESS) else None
            repair = Repair(
                pothole_id=p.id, team_id=team.id,
                estimated_cost=cost,
                actual_cost=p.actual_cost,
                repair_area=repair_area,
                status="CLOSED" if status == PotholeStatus.CLOSED else
                       ("COMPLETED" if completion else "IN_PROGRESS" if status == PotholeStatus.IN_PROGRESS else "ASSIGNED"),
                assigned_at=assigned_at, start_date=assigned_at + timedelta(days=1),
                completion_date=completion,
                deadline=assigned_at + timedelta(days=14),
            )
            db.add(repair)
    db.commit()
    print(f"Seed complete. Potholes created: {created}. Total: "
          f"{db.execute(select(func.count()).select_from(Pothole)).scalar_one()}")
    print("Demo logins (password: demo1234):")
    for u in DEMO_USERS:
        print(f"  {u['role'].value:<20} {u['email']}")


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
