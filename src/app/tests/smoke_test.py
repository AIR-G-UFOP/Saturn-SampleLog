"""
This is a simple smoke test to verify that the database can be initialised and that the expected tables are present.
It does not test any specific functionality of the application, but it can help catch basic issues with database
connectivity or schema setup.
"""


from sqlalchemy import inspect
from src.app.db import init_db, engine


def run_smoke_test():
    try:
        print("Running smoke test: Initializing the database and checking for expected tables...")
        init_db()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        expected_tables = ['users', 'samples', 'analyses', 'reductions']
        for table in expected_tables:
            if table not in tables:
                print(f"Smoke test failed: Table '{table}' not found in the database.")
                return
        print("Smoke test passed: All expected tables are present in the database.")
    except Exception as e:
        print(f"Smoke test failed with an exception: {e}")


if __name__ == "__main__":
    run_smoke_test()
