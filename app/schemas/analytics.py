from datetime import date, datetime
from typing import List

from pydantic import BaseModel


class UserAverageScore(BaseModel):
    average_score: float


class QuizAverageScore(BaseModel):
    quiz_id: int
    average_score: float
    first_completed: datetime
    last_completed: datetime


class QuizCompletion(BaseModel):
    quiz_id: int
    last_completed: datetime


class MemberAverageScore(BaseModel):
    user_id: int
    average_score: float


class MemberQuizCompletion(BaseModel):
    user_id: int
    last_completed: datetime


class WeeklyScore(BaseModel):
    week_start: datetime
    week_end: datetime
    average_score: float


class WeeklyMemberAverageScore(BaseModel):
    user_id: int
    weekly_scores: list[WeeklyScore]


class UserWeeklyScore(BaseModel):
    user_id: int
    average_score: float


class WeeklyScores(BaseModel):
    week_start: datetime
    week_end: datetime
    user_scores: List[UserWeeklyScore]


class QuizWeeklyScore(BaseModel):
    quiz_id: int
    average_score: float


class UserQuizWeeklyScores(BaseModel):
    week_start: date
    week_end: date
    quiz_scores: List[QuizWeeklyScore]
