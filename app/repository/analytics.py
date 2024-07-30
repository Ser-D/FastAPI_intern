from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func

from app.models import Member, QuizResult
from app.schemas.analytics import (
    MemberQuizCompletion,
    QuizAverageScore,
    QuizCompletion,
    QuizWeeklyScore,
    UserQuizWeeklyScores,
    UserWeeklyScore,
    WeeklyScores,
)


class AnalyticsService:
    async def get_user_average_score(self, db: AsyncSession, user_id: int) -> float:
        result = await db.execute(
            select(func.avg(QuizResult.score)).where(QuizResult.user_id == user_id)
        )
        return result.scalar()

    async def get_user_quiz_scores(
        self,
        db: AsyncSession,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[QuizAverageScore]:
        query = select(
            QuizResult.quiz_id,
            func.avg(QuizResult.score).label("average_score"),
            func.min(QuizResult.completed_at).label("first_completed"),
            func.max(QuizResult.completed_at).label("last_completed"),
        )
        query = query.where(QuizResult.user_id == user_id)
        if start_date:
            query = query.where(QuizResult.completed_at >= start_date)
        if end_date:
            query = query.where(QuizResult.completed_at <= end_date)
        query = query.group_by(QuizResult.quiz_id)
        result = await db.execute(query)
        return [
            QuizAverageScore(
                quiz_id=row[0],
                average_score=row[1],
                first_completed=row[2],
                last_completed=row[3],
            )
            for row in result.all()
        ]

    async def get_user_quiz_completions(
        self, db: AsyncSession, user_id: int
    ) -> List[QuizCompletion]:
        result = await db.execute(
            select(
                QuizResult.quiz_id,
                func.max(QuizResult.completed_at).label("last_completed"),
            )
            .where(QuizResult.user_id == user_id)
            .group_by(QuizResult.quiz_id)
        )
        return [
            QuizCompletion(quiz_id=row[0], last_completed=row[1])
            for row in result.all()
        ]

    async def get_company_quiz_results(
        self, db: AsyncSession, company_id: int
    ) -> List[Tuple[int, datetime, float]]:
        result = await db.execute(
            select(Member.user_id, QuizResult.completed_at, QuizResult.score)
            .join(QuizResult, QuizResult.user_id == Member.user_id)
            .where(Member.company_id == company_id)
            .order_by(Member.user_id, QuizResult.completed_at)
        )
        return result.fetchall()

    async def get_company_weekly_average_scores(
        self, db: AsyncSession, company_id: int
    ) -> List[WeeklyScores]:
        quiz_results = await self.get_company_quiz_results(db, company_id)

        if not quiz_results:
            return []

        start_date = min(completed_at for _, completed_at, _ in quiz_results)
        end_date = max(completed_at for _, completed_at, _ in quiz_results)

        current_start = start_date - timedelta(days=start_date.weekday())
        weekly_dict = {}
        while current_start <= end_date:
            current_end = current_start + timedelta(days=6)
            week_key = f"{current_start.strftime('%Y-%m-%d')} - {current_end.strftime('%Y-%m-%d')}"
            weekly_dict[week_key] = {}
            current_start = current_end + timedelta(days=1)

        for user_id, completed_at, score in quiz_results:
            for week_key in weekly_dict.keys():
                week_start_str, week_end_str = week_key.split(" - ")
                week_start = datetime.strptime(week_start_str, "%Y-%m-%d")
                week_end = datetime.strptime(week_end_str, "%Y-%m-%d")
                if week_start <= completed_at <= week_end:
                    if user_id not in weekly_dict[week_key]:
                        weekly_dict[week_key][user_id] = []
                    weekly_dict[week_key][user_id].append(score)

        weekly_averages = []
        for week_key, user_scores in weekly_dict.items():
            if not user_scores:
                continue
            week_start_str, week_end_str = week_key.split(" - ")
            week_start = datetime.strptime(week_start_str, "%Y-%m-%d")
            week_end = datetime.strptime(week_end_str, "%Y-%m-%d")
            user_weekly_scores = [
                UserWeeklyScore(
                    user_id=user_id, average_score=sum(scores) / len(scores)
                )
                for user_id, scores in user_scores.items()
            ]
            weekly_averages.append(
                WeeklyScores(
                    week_start=week_start,
                    week_end=week_end,
                    user_scores=user_weekly_scores,
                )
            )

        return weekly_averages

        return weekly_dict

    async def is_user_member_of_company(
        self, db: AsyncSession, user_id: int, company_id: int
    ):
        result = await db.execute(
            select(Member).where(
                Member.user_id == user_id, Member.company_id == company_id
            )
        )
        member = result.scalars().first()
        if not member:
            raise HTTPException(
                status_code=404, detail="User is not a member of the company"
            )
        return member is not None

    async def get_user_quiz_scores_over_time(
        self, db: AsyncSession, user_id: int, company_id: int
    ) -> List[UserQuizWeeklyScores]:
        quiz_results = await db.execute(
            select(QuizResult.quiz_id, QuizResult.completed_at, QuizResult.score)
            .join(Member, Member.user_id == QuizResult.user_id)
            .where(QuizResult.user_id == user_id, Member.company_id == company_id)
        )
        quiz_results = quiz_results.fetchall()

        if not quiz_results:
            return []

        start_date = min(completed_at for _, completed_at, _ in quiz_results)
        end_date = max(completed_at for _, completed_at, _ in quiz_results)

        current_start = start_date - timedelta(days=start_date.weekday())
        weekly_dict = {}
        while current_start <= end_date:
            current_end = current_start + timedelta(days=6)
            week_key = f"{current_start.strftime('%Y-%m-%d')} - {current_end.strftime('%Y-%m-%d')}"
            weekly_dict[week_key] = {}
            current_start = current_end + timedelta(days=1)

        for quiz_id, completed_at, score in quiz_results:
            for week_key in weekly_dict.keys():
                week_start_str, week_end_str = week_key.split(" - ")
                week_start = datetime.strptime(week_start_str, "%Y-%m-%d")
                week_end = datetime.strptime(week_end_str, "%Y-%m-%d")
                if week_start <= completed_at <= week_end:
                    if quiz_id not in weekly_dict[week_key]:
                        weekly_dict[week_key][quiz_id] = []
                    weekly_dict[week_key][quiz_id].append(score)

        weekly_averages = []
        for week_key, quiz_scores in weekly_dict.items():
            if not quiz_scores:
                continue
            week_start_str, week_end_str = week_key.split(" - ")
            week_start = datetime.strptime(week_start_str, "%Y-%m-%d").date()
            week_end = datetime.strptime(week_end_str, "%Y-%m-%d").date()
            quiz_weekly_scores = [
                QuizWeeklyScore(
                    quiz_id=quiz_id, average_score=sum(scores) / len(scores)
                )
                for quiz_id, scores in quiz_scores.items()
            ]
            weekly_averages.append(
                UserQuizWeeklyScores(
                    week_start=week_start,
                    week_end=week_end,
                    quiz_scores=quiz_weekly_scores,
                )
            )

        return weekly_averages

    async def get_company_quiz_completions(
        self, db: AsyncSession, company_id: int
    ) -> List[MemberQuizCompletion]:
        result = await db.execute(
            select(
                Member.user_id,
                func.max(QuizResult.completed_at).label("last_completed"),
            )
            .join(QuizResult, QuizResult.user_id == Member.user_id)
            .where(Member.company_id == company_id)
            .group_by(Member.user_id)
        )
        return [
            MemberQuizCompletion(user_id=row[0], last_completed=row[1])
            for row in result.all()
        ]


analytics_service = AnalyticsService()
