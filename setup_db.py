import duckdb
import pandas as pd
from datetime import datetime, timedelta
import random

DB_PATH = "analytics.duckdb"

def main():
    con = duckdb.connect(DB_PATH)

    # Create a simple subscriptions dataset (Ring-ish business analytics)
    rows = []
    plans = ["basic", "plus", "pro"]
    today = datetime.utcnow().date()

    for user_id in range(1, 2001):
        plan = random.choice(plans)
        start = today - timedelta(days=random.randint(30, 365))
        churned = random.random() < 0.18
        end = (start + timedelta(days=random.randint(7, 240))) if churned else None
        rows.append((user_id, plan, start.isoformat(), end.isoformat() if end else None, churned))

    df = pd.DataFrame(rows, columns=["user_id", "plan", "start_date", "end_date", "churned"])

    con.execute("DROP TABLE IF EXISTS subscriptions")
    con.execute("""
        CREATE TABLE subscriptions (
          user_id BIGINT,
          plan VARCHAR,
          start_date DATE,
          end_date DATE,
          churned BOOLEAN
        )
    """)

    con.register("df", df)
    con.execute("INSERT INTO subscriptions SELECT * FROM df")


    print(f"Created {DB_PATH} with table: subscriptions (rows={len(df)})")

        # Create an events dataset
    event_types = ["motion", "doorbell_press", "camera_live_view", "alarm_triggered"]
    device_types = ["stick_up_cam", "doorbell", "floodlight_cam"]
    rows = []
    now = datetime.utcnow()

    for _ in range(20000):
        user_id = random.randint(1, 2000)
        device_type = random.choice(device_types)
        event_type = random.choice(event_types)
        ts = now - timedelta(minutes=random.randint(0, 60 * 24 * 30))  # last 30 days
        rows.append((ts.isoformat(timespec="seconds"), user_id, device_type, event_type))

    df_events = pd.DataFrame(rows, columns=["event_ts", "user_id", "device_type", "event_type"])

    con.execute("DROP TABLE IF EXISTS events")
    con.execute("""
        CREATE TABLE events (
          event_ts TIMESTAMP,
          user_id BIGINT,
          device_type VARCHAR,
          event_type VARCHAR
        )
    """)
    con.register("df_events", df_events)
    con.execute("INSERT INTO events SELECT * FROM df_events")
    con.close()


if __name__ == "__main__":
    main()
