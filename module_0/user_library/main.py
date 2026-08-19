"""
User Library - a mini CRUD app with FastAPI
"""

from datetime import date
from typing import Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="User Library API", version="1.0.0")

users_db: list[dict] = []


# Models

class UserCreate(BaseModel):
    name: str
    dob: date
    gender: str
    city: str
    email: str
    phone: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    dob: Optional[date] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None


# Routes

@app.post("/users/", status_code=201)
async def create_user(user_data: UserCreate):
    
    for user in users_db:
        if user["email"] == user_data.email:
            raise HTTPException(status_code=409, detail="Email already exists")

    user = user_data.model_dump()
    user["id"] = str(uuid4())
    users_db.append(user)
    return user


@app.get("/users/")
async def list_users():
    return users_db


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.put("/users/{user_id}")
async def update_user(user_id: str, update_data: UserUpdate):
    for user in users_db:
        if user["id"] == user_id:
            updates = update_data.model_dump(exclude_unset=True)

            if "email" in updates:
                for other in users_db:
                    if other["email"] == updates["email"] and other["id"] != user_id:
                        raise HTTPException(status_code=409, detail="Email already exists")

            user.update(updates)
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    for i, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db.pop(i)
            return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")


# Run

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
