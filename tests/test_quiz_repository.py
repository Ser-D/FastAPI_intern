import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.redis import redis_client
from app.models import Member
from app.models.question import Question as QuestionModel
from app.models.quiz import Quiz as QuizModel
from app.models.quizresult import QuizResult as QuizResultModel
from app.repository.notifications import notification_repo
from app.repository.quizresult import repo_quizresult
from app.repository.quizzes import QuizRepository
from app.schemas.quizzes import QuizRunResponse


@pytest.mark.asyncio
async def test_create_quiz(mock_db_session, quiz_create_data):
    question = QuestionModel(id=1, company_id=1)

    with patch.object(
        QuizRepository, "check_if_admin", new_callable=AsyncMock, return_value=None
    ):
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [question]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        with patch.object(
            mock_db_session, "execute", new_callable=AsyncMock, return_value=mock_result
        ):
            with patch.object(
                mock_db_session, "commit", new_callable=AsyncMock, return_value=None
            ):
                with patch.object(
                    mock_db_session,
                    "refresh",
                    new_callable=AsyncMock,
                    return_value=None,
                ):
                    with patch.object(
                        mock_db_session,
                        "add",
                        new_callable=AsyncMock,
                        return_value=None,
                    ):
                        with patch.object(
                            notification_repo,
                            "create_quiz_notification",
                            new_callable=AsyncMock,
                            return_value=None,
                        ):
                            quiz_repo = QuizRepository()
                            created_quiz = await quiz_repo.create_quiz(
                                db=mock_db_session,
                                quiz=quiz_create_data,
                                company_id=1,
                                user_id=1,
                            )

                            assert created_quiz.title == quiz_create_data.title
                            assert (
                                created_quiz.description == quiz_create_data.description
                            )


@pytest.mark.asyncio
async def test_get_quizzes(mock_db_session, quiz_create_data):
    quiz = QuizModel(
        id=1,
        company_id=1,
        title=quiz_create_data.title,
        description=quiz_create_data.description,
    )

    with patch.object(
        QuizRepository, "check_if_admin", new_callable=AsyncMock, return_value=None
    ):
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [quiz]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        with patch.object(
            mock_db_session, "execute", new_callable=AsyncMock, return_value=mock_result
        ):
            quiz_repo = QuizRepository()
            quizzes = await quiz_repo.get_quizzes(
                db=mock_db_session, company_id=1, user_id=1, skip=0, limit=10
            )

            assert len(quizzes) == 1
            assert quizzes[0].title == quiz_create_data.title


@pytest.mark.asyncio
async def test_update_quiz(mock_db_session, quiz_update_data):
    quiz = QuizModel(
        id=1,
        company_id=1,
        title=quiz_update_data.title,
        description=quiz_update_data.description,
    )

    with patch.object(QuizRepository, "check_if_admin", AsyncMock(return_value=None)):
        with patch.object(mock_db_session, "get", AsyncMock(return_value=quiz)):
            with patch.object(mock_db_session, "commit", AsyncMock(return_value=None)):
                with patch.object(
                    mock_db_session, "refresh", AsyncMock(return_value=None)
                ):
                    quiz_repo = QuizRepository()
                    updated_quiz = await quiz_repo.update_quiz(
                        db=mock_db_session,
                        quiz_id=1,
                        quiz=quiz_update_data,
                        company_id=1,
                        user_id=1,
                    )

                    assert updated_quiz.title == quiz_update_data.title
                    assert updated_quiz.description == quiz_update_data.description


@pytest.mark.asyncio
async def test_delete_quiz(mock_db_session):
    quiz = QuizModel(id=1, company_id=1)

    with patch.object(QuizRepository, "check_if_admin", AsyncMock(return_value=None)):
        with patch.object(mock_db_session, "get", AsyncMock(return_value=quiz)):
            with patch.object(mock_db_session, "commit", AsyncMock(return_value=None)):
                with patch.object(
                    mock_db_session, "delete", AsyncMock(return_value=None)
                ):
                    quiz_repo = QuizRepository()
                    await quiz_repo.delete_quiz(
                        db=mock_db_session, quiz_id=1, company_id=1, user_id=1
                    )

                    mock_db_session.get.assert_awaited_once_with(QuizModel, 1)
                    mock_db_session.commit.assert_awaited_once()
                    mock_db_session.delete.assert_awaited_once_with(quiz)


@pytest.mark.asyncio
async def test_run_quiz(mock_db_session, quiz_run_responses):
    quiz = QuizModel(id=1, company_id=1, question_ids=[1, 2, 3])
    question = QuestionModel(id=1, company_id=1, correct_answers=[1])

    with patch.object(
        mock_db_session, "get", new_callable=AsyncMock, return_value=quiz
    ):
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [question]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        with patch.object(
            mock_db_session, "execute", new_callable=AsyncMock, return_value=mock_result
        ):
            with patch.object(
                QuizRepository,
                "store_quiz_responses",
                new_callable=AsyncMock,
                return_value=None,
            ):
                with patch.object(
                    repo_quizresult,
                    "create_quiz_result",
                    new_callable=AsyncMock,
                    return_value=QuizResultModel(id=1),
                ):
                    quiz_repo = QuizRepository()
                    result = await quiz_repo.run_quiz(
                        db=mock_db_session,
                        quiz_id=1,
                        responses=quiz_run_responses,
                        user_id=1,
                        company_id=1,
                    )

                    assert result.id == 1


