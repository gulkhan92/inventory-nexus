from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import Base, SessionLocal, engine
from app.models import domain  # noqa: F401
from app.services.seed import seed_database


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        result = seed_database(db)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
