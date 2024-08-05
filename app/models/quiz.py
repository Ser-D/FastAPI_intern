from sqlalchemy import ARRAY, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    question_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)

    company = relationship("Company", back_populates="quizzes")
    quiz_results = relationship("QuizResult", back_populates="quiz")
