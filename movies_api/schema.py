from pydantic import BaseModel
from typing import Optional

class Movie(BaseModel):
    movie_id: str
    score: Optional[float]
    title: Optional[str]
    duration: Optional[str]
    director_name: Optional[str]
    actor_1_name: Optional[str]
    actor_2_name: Optional[str]
    actor_3_name: Optional[str]
    num_reviews: Optional[int]
    num_critics: Optional[int]
    num_votes: Optional[int]
    metascore: Optional[int]
    language: Optional[str]
    global_gross: Optional[int]
    year: Optional[int]
    overview: Optional[str]
    link: Optional[str]
    src: Optional[str]
    alt: Optional[str]

    class Config:
        from_attributes = True
