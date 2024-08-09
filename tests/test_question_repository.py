from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models import Member
from app.models.question import Question as QuestionModel
from app.repository.questions import QuestionRepository
from app.schemas.questions import QuestionCreate, QuestionUpdate


@pytest.mark.asyncio
async def test_check_if_admin_authorized(mock_db_session):
    member = Member(company_id=1, user_id=1, is_admin=True)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = member

    with patch.object(
        mock_db_session, "execute", new_callable=AsyncMock, return_value=mock_result
    ):
        question_repo = QuestionRepository()
        await question_repo.check_if_admin(db=mock_db_session, user_id=1, company_id=1)


@pytest.mark.asyncio
async def test_create_question(mock_db_session):
    question_data = QuestionCreate(
        text="Sample question?",
        answer_options=["Option 1", "Option 2"],
        correct_answers=["0"],
    )

    with patch.object(
        QuestionRepository, "check_if_admin", new_callable=AsyncMock, return_value=None
    ):
        with patch.object(mock_db_session, "add", new_callable=AsyncMock) as mock_add:
            with patch.object(
                mock_db_session, "commit", new_callable=AsyncMock
            ) as mock_commit:
                with patch.object(
                    mock_db_session, "refresh", new_callable=AsyncMock
                ) as mock_refresh:
                    question_repo = QuestionRepository()
                    created_question = await question_repo.create_question(
                        db=mock_db_session,
                        question=question_data,
                        company_id=1,
                        user_id=1,
                    )

                    assert created_question.text == question_data.text
                    assert (
                        created_question.answer_options == question_data.answer_options
                    )
                    mock_add.assert_called_once()
                    mock_commit.assert_awaited_once()

                    refreshed_question = mock_refresh.call_args[0][0]
                    assert refreshed_question.text == question_data.text
                    assert (
                        refreshed_question.answer_options
                        == question_data.answer_options
                    )
                    assert (
                        refreshed_question.correct_answers
                        == question_data.correct_answers
                    )


@pytest.mark.asyncio
async def test_get_questions(mock_db_session):
    question_model = QuestionModel(
        id=1,
        text="Sample question?",
        answer_options=["Option 1", "Option 2"],
        correct_answers=["0"],
        company_id=1,
    )

    with patch.object(
        QuestionRepository, "check_if_admin", new_callable=AsyncMock, return_value=None
    ):
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [question_model]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        with patch.object(
            mock_db_session, "execute", new_callable=AsyncMock, return_value=mock_result
        ):
            question_repo = QuestionRepository()
            questions = await question_repo.get_questions(
                db=mock_db_session, company_id=1, user_id=1
            )

            assert len(questions) == 1
            assert questions[0].text == question_model.text


@pytest.mark.asyncio
async def test_update_question(mock_db_session):
    question_data = QuestionUpdate(
        text="Updated question?",
        answer_options=["Option 1", "Option 2", "Option 3"],
        correct_answers=[1],
    )
    question_model = QuestionModel(
        id=1,
        text="Sample question?",
        answer_options=["Option 1", "Option 2"],
        correct_answers=["0"],
        company_id=1,
    )
    updated_question_model = QuestionModel(
        id=1,
        text=question_data.text,
        answer_options=question_data.answer_options,
        correct_answers=[str(answer) for answer in question_data.correct_answers],
        company_id=1,
    )

    with patch.object(
        QuestionRepository, "check_if_admin", new_callable=AsyncMock, return_value=None
    ):
        with patch.object(
            mock_db_session, "get", new_callable=AsyncMock, return_value=question_model
        ):
            with patch.object(
                mock_db_session, "commit", new_callable=AsyncMock
            ) as mock_commit:
                with patch.object(
                    mock_db_session,
                    "refresh",
                    new_callable=AsyncMock,
                    return_value=updated_question_model,
                ) as mock_refresh:
                    question_repo = QuestionRepository()
                    updated_question = await question_repo.update_question(
                        db=mock_db_session,
                        question_id=1,
                        question=question_data,
                        company_id=1,
                        user_id=1,
                    )

                    assert updated_question.text == question_data.text
                    assert (
                        updated_question.answer_options == question_data.answer_options
                    )
                    assert updated_question.correct_answers == [
                        str(answer) for answer in question_data.correct_answers
                    ]
                    mock_commit.assert_awaited_once()

                    refreshed_question = mock_refresh.call_args[0][0]
                    assert refreshed_question.text == question_data.text
                    assert (
                        refreshed_question.answer_options
                        == question_data.answer_options
                    )
                    assert refreshed_question.correct_answers == [
                        str(answer) for answer in question_data.correct_answers
                    ]
