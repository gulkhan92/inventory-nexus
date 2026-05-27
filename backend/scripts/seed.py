from app.db.session import SessionLocal
from app.services.seed import seed_database


def main() -> None:
    db = SessionLocal()
    try:
        result = seed_database(db)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
