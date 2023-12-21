from pydantic import BaseModel


class PredictCommentSchema(BaseModel):
    comment: str

    class Config:
        json_schema_extra = {
            "example": {
                "comment": "Yeu Chinh Dinh nhat tren doi"
            }
        }


class MovieRecommendaionSchema(BaseModel):
    movieId: int

    class Config:
        json_schema_extra = {
            "example": {
                "movieId": 1
            }
        }