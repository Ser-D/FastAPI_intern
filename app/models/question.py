from typing import List

from sqlalchemy import ARRAY, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String, nullable=False)  # Текст питання
    answer_options: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False
    )  # Перелік відповідей (від 2 до 4)
    correct_answers: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False
    )  # Перелік правильних відповідей
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id"), nullable=False
    )  # ID компанії

    company = relationship(
        "Company", back_populates="questions"
    )  # Відношення до компанії
