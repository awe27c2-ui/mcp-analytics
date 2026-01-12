import duckdb
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-analytics")
DB_PATH = "analytics.duckdb"

CATALOG = {
    "subscriptions": {
        "description": "Subscription lifecycle table with churn flag and plan tier.",
        "columns": [
            {"name": "user_id", "type": "BIGINT", "description": "Unique user identifier"},
            {"name": "plan", "type": "VARCHAR", "description": "Subscription plan tier"},
            {"name": "start_date", "type": "DATE", "description": "Subscription start date"},
            {"name": "end_date", "type": "DATE", "description": "End date if churned; NULL otherwise"},
            {"name": "churned", "type": "BOOLEAN", "description": "Whether the user churned"},
        ],
        "example_questions": [
            "What is churn rate by plan?",
            "How many active subscribers are there by plan?"
        ],
        "example_sql": [
            "SELECT plan, AVG(CASE WHEN churned THEN 1 ELSE 0 END) AS churn_rate FROM subscriptions GROUP BY plan",
            "SELECT plan, COUNT(*) AS active_subs FROM subscriptions WHERE churned = FALSE GROUP BY plan"
        ],
    },
    "events": {
        "description": "Event stream table capturing user device events over time.",
        "columns": [
            {"name": "event_ts", "type": "TIMESTAMP", "description": "Event timestamp"},
            {"name": "user_id", "type": "BIGINT", "description": "User identifier"},
            {"name": "device_type", "type": "VARCHAR", "description": "Device type"},
            {"name": "event_type", "type": "VARCHAR", "description": "Type of event"},
        ],
        "example_questions": [
            "What are the top event types by week?",
            "Which device types generate the most motion events?"
        ],
        "example_sql": [
            "SELECT event_type, COUNT(*) AS events FROM events GROUP BY 1 ORDER BY 2 DESC",
            "SELECT device_type, COUNT(*) AS motion_events FROM events WHERE event_type='motion' GROUP BY 1 ORDER BY 2 DESC"
        ],
    }
}

@mcp.tool()
def debug_catalog_keys() -> dict:
    return {"keys": list(CATALOG.keys())}


def _connect():
    return duckdb.connect(DB_PATH, read_only=True)

def _is_safe_select(sql: str) -> bool:
    s = sql.strip().lower()
    # single-statement SELECT only
    return s.startswith("select") and (";" not in s[:-1])

def _enforce_limit(sql: str, default_limit: int = 200) -> str:
    s = sql.strip().rstrip(";")
    if " limit " in s.lower():
        return s
    return f"{s} LIMIT {default_limit}"

@mcp.tool()
def list_datasets() -> dict:
    """List available datasets."""
    return {
        "datasets": [
            {"name": name, "description": meta["description"]}
            for name, meta in CATALOG.items()
        ]
    }

@mcp.tool()
def describe_dataset(name: str) -> dict:
    """Describe a dataset: schema, description, example questions and SQL."""
    meta = CATALOG.get(name)
    if not meta:
        return {"error": f"Unknown dataset: {name}", "available": list(CATALOG.keys())}
    return {"name": name, **meta}

@mcp.tool()
def run_query(sql: str) -> dict:
    """Execute a safe SELECT query against DuckDB and return results."""
    if not _is_safe_select(sql):
        return {"error": "Only single SELECT statements are allowed."}

    sql = _enforce_limit(sql)

    con = _connect()
    try:
        cur = con.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        return {"sql": sql, "columns": cols, "rows": rows}
    finally:
        con.close()

if __name__ == "__main__":
    mcp.run()
