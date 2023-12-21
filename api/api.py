from fastapi import FastAPI
from schema import MovieRecommendaionSchema, PredictCommentSchema


app = FastAPI()


@app.get('/')
def index():
    return {'message': 'Hello, world!'}


@app.post('/recommend-movie')
def recommend_movie(request: MovieRecommendaionSchema):
    return {
        'movieId': request.movieId,
        'rating': 5,
    }


@app.post('/predict-comment')
def predict_comment(request: PredictCommentSchema):
    return {
        'comment': request.comment,
        'isPositive': False,
    }