@pytest.mark.asyncio
async def test_get_quiz_with_questions(mock_db_session):
    quiz_id = 1
    quiz = QuizModel(id=quiz_id, question_ids=[1, 2])
    questions = [
        QuestionModel(id=1, text="Question 1", answer_options=[], correct_answers=[]),
        QuestionModel(id=2, text="Question 2", answer_options=[], correct_answers=[]),
    ]

    mock_result_quiz = MagicMock()
    mock_result_quiz.scalars.return_value.first.return_value = quiz
    mock_result_questions = MagicMock()
    mock_result_questions.scalars.return_value.all.return_value = questions

    mock_db_session.execute.side_effect = [mock_result_quiz, mock_result_questions]

    quiz_repo = QuizRepository()
    result_quiz, result_questions = await quiz_repo.get_quiz_with_questions(
        mock_db_session, quiz_id
    )

    assert result_quiz == quiz
    assert result_questions == questions


@pytest.mark.asyncio
async def test_get_quiz_from_db(mock_db_session):
    quiz_id = 1
    quiz = QuizModel(id=quiz_id)

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = quiz
    mock_db_session.execute.return_value = mock_result

    quiz_repo = QuizRepository()
    result_quiz = await quiz_repo.get_quiz_from_db(mock_db_session, quiz_id)

    assert result_quiz == quiz


@pytest.mark.asyncio
async def test_store_quiz_responses(mock_db_session):
    quiz_id = 1
    user_id = 1
    responses = [
        QuizRunResponse(selected_answers=[1]),
        QuizRunResponse(selected_answers=[2]),
    ]
    correct_answers = 2
    total_questions = 2

    quiz = QuizModel(id=quiz_id, question_ids=[1, 2])
    questions = [
        QuestionModel(id=1, text="Question 1", answer_options=[], correct_answers=[1]),
        QuestionModel(id=2, text="Question 2", answer_options=[], correct_answers=[2]),
    ]

    mock_result_quiz = MagicMock()
    mock_result_quiz.scalars.return_value.first.return_value = quiz
    mock_result_questions = MagicMock()
    mock_result_questions.scalars.return_value.all.return_value = questions

    mock_db_session.execute.side_effect = [mock_result_quiz, mock_result_questions]

    mock_redis_setex = AsyncMock()

    with patch.object(redis_client, "setex", mock_redis_setex):
        quiz_repo = QuizRepository()
        await quiz_repo.store_quiz_responses(
            mock_db_session,
            user_id,
            quiz_id,
            responses,
            correct_answers,
            total_questions,
        )

        key = f"quiz_responses:{user_id}:{quiz_id}"
        expected_data = [
            {
                "question_text": "Question 1",
                "question_answer_options": [],
                "response": {"selected_answers": [1], "is_correct": True},
            },
            {
                "question_text": "Question 2",
                "question_answer_options": [],
                "response": {"selected_answers": [2], "is_correct": True},
            },
            {
                "quiz_data": {
                    "quiz_id": quiz_id,
                    "title": quiz.title,
                    "description": quiz.description,
                    "company_id": quiz.company_id,
                    "user_id": user_id,
                    "correct_answers": correct_answers,
                    "total_questions": total_questions,
                }
            },
        ]
        mock_redis_setex.assert_awaited_once_with(
            key, timedelta(hours=48), json.dumps(expected_data)
        )


@pytest.mark.asyncio
async def test_get_last_completion_time(mock_db_session):
    user_id = 1
    quiz_id = 1
    last_completion_time = datetime.utcnow()

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = last_completion_time
    mock_db_session.execute.return_value = mock_result

    quiz_repo = QuizRepository()
    result = await quiz_repo.get_last_completion_time(mock_db_session, user_id, quiz_id)

    assert result == last_completion_time


@pytest.mark.asyncio
async def test_check_if_member(mock_db_session):
    quiz_id = 1
    user_id = 1
    company_id = 1

    quiz = QuizModel(id=quiz_id, company_id=company_id)
    member = Member(user_id=user_id, company_id=company_id)

    mock_result_quiz = MagicMock()
    mock_result_quiz.scalars.return_value.first.return_value = quiz
    mock_result_member = MagicMock()
    mock_result_member.scalar_one_or_none.return_value = member

    mock_db_session.execute.side_effect = [mock_result_quiz, mock_result_member]

    quiz_repo = QuizRepository()
    result = await quiz_repo.check_if_member(mock_db_session, user_id, quiz_id)

    assert result == company_id


@pytest.mark.asyncio
async def test_check_if_admin(mock_db_session):
    user_id = 1
    company_id = 1
    member = Member(user_id=user_id, company_id=company_id, is_admin=True)

    mock_result_admin = MagicMock()
    mock_result_admin.scalar_one_or_none.return_value = member

    mock_db_session.execute.return_value = mock_result_admin

    quiz_repo = QuizRepository()
    await quiz_repo.check_if_admin(mock_db_session, user_id, company_id)

    mock_db_session.execute.assert_called_once()
    mock_result_admin.scalar_one_or_none.assert_called_once()
