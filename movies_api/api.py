from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Movies, get_db

from models import Movie as ModelMovie

from schema import Movie as SchemaMovie

app = FastAPI()

origins = [
    'http://localhost:3000'
]

# to avoid csrftoken error
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get('/')
def index():
    return {'message': 'Hello, world!'}


@app.get('/movies')
def get_movies(
    page: int = Query(1),
    size: int = Query(20),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * size
    movies = db.query(Movies).offset(offset).limit(size).all()
    
    total_records = db.query(Movies).count()
    total_pages = total_records // size + 1 if total_records % size != 0 else total_records // size

    return {
        "data": movies,
        "page": page,
        "size": size,
        "totalPages": total_pages,
        "totalRecords": total_records
    }

@app.get('/movies/{id}')
def get_movie(id: str, db: Session = Depends(get_db)):
    movie = db.query(Movies).filter(Movies.movie_id == id).first()

    return movie


@app.get('/movies/search')
def search_movie(search_content: str, db: Session = Depends(get_db)):
    movies = db.query(Movies).filter(Movies.title.like(f'%{search_content}%')).all()

    return movies