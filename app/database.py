from datetime import datetime
from sqlalchemy import create_engine, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session
from app.config import DATABASE_URL

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    goal: Mapped[str] = mapped_column(String(50), nullable=False)
    intensity: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    plan: Mapped["Plan | None"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )

class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)
    original_plan: Mapped[str] = mapped_column(Text, nullable=False)
    updated_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    nutrition_tip: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    user: Mapped["User"] = relationship(back_populates="plan")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_user(db: Session, user_data):
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()

def get_all_users(db: Session):
    return db.query(User).order_by(User.created_at.desc()).all()

def save_plan(db: Session, user_id: int, original_plan: str, nutrition_tip: str):
    plan = Plan(
        user_id=user_id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

def get_original_plan(db: Session, user_id: int):
    return db.query(Plan).filter(Plan.user_id == user_id).first()

def update_plan(db: Session, plan: Plan, updated_plan: str, nutrition_tip: str):
    plan.updated_plan = updated_plan
    plan.nutrition_tip = nutrition_tip
    plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(plan)
    return plan

def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()