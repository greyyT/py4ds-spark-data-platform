from fastapi import FastAPI
from schema import MovieRecommendaionSchema, PredictCommentSchema
from tensorflow.keras.models import load_model

from utils import text_preprocessing

model = load_model('cnn_lstm.h5')

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
    processed_comment = text_preprocessing([request.comment])
    
    print(processed_comment)

    is_positive = model.predict(processed_comment)

    return {
        'comment': request.comment,
        'isPositive': 'Positive' if is_positive[0][0] > 0.5 else 'Negative',
        'accuracy': is_positive[0][0] if is_positive[0][0] > 0.5 else 1 - is_positive[0][0],
    }