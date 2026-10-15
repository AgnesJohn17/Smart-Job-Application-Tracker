"""Job tracker REST API. All application queries are scoped to the signed-in user."""
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Application, User
from .schemas import ApplicationInput, ApplicationOut, ApplicationPatch, Dashboard, Login, Register, Status, Token
from .security import current_user, hash_password, make_token, verify_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    # MVP simplification; use Alembic migrations for production schema changes.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Smart Job Application Tracker API", version="0.1.0", lifespan=lifespan)
origins = [s.strip() for s in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if s.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(body: Register, db: Session = Depends(get_db)):
    email = str(body.email).lower()
    if db.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(409, "Email already registered")
    user = User(email=email, password_hash=hash_password(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already registered")
    db.refresh(user)
    return Token(access_token=make_token(user.id))


@app.post("/api/auth/login", response_model=Token)
def login(body: Login, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(body.email).lower()))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return Token(access_token=make_token(user.id))


@app.get("/api/auth/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email}


@app.get("/api/applications", response_model=list[ApplicationOut])
def list_applications(
    q: str = Query(default="", max_length=120),
    stage: Status | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    query = select(Application).where(Application.owner_id == user.id)
    if q.strip():
        term = f"%{q.strip()}%"
        query = query.where(or_(Application.company.ilike(term), Application.role.ilike(term)))
    if stage:
        query = query.where(Application.status == stage)
    return db.scalars(query.order_by(Application.created_at.desc(), Application.id.desc())).all()


@app.post("/api/applications", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def add_application(body: ApplicationInput, db: Session = Depends(get_db), user: User = Depends(current_user)):
    data = body.model_dump(mode="json")
    record = Application(owner_id=user.id, **data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def owned_application(app_id: int, db: Session, user: User):
    record = db.scalar(select(Application).where(Application.id == app_id, Application.owner_id == user.id))
    if record is None:
        raise HTTPException(404, "Application not found")
    return record


@app.patch("/api/applications/{app_id}", response_model=ApplicationOut)
def edit_application(app_id: int, body: ApplicationPatch, db: Session = Depends(get_db), user: User = Depends(current_user)):
    record = owned_application(app_id, db, user)
    changes = body.model_dump(exclude_unset=True, mode="json")
    for field, value in changes.items():
        if field in ("company", "role", "status") and value is None:
            raise HTTPException(422, f"{field} cannot be null")
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@app.delete("/api/applications/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(app_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    record = owned_application(app_id, db, user)
    db.delete(record)
    db.commit()
    return None


@app.get("/api/dashboard", response_model=Dashboard)
def dashboard(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.execute(select(Application.status, func.count(Application.id)).where(Application.owner_id == user.id).group_by(Application.status)).all()
    output = {stage: 0 for stage in ("Wishlist", "Applied", "Interview", "Offer", "Rejected")}
    for stage, count in rows:
        output[stage] = count
    return Dashboard(total=sum(output.values()), **output)
