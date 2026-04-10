from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Alpaca
    alpaca_api_key: str = ""
    alpaca_secret_key: str = ""
    alpaca_paper: bool = True

    # Claude API
    anthropic_api_key: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/alpha_trader"

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Risk parameters
    max_risk_per_trade: float = 0.02
    max_daily_loss: float = 0.03
    max_portfolio_heat: float = 0.06
    max_drawdown: float = 0.10
    max_sector_exposure: float = 0.25

    # Agent settings
    analysis_interval_minutes: int = 15
    max_watchlist_size: int = 50
    min_signal_threshold: int = 40
    min_rr_ratio: float = 2.0
    max_consecutive_losses: int = 3

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
