from fastapi import FastAPI,Response,status,HTTPException, Depends , APIRouter
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional,List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session


from database import engine, get_db
import models,schemas,utils

router = APIRouter(
    prefix = "/posts" 
    ,tags = ["Posts"]
    )

@router.get("/",response_model = List[schemas.Post])
def get_posts(db:Session =Depends(get_db)):
    # cur.execute("""SELECT * FROM posts""")
    # posts =cur.fetchall()
    # print(posts)
    posts = db.query(models.Post).all()
 
    return posts

@router.post("/posts3",status_code = status.HTTP_201_CREATED, response_model = schemas.Post) 
def create_post_sqlalchemy2(post:schemas.PostCreate, db:Session =Depends(get_db)):
    new_post = models.Post(**post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post