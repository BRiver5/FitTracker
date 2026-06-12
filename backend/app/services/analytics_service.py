from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import CalorieLog, SessionSet, WeightLog, WorkoutSession


def _day_start(d: date) -> datetime:
    return datetime.combine(d, time.min, tzinfo=timezone.utc)


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def summary(self, user_id: int) -> dict:
        today = datetime.now(timezone.utc).date()

        session_days = {
            row.date()
            for row in self.db.scalars(
                select(WorkoutSession.started_at).where(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.finished_at.is_not(None),
                )
            )
        }
        streak = 0
        cursor = today
        if cursor not in session_days:
            cursor -= timedelta(days=1)
        while cursor in session_days:
            streak += 1
            cursor -= timedelta(days=1)

        total_workouts = (
            self.db.scalar(
                select(func.count(WorkoutSession.id)).where(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.finished_at.is_not(None),
                )
            )
            or 0
        )

        total_volume = (
            self.db.scalar(
                select(func.coalesce(func.sum(SessionSet.weight_kg * SessionSet.reps), 0))
                .join(WorkoutSession, SessionSet.session_id == WorkoutSession.id)
                .where(WorkoutSession.user_id == user_id)
            )
            or 0
        )

        week_ago = _day_start(today - timedelta(days=6))
        avg_kcal_row = self.db.execute(
            select(
                func.coalesce(func.sum(CalorieLog.kcal), 0),
                func.count(func.distinct(func.date(CalorieLog.logged_at))),
            ).where(CalorieLog.user_id == user_id, CalorieLog.logged_at >= week_ago)
        ).one()
        total_kcal, days_logged = float(avg_kcal_row[0]), int(avg_kcal_row[1])
        avg_calories = round(total_kcal / days_logged) if days_logged else 0

        latest_weight = self.db.scalar(
            select(WeightLog.weight_kg)
            .where(WeightLog.user_id == user_id)
            .order_by(WeightLog.logged_at.desc())
            .limit(1)
        )
        prev_week_weight = self.db.scalar(
            select(func.avg(WeightLog.weight_kg)).where(
                WeightLog.user_id == user_id,
                WeightLog.logged_at < week_ago,
                WeightLog.logged_at >= _day_start(today - timedelta(days=13)),
            )
        )
        weight_delta = None
        if latest_weight is not None and prev_week_weight is not None:
            weight_delta = round(float(latest_weight) - float(prev_week_weight), 1)

        # Today's quick stats
        today_start = _day_start(today)
        today_sessions = list(
            self.db.scalars(
                select(WorkoutSession).where(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.started_at >= today_start,
                )
            )
        )
        active_minutes = 0
        for s in today_sessions:
            end = s.finished_at or datetime.now(timezone.utc)
            start = s.started_at if s.started_at.tzinfo else s.started_at.replace(tzinfo=timezone.utc)
            end = end if end.tzinfo else end.replace(tzinfo=timezone.utc)
            active_minutes += max(0, int((end - start).total_seconds() // 60))
        workouts_today = sum(1 for s in today_sessions if s.finished_at is not None)
        # Rough estimate: ~7 kcal burned per active minute of training
        calories_burned_today = active_minutes * 7

        return {
            "streak_days": streak,
            "total_workouts": total_workouts,
            "total_volume_kg": round(float(total_volume), 1),
            "avg_calories_week": avg_calories,
            "latest_weight_kg": float(latest_weight) if latest_weight is not None else None,
            "weight_delta_kg": weight_delta,
            "today": {
                "workouts_done": workouts_today,
                "active_minutes": active_minutes,
                "calories_burned": calories_burned_today,
            },
        }

    def progress(self, user_id: int, range_days: int) -> dict:
        today = datetime.now(timezone.utc).date()
        start = _day_start(today - timedelta(days=range_days - 1))
        prev_start = _day_start(today - timedelta(days=2 * range_days - 1))

        def daily_series(rows: list[tuple], agg: str) -> list[dict]:
            by_day: dict[str, list[float]] = {}
            for logged_at, value in rows:
                key = logged_at.date().isoformat()
                by_day.setdefault(key, []).append(float(value))
            series = []
            for i in range(range_days):
                d = (today - timedelta(days=range_days - 1 - i)).isoformat()
                values = by_day.get(d, [])
                if not values:
                    series.append({"date": d, "value": None})
                elif agg == "sum":
                    series.append({"date": d, "value": round(sum(values), 1)})
                else:
                    series.append({"date": d, "value": round(sum(values) / len(values), 1)})
            return series

        kcal_rows = self.db.execute(
            select(CalorieLog.logged_at, CalorieLog.kcal).where(
                CalorieLog.user_id == user_id, CalorieLog.logged_at >= start
            )
        ).all()
        weight_rows = self.db.execute(
            select(WeightLog.logged_at, WeightLog.weight_kg).where(
                WeightLog.user_id == user_id, WeightLog.logged_at >= start
            )
        ).all()

        prev_kcal = self.db.scalar(
            select(func.coalesce(func.sum(CalorieLog.kcal), 0)).where(
                CalorieLog.user_id == user_id,
                CalorieLog.logged_at >= prev_start,
                CalorieLog.logged_at < start,
            )
        )
        cur_kcal = sum(float(v) for _, v in kcal_rows)

        prev_weight_avg = self.db.scalar(
            select(func.avg(WeightLog.weight_kg)).where(
                WeightLog.user_id == user_id,
                WeightLog.logged_at >= prev_start,
                WeightLog.logged_at < start,
            )
        )
        cur_weights = [float(v) for _, v in weight_rows]
        cur_weight_avg = round(sum(cur_weights) / len(cur_weights), 1) if cur_weights else None

        macros = self.db.execute(
            select(
                func.coalesce(func.sum(CalorieLog.protein), 0),
                func.coalesce(func.sum(CalorieLog.carbs), 0),
                func.coalesce(func.sum(CalorieLog.fat), 0),
            ).where(CalorieLog.user_id == user_id, CalorieLog.logged_at >= start)
        ).one()

        # Personal records: max weight per exercise
        pr_rows = self.db.execute(
            select(
                SessionSet.exercise_id,
                func.max(SessionSet.weight_kg),
            )
            .join(WorkoutSession, SessionSet.session_id == WorkoutSession.id)
            .where(WorkoutSession.user_id == user_id, SessionSet.weight_kg.is_not(None))
            .group_by(SessionSet.exercise_id)
        ).all()
        records = []
        for exercise_id, max_weight in pr_rows:
            detail = self.db.execute(
                select(SessionSet.completed_at, SessionSet.reps)
                .join(WorkoutSession, SessionSet.session_id == WorkoutSession.id)
                .where(
                    WorkoutSession.user_id == user_id,
                    SessionSet.exercise_id == exercise_id,
                    SessionSet.weight_kg == max_weight,
                )
                .order_by(SessionSet.completed_at.desc())
                .limit(1)
            ).one()
            from app.models import Exercise

            exercise = self.db.get(Exercise, exercise_id)
            records.append(
                {
                    "exercise_id": exercise_id,
                    "exercise_name": exercise.name if exercise else "Unknown",
                    "weight_kg": float(max_weight),
                    "reps": detail[1],
                    "date": detail[0].date().isoformat(),
                }
            )
        records.sort(key=lambda r: r["weight_kg"], reverse=True)

        return {
            "range_days": range_days,
            "calories": {
                "series": daily_series(kcal_rows, "sum"),
                "average": round(cur_kcal / range_days) if range_days else 0,
                "delta_vs_previous": round(cur_kcal - float(prev_kcal or 0), 1),
            },
            "weight": {
                "series": daily_series(weight_rows, "avg"),
                "average": cur_weight_avg,
                "delta_vs_previous": (
                    round(cur_weight_avg - float(prev_weight_avg), 1)
                    if cur_weight_avg is not None and prev_weight_avg is not None
                    else None
                ),
            },
            "macros": {
                "protein": round(float(macros[0]), 1),
                "carbs": round(float(macros[1]), 1),
                "fat": round(float(macros[2]), 1),
            },
            "personal_records": records[:10],
        }
