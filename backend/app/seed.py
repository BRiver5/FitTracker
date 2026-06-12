"""Seed the exercise library with 50+ default exercises. Idempotent."""

from app.core.database import SessionLocal
from app.models import Exercise
from app.repositories.exercise_repo import ExerciseRepository

EXERCISES: list[dict] = [
    # Push
    {"name": "Bench Press", "category": "push", "muscle_groups": ["chest", "triceps", "shoulders"]},
    {"name": "Incline Bench Press", "category": "push", "muscle_groups": ["chest", "shoulders"]},
    {"name": "Decline Bench Press", "category": "push", "muscle_groups": ["chest", "triceps"]},
    {"name": "Dumbbell Bench Press", "category": "push", "muscle_groups": ["chest", "triceps"]},
    {"name": "Overhead Press", "category": "push", "muscle_groups": ["shoulders", "triceps"]},
    {"name": "Dumbbell Shoulder Press", "category": "push", "muscle_groups": ["shoulders"]},
    {"name": "Push-Up", "category": "push", "muscle_groups": ["chest", "triceps", "core"]},
    {"name": "Dips", "category": "push", "muscle_groups": ["chest", "triceps"]},
    {"name": "Cable Fly", "category": "push", "muscle_groups": ["chest"]},
    {"name": "Lateral Raise", "category": "push", "muscle_groups": ["shoulders"]},
    {"name": "Tricep Pushdown", "category": "push", "muscle_groups": ["triceps"]},
    {"name": "Skull Crusher", "category": "push", "muscle_groups": ["triceps"]},
    {"name": "Arnold Press", "category": "push", "muscle_groups": ["shoulders"]},
    # Pull
    {"name": "Deadlift", "category": "pull", "muscle_groups": ["back", "hamstrings", "glutes"]},
    {"name": "Pull-Up", "category": "pull", "muscle_groups": ["back", "biceps"]},
    {"name": "Chin-Up", "category": "pull", "muscle_groups": ["back", "biceps"]},
    {"name": "Barbell Row", "category": "pull", "muscle_groups": ["back", "biceps"]},
    {"name": "Dumbbell Row", "category": "pull", "muscle_groups": ["back"]},
    {"name": "Lat Pulldown", "category": "pull", "muscle_groups": ["back", "biceps"]},
    {"name": "Seated Cable Row", "category": "pull", "muscle_groups": ["back"]},
    {"name": "Face Pull", "category": "pull", "muscle_groups": ["rear delts", "upper back"]},
    {"name": "Barbell Curl", "category": "pull", "muscle_groups": ["biceps"]},
    {"name": "Dumbbell Curl", "category": "pull", "muscle_groups": ["biceps"]},
    {"name": "Hammer Curl", "category": "pull", "muscle_groups": ["biceps", "forearms"]},
    {"name": "Preacher Curl", "category": "pull", "muscle_groups": ["biceps"]},
    {"name": "Shrug", "category": "pull", "muscle_groups": ["traps"]},
    # Legs
    {"name": "Back Squat", "category": "legs", "muscle_groups": ["quads", "glutes", "core"]},
    {"name": "Front Squat", "category": "legs", "muscle_groups": ["quads", "core"]},
    {"name": "Goblet Squat", "category": "legs", "muscle_groups": ["quads", "glutes"]},
    {"name": "Leg Press", "category": "legs", "muscle_groups": ["quads", "glutes"]},
    {"name": "Romanian Deadlift", "category": "legs", "muscle_groups": ["hamstrings", "glutes"]},
    {"name": "Walking Lunge", "category": "legs", "muscle_groups": ["quads", "glutes"]},
    {"name": "Bulgarian Split Squat", "category": "legs", "muscle_groups": ["quads", "glutes"]},
    {"name": "Leg Extension", "category": "legs", "muscle_groups": ["quads"]},
    {"name": "Leg Curl", "category": "legs", "muscle_groups": ["hamstrings"]},
    {"name": "Hip Thrust", "category": "legs", "muscle_groups": ["glutes"]},
    {"name": "Calf Raise", "category": "legs", "muscle_groups": ["calves"]},
    {"name": "Step-Up", "category": "legs", "muscle_groups": ["quads", "glutes"]},
    # Core
    {"name": "Plank", "category": "core", "muscle_groups": ["core"]},
    {"name": "Side Plank", "category": "core", "muscle_groups": ["obliques", "core"]},
    {"name": "Crunch", "category": "core", "muscle_groups": ["abs"]},
    {"name": "Hanging Leg Raise", "category": "core", "muscle_groups": ["abs", "hip flexors"]},
    {"name": "Russian Twist", "category": "core", "muscle_groups": ["obliques"]},
    {"name": "Ab Wheel Rollout", "category": "core", "muscle_groups": ["abs", "core"]},
    {"name": "Cable Crunch", "category": "core", "muscle_groups": ["abs"]},
    {"name": "Dead Bug", "category": "core", "muscle_groups": ["core"]},
    {"name": "Mountain Climber", "category": "core", "muscle_groups": ["core", "shoulders"]},
    # Cardio
    {"name": "Running", "category": "cardio", "muscle_groups": ["legs", "cardio"]},
    {"name": "Cycling", "category": "cardio", "muscle_groups": ["legs", "cardio"]},
    {"name": "Rowing Machine", "category": "cardio", "muscle_groups": ["back", "legs", "cardio"]},
    {"name": "Jump Rope", "category": "cardio", "muscle_groups": ["calves", "cardio"]},
    {"name": "Stair Climber", "category": "cardio", "muscle_groups": ["legs", "cardio"]},
    {"name": "Burpee", "category": "cardio", "muscle_groups": ["full body", "cardio"]},
    {"name": "Swimming", "category": "cardio", "muscle_groups": ["full body", "cardio"]},
    {"name": "Elliptical", "category": "cardio", "muscle_groups": ["legs", "cardio"]},
    # Flexibility
    {"name": "Hamstring Stretch", "category": "flexibility", "muscle_groups": ["hamstrings"]},
    {"name": "Hip Flexor Stretch", "category": "flexibility", "muscle_groups": ["hip flexors"]},
    {"name": "Shoulder Stretch", "category": "flexibility", "muscle_groups": ["shoulders"]},
    {"name": "Cat-Cow", "category": "flexibility", "muscle_groups": ["spine", "core"]},
    {"name": "Downward Dog", "category": "flexibility", "muscle_groups": ["hamstrings", "shoulders"]},
    {"name": "Pigeon Pose", "category": "flexibility", "muscle_groups": ["glutes", "hips"]},
]


def seed_exercises() -> None:
    db = SessionLocal()
    try:
        repo = ExerciseRepository(db)
        if repo.count_defaults() > 0:
            return
        for item in EXERCISES:
            db.add(
                Exercise(
                    name=item["name"],
                    category=item["category"],
                    muscle_groups=item["muscle_groups"],
                    instructions=item.get("instructions"),
                    is_default=True,
                )
            )
        db.commit()
        print(f"Seeded {len(EXERCISES)} exercises")
    finally:
        db.close()


if __name__ == "__main__":
    from app.core.database import Base, engine

    Base.metadata.create_all(bind=engine)
    seed_exercises()
