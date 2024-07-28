from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    correct_answers = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    completed_at = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="quiz_results")
    company = relationship("Company", back_populates="quiz_results")
    quiz = relationship("Quiz", back_populates="quiz_results")

    def __repr__(self):
        return (
            f"<QuizResult(id={self.id}, user_id={self.user_id}, "
            f"company_id={self.company_id}, quiz_id={self.quiz_id}, "
            f"score={self.score}, completed_at={self.completed_at})>"
        )
