
from fastapi import FastAPI,Response,status,HTTPException, Depends
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
from routers import post,user




models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)
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

    posts = db.query(models.Post).all()

    return {"data":posts}



@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate):
    cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s,%s,%s) RETURNING *""",(post.title,post.content,post.published,))
    new_post = cur.fetchone()
    conn.commit()
    print(new_post)
    return {"data":new_post}
#title str, content str, category, Bool published

@app.post("/post", status_code= status.HTTP_201_CREATED)
def create_post_sqlalchemy(post:schemas.PostCreate, db:Session =Depends(get_db)):
    #new_post = models.Post(
    #title = post.title,content = post.content, published = post.published)
    #print(**post.dict())
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts/{id}")
def get_post(id:int):
    cur.execute("""SELECT * FROM posts WHERE id = %s""",(str(id),))
    post = cur.fetchone()

    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with{id} was not found")
    return {"post_detail":post}

@app.get("/posts2/{id}")
def get_post_sqlalchemy(id:int,db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with{id} was not found")
    return post
    



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

@app.delete("/posts2/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post_sqlalchemy (id:int,db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with{id} was not found")
    post.delete(synchronize_session=False)
    db.commit()

    return post

@app.put("/posts/{id}")
def update_post(id:int, post:schemas.PostCreate):
    
    cur.execute("""UPDATE posts SET title =%s, content = %s, published =%s WHERE id = %s RETURNING * """,(post.title, post.content, post.published, str(id),))
    index = cur.fetchone()
    if not index:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail =f"{id} not found")
    conn.commit()
    return {"message": f"update {id} DONE!"}
    
@app.put("/posts2/{id}",response_model = schemas.Post)
def update_post_sqlalchemy(id:int,db: Session = Depends(get_db)):

    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with{id} was not found")
    post.update({'title':'hey yoyoy ehceojfdisof','content':'changed'}, synchronize_session=False)
    db.commit()

    return {"post_detail":'successful'}

######USERS######
