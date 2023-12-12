from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from sqlalchemy import Column, Integer, String, ForeignKey


app = FastAPI()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI application!"}
@app.get("/favicon.ico")
def favicon():
    return FileResponse("path/to/favicon.ico")
class SubscriptionPlanModel(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    details = Column(String)

class SubscriptionPlanCreate(BaseModel):
    name: str
    details: str
class PermissionUpdate(BaseModel):
    name: str
    details: str
class PermissionModel(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    details = Column(String)
class UserSubscription(BaseModel):
    user_id: str
    plan_id: int
class PermissionCreate(BaseModel):
    name: str
    details: str
class UserUsageModel(Base):
    __tablename__ = 'user_usage'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    api_calls_made = Column(Integer, default=0)
class UserSubscriptionModel(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    plan_id = Column(Integer)

class UserSubscriptionCreate(BaseModel):
    user_id: str
    plan_id: int
class UserSubscriptionUpdate(BaseModel):
    plan_id: int 
class APIStatusModel(Base):
    __tablename__ = 'api_status'

    id = Column(Integer, primary_key=True, index=True)
    api_endpoint = Column(String, index=True)
    call_count = Column(Integer, default=0)


    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    api_call_limit = Column(Integer) 
class PlanServiceAssociation(Base):
    __tablename__ = 'plan_service_association'
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey('subscription_plans.id'))
    service_id = Column(String)
Base.metadata.create_all(bind=engine)
