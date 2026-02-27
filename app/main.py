from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db, create_tables
from app.schemas.user import UserCreate, UserOut
from app.db.queries_users import add_user, list_users, delete_user, get_user_by_id

app = FastAPI(title="TimeBankBack")

@app.on_event("startup")
def on_startup() -> None:
    create_tables()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/users", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    # evita emails duplicados de forma amigable
    from app.db.queries_users import get_user_by_email
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Email already exists")

    return add_user(db, payload.email, payload.password, payload.full_name)


@app.get("/users", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    return list_users(db)


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/users/{user_id}")
def remove_user(user_id: int, db: Session = Depends(get_db)):
    ok = delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": True}