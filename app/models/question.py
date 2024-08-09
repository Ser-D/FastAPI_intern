from typing import List

from sqlalchemy import ARRAY, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    answer_options: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    correct_answers: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)

    company = relationship("Company", back_populates="questions")
