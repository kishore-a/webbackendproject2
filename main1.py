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
@app.post("/plans/")
def create_subscription_plan(plan: SubscriptionPlanCreate, db: Session = Depends(get_db)):
    db_plan = SubscriptionPlanModel(name=plan.name, details=plan.details)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan
@app.put("/permissions/{permission_id}")
def update_permission(permission_id: int, permission: PermissionUpdate, db: Session = Depends(get_db)):
    db_permission = db.query(PermissionModel).filter(PermissionModel.id == permission_id).first()

    if db_permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")

    db_permission.name = permission.name
    db_permission.details = permission.details

    db.commit()
    db.refresh(db_permission)

    return db_permission
@app.delete("/permissions/{permission_id}")
def delete_permission(permission_id: int, db: Session = Depends(get_db)):
    db_permission = db.query(PermissionModel).filter(PermissionModel.id == permission_id).first()
    if db_permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    db.delete(db_permission)
    db.commit()
    return {"message": "Permission deleted successfully"}

@app.put("/plans/{plan_id}")
def update_subscription_plan(plan_id: int, plan: SubscriptionPlanCreate, db: Session = Depends(get_db)):
    db_plan = db.query(SubscriptionPlanModel).filter(SubscriptionPlanModel.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    db_plan.name = plan.name
    db_plan.details = plan.details
    db.commit()
    db.refresh(db_plan)
    return db_plan

@app.delete("/plans/{plan_id}")
def delete_subscription_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = db.query(SubscriptionPlanModel).filter(SubscriptionPlanModel.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    db.delete(db_plan)
    db.commit()
    return {"message": "Subscription plan deleted successfully"}
@app.post("/permissions/")
def create_permission(permission: PermissionCreate, db: Session = Depends(get_db)):
    db_permission = PermissionModel(name=permission.name, details=permission.details)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission
@app.post("/subscriptions/")
def create_user_subscription(subscription: UserSubscriptionCreate, db: Session = Depends(get_db)):
    db_subscription = UserSubscriptionModel(user_id=subscription.user_id, plan_id=subscription.plan_id)
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription
@app.get("/subscriptions/{user_id}", response_model=UserSubscription)
def view_user_subscription(user_id: str, db: Session = Depends(get_db)):
    db_subscription = db.query(UserSubscriptionModel).filter(UserSubscriptionModel.user_id == user_id).first()

    if db_subscription is None:
        raise HTTPException(status_code=404, detail="User subscription not found")

    return db_subscription
@app.put("/subscriptions/{user_id}", response_model=UserSubscription)
def update_user_plan(user_id: str, subscription_update: UserSubscriptionUpdate, db: Session = Depends(get_db)):
    db_subscription = db.query(UserSubscriptionModel).filter(UserSubscriptionModel.user_id == user_id).first()

    if db_subscription is None:
        raise HTTPException(status_code=404, detail="User subscription not found")

    db_subscription.plan_id = subscription_update.plan_id
    db.commit()
    db.refresh(db_subscription)

    return db_subscription
@app.get("/check-access/{user_id}/{service_id}")
def check_access(user_id: str, service_id: str, db: Session = Depends(get_db)):
    db_subscription = db.query(UserSubscriptionModel).filter(UserSubscriptionModel.user_id == user_id).first()

    if db_subscription is None:
        raise HTTPException(status_code=404, detail="User subscription not found")

    if has_access_to_service(db_subscription.plan_id, service_id, db):
        return {"access": True}
    else:
        return {"access": False}
def track_api_status(api_endpoint: str, db: Session):
    api_status = db.query(APIStatusModel).filter(APIStatusModel.api_endpoint == api_endpoint).first()

    if api_status:
        api_status.call_count += 1
    else:
        api_status = APIStatusModel(api_endpoint=api_endpoint, call_count=1)
        db.add(api_status)

    db.commit()
@app.get("/some-api-endpoint")
def some_api_endpoint(db: Session = Depends(get_db)):

    track_api_status("/some-api-endpoint", db)

    return {"message": "API response"}
@app.get("/api-status")
def get_api_status(db: Session = Depends(get_db)):
    api_statuses = db.query(APIStatusModel).all()
    return api_statuses
@app.get("/limit-status/{user_id}")
def check_limit_status(user_id: str, db: Session = Depends(get_db)):
    user_usage = db.query(UserUsageModel).filter(UserUsageModel.user_id == user_id).first()

    if user_usage is None:
        raise HTTPException(status_code=404, detail="User usage data not found")

    user_subscription = db.query(UserSubscriptionModel).filter(UserSubscriptionModel.user_id == user_id).first()
    if user_subscription is None:
        raise HTTPException(status_code=404, detail="User subscription not found")

    limits = get_plan_limits(user_subscription.plan_id, db)

    limit_status = {
        "api_calls_made": user_usage.api_calls_made,
        "api_call_limit": limits['api_call_limit'],
        "within_limit": user_usage.api_calls_made <= limits['api_call_limit']
    }

    return limit_status
def get_plan_limits(plan_id: int, db: Session) -> dict:
    subscription_plan = db.query(SubscriptionPlanModel).filter(SubscriptionPlanModel.id == plan_id).first()

    if subscription_plan is None:
        raise HTTPException(status_code=404, detail="Subscription plan not found")


    limits = {
        "api_call_limit": subscription_plan.api_call_limit
    }

    return limits

def has_access_to_service(plan_id: int, service_id: str, db: Session) -> bool:
    access = db.query(PlanServiceAssociation).filter(
        PlanServiceAssociation.plan_id == plan_id,
        PlanServiceAssociation.service_id == service_id
    ).first()

    return access is not None