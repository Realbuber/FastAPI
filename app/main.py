import os
from fastapi import FastAPI,Response,status,HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session

from models import Post
from database import engine, get_db

Post.metadata.create_all(bind=engine)
app = FastAPI()





class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating:Optional[int] = None

while True:
    try:
        conn = psycopg2.connect(
            host = 'localhost',
            database = 'fastapi',
            user = 'postgres',
            password = 'aaaa1177',
            cursor_factory = RealDictCursor
            )
        cur = conn.cursor()
        print("DB connect successful.")
        break
    except Exception as error:
        print("connect to db failed")
        print("Error:",error)
        time.sleep(2)


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/sqlalchemy")
def test_posts(db:Session =Depends(get_db)):

    posts = db.query(Post).all()

    return {"data":posts}

@app.get("/posts")
def get_posts():
    cur.execute("""SELECT * FROM posts""")
    posts =cur.fetchall()
    print(posts)
    return {"data":posts}

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s,%s,%s) RETURNING *""",(post.title,post.content,post.published,))
    new_post = cur.fetchone()
    conn.commit()
    print(new_post)
    return {"data":new_post}
#title str, content str, category, Bool published


@app.get("/posts/{id}")
def get_post(id:int):
    cur.execute("""SELECT * FROM posts WHERE id = %s""",(str(id),))
    post = cur.fetchone()
#123
    #post = find_post(id)

    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with{id} was not found")
    
    return {"post_detail":post}

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    #delete post
    #find the index in arry to delete
    cur.execute("""DELETE FROM posts WHERE id = %s Returning *""",(str(id),))
    index = cur.fetchone()
    conn.commit()
    if not index:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail ="id not found")
    
    return {"message":f"delete {id} successful."}

@app.put("/posts/{id}")
def update_post(id:int, post:Post):
    
    cur.execute("""UPDATE posts SET title =%s, content = %s, published =%s WHERE id = %s RETURNING * """,(post.title, post.content, post.published, str(id),))
    index = cur.fetchone()
    if not index:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail =f"{id} not found")
    conn.commit()
    return {"message": f"update {id} DONE!"}
    
    