from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QuizResultSchema(BaseModel):
    user_id: int
    company_id: int
    quiz_id: int
    correct_answers: int
    total_questions: int
    score: float
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserAverageScoreInCompany(BaseModel):
    user_id: int
    company_id: int
    total_questions: int
    total_correct_answers: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)


class UserAverageScoreSystemwide(BaseModel):
    user_id: int
    total_questions: int
    total_correct_answers: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)
