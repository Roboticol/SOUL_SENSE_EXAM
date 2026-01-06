
from app.db import get_connection


def load_questions(
    age: int | str | None = None,
    db_path: str | None = None
):
    """
    Load questions from DB.
    Supports backward-compatible call:
        load_questions(db_path)
    And new usage:
        load_questions(age=25)
        load_questions(age=25, db_path=...)
    """

    # ---------------- BACKWARD COMPAT ----------------
    if isinstance(age, str) and db_path is None:
        db_path = age
        age = None

    conn = get_connection(db_path)
    cursor = conn.cursor()

    if age is None:
        cursor.execute("""
            SELECT id, question_text
            FROM question_bank
            WHERE is_active = 1
            ORDER BY id
        """)
    else:
        cursor.execute("""
            SELECT id, question_text
            FROM question_bank
            WHERE is_active = 1
              AND min_age <= ?
              AND max_age >= ?
            ORDER BY id
        """, (age, age))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise RuntimeError("No questions found in database")

    return rows

