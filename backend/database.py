"""
database.py — SQLAlchemy database layer for NayePankh AI Hub

Provides:
- Database connection (SQLite via SQLAlchemy)
- Volunteer ORM model
- init_db(), get_db() dependency
- Helper functions: save_volunteer, get_all_volunteers, get_stats
"""

# ─────────────────────────────────────────────
# SECTION 1 — IMPORTS
# ─────────────────────────────────────────────
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker


# ─────────────────────────────────────────────
# SECTION 2 — DATABASE CONNECTION
# ─────────────────────────────────────────────
DATABASE_URL = "sqlite:///./nayepankh.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ─────────────────────────────────────────────
# SECTION 3 — VOLUNTEER MODEL
# ─────────────────────────────────────────────
class Volunteer(Base):
    __tablename__ = "volunteers"

    id             = Column(Integer, primary_key=True, index=True)
    name           = Column(String,  nullable=False)
    email          = Column(String,  unique=True, index=True, nullable=False)
    skills         = Column(String,  nullable=False)
    city           = Column(String,  nullable=False)
    hours_per_week = Column(Integer, nullable=False)
    department     = Column(String,  nullable=False)
    registered_at  = Column(DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────
# SECTION 4 — INITIALIZE FUNCTION
# ─────────────────────────────────────────────
def init_db():
    """Create all tables in the database (runs once on startup)."""
    Base.metadata.create_all(bind=engine)


# ─────────────────────────────────────────────
# SECTION 5 — GET DB DEPENDENCY
# ─────────────────────────────────────────────
def get_db():
    """
    FastAPI dependency — opens a DB session per request, closes it after.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────
# SECTION 6 — HELPER FUNCTIONS
# ─────────────────────────────────────────────
def save_volunteer(db, name: str, email: str, skills: str,
                   city: str, hours_per_week: int, department: str):
    """Create and persist a new Volunteer record. Returns the saved object."""
    volunteer = Volunteer(
        name=name,
        email=email,
        skills=skills,
        city=city,
        hours_per_week=hours_per_week,
        department=department,
    )
    db.add(volunteer)
    db.commit()
    db.refresh(volunteer)
    return volunteer


def get_all_volunteers(db):
    """Return all volunteers from the database."""
    return db.query(Volunteer).all()


def get_stats(db) -> dict:
    """
    Return aggregated volunteer statistics.

    Returns:
        {
            "total": int,
            "by_department": { dept_name: count, ... },
            "by_city":       { city_name: count, ... }
        }
    """
    volunteers = get_all_volunteers(db)

    by_department = {}
    by_city = {}

    for v in volunteers:
        # Count by department
        by_department[v.department] = by_department.get(v.department, 0) + 1
        # Count by city
        by_city[v.city] = by_city.get(v.city, 0) + 1

    return {
        "total":         len(volunteers),
        "by_department": by_department,
        "by_city":       by_city,
    }
