import subprocess
import json
import uuid

class SpannerClient:
    """Handles unified database access for licenses and telemetry in Google Cloud Spanner."""
    
    def __init__(self, instance="erdos-sieve-spanner", database="sieve-db"):
        self.instance = instance
        self.database = database

    def execute_sql(self, sql_query: str) -> list:
        """Helper to run arbitrary SQL query on Spanner using gcloud."""
        cmd = f'gcloud spanner databases execute-sql {self.database} --instance={self.instance} --sql="{sql_query}" --format=json'
        try:
            res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, check=True)
            if not res.stdout.strip():
                return []
            return json.loads(res.stdout)
        except subprocess.CalledProcessError as e:
            print(f"[Spanner Client Error] {e.stderr}")
            return []

    def get_license(self, license_key: str) -> dict:
        """Query license details by key."""
        query = f"SELECT * FROM Licenses WHERE LicenseKey = '{license_key}'"
        rows = self.execute_sql(query)
        if not rows:
            return None
        # Map row response list to dictionary format
        row = rows[0]
        return {
            "LicenseKey": row[0],
            "LicenseType": row[1],
            "Status": row[2],
            "AccumulatedRequests": int(row[3]),
            "MaxRequests": int(row[4]) if row[4] else None
        }

    def create_license(self, license_key: str, license_type: str, max_requests=None) -> bool:
        """Insert a new Gumroad or Stripe customer license."""
        max_req_val = max_requests if max_requests else "NULL"
        query = (
            f"INSERT INTO Licenses (LicenseKey, LicenseType, Status, AccumulatedRequests, MaxRequests) "
            f"VALUES ('{license_key}', '{license_type}', 'active', 0, {max_req_val})"
        )
        self.execute_sql(query)
        return True

    def increment_usage(self, license_key: str) -> bool:
        """Atomic usage tracking increment for metered APIs."""
        query = f"UPDATE Licenses SET AccumulatedRequests = AccumulatedRequests + 1 WHERE LicenseKey = '{license_key}'"
        self.execute_sql(query)
        return True

    def log_telemetry(self, event_name: str, details: dict):
        """Append API invocation events to TelemetryEvents table."""
        event_id = str(uuid.uuid4())
        details_str = json.dumps(details).replace('"', '\\"')
        query = (
            f"INSERT INTO TelemetryEvents (EventId, Timestamp, EventName, Details) "
            f"VALUES ('{event_id}', PENDING_COMMIT_TIMESTAMP(), '{event_name}', '{details_str}')"
        )
        self.execute_sql(query)
