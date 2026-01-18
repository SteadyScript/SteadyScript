from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pen_color: str = "red"
    debug: bool = True
    log_level: str = "info"
    ws_heartbeat_interval: int = 30
    stability_window_size: int = 30
    jitter_threshold_low: float = 5.0
    jitter_threshold_high: float = 15.0

    class Config:
        env_file = ".env"


settings = Settings()

