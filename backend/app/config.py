from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Campus Patrol API"
    database_url: str = "postgresql+psycopg://patrol:patrol@localhost:5432/patrol"
    # A rover counts as online if it reported within this many seconds.
    online_window_seconds: int = 30
    # When set, telemetry/event ingestion requires a matching X-Rover-Token header.
    ingest_token: str = ""
    seed_demo_data: bool = False


settings = Settings()
