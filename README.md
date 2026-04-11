# Alpha Trader

Agente autonomo de trading de acciones USA con gestion de riesgo profesional de 5 niveles, analisis multi-agente y dashboard en tiempo real.

**Coste total: $0/mes** — usa LLMs locales (Ollama) y paper trading de Alpaca.

## Que hace

Alpha Trader analiza acciones automaticamente combinando 3 tipos de analisis, toma decisiones de inversion y ejecuta ordenes con proteccion automatica (stop-loss + take-profit).

```
Noticias reales          Indicadores tecnicos       Datos fundamentales
(Alpaca News API)        (RSI, MACD, EMA, etc.)     (P/E, ROE, FCF, etc.)
        |                        |                          |
        v                        v                          v
  Agente Sentimiento      Agente Tecnico           Agente Fundamental
  (LLM: llama3.2)        (Python puro)             (Python puro)
        |                        |                          |
        +------------------------+---------------------------+
                                 |
                                 v
                        Agente Decisor (LLM: llama3)
                        "BUY AAPL, confidence 0.82"
                                 |
                                 v
                        Agente de Riesgo (Python puro)
                        Pre-trade checks, position sizing
                                 |
                                 v
                        Alpaca API -> Bracket Order
                        (entry + stop-loss + take-profit)
```

## Gestion de riesgo (5 niveles)

| Nivel | Regla | Detalle |
|---|---|---|
| 1. Por operacion | Max 2% de riesgo | Stop-loss obligatorio en cada trade |
| 2. Diario | Max 3% perdida/dia | Pausa automatica si se alcanza |
| 3. Portfolio | Max 6% heat total | Suma de riesgo abierto limitada |
| 4. Circuit breaker | Progresivo | 5%: reduce 50%, 8%: reduce 75%, 10%: cierra todo |
| 5. Pre-trade | Checks automaticos | Buying power, sector, correlacion, mercado abierto |

## Stack

| Componente | Tecnologia | Coste |
|---|---|---|
| Trading | Alpaca Paper Trading | $0 |
| LLM Sentimiento | Ollama + llama3.2 (local) | $0 |
| LLM Decisor | Ollama + llama3 (local) | $0 |
| Analisis tecnico | pandas-ta (13 indicadores) | $0 |
| Analisis fundamental | yfinance (10 metricas) | $0 |
| Noticias | Alpaca News API (tiempo real) | $0 |
| Base de datos | PostgreSQL | $0 |
| Dashboard | FastAPI + HTMX | $0 |
| Notificaciones | Telegram Bot | $0 |

Compatible con cualquier API OpenAI-compatible: Ollama, ChatGPT, Grok, Gemini, vLLM, etc. Solo cambia `LLM_BASE_URL` en `.env`.

## Quick Start

### Requisitos previos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes)
- [Ollama](https://ollama.com) (LLM local)
- [Docker](https://docker.com) (para PostgreSQL)
- Cuenta gratuita en [Alpaca Markets](https://alpaca.markets) (Trading API, paper trading)

### Instalacion

```bash
# 1. Clonar
git clone https://github.com/naattiiiiiiiii/alpha-trader.git
cd alpha-trader

# 2. Instalar modelos de Ollama
ollama pull llama3
ollama pull llama3.2

# 3. Configurar
cp .env.example .env
# Editar .env con tus API keys de Alpaca

# 4. Levantar base de datos
docker compose up db -d

# 5. Instalar dependencias
uv sync

# 6. Crear tablas
uv run python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.models.database import Base
from src.models import Trade, Signal, RiskEvent, PortfolioSnapshot, AgentConfig
async def init():
    engine = create_async_engine('postgresql+asyncpg://postgres:postgres@localhost:5433/alpha_trader')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
asyncio.run(init())
"

# 7. Ejecutar
uv run python -m src.main
```

### Dashboard

Abre `http://localhost:8000` para ver:
- Estado del agente y P&L en tiempo real
- Posiciones abiertas con boton de cierre manual
- Historial de trades con estadisticas (win rate, profit factor)
- Senales de los 3 agentes con scores
- Parametros de riesgo editables en vivo
- Logs en tiempo real

## Configuracion (.env)

```env
# Alpaca (paper trading)
ALPACA_API_KEY=tu_key
ALPACA_SECRET_KEY=tu_secret
ALPACA_PAPER=true

# LLM (Ollama por defecto, o cualquier API OpenAI-compatible)
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL_FAST=llama3.2    # Sentimiento (rapido)
LLM_MODEL_SMART=llama3     # Decisiones (mas capaz)

# Risk (ajustables desde el dashboard)
MAX_RISK_PER_TRADE=0.02    # 2% max por operacion
MAX_DAILY_LOSS=0.03        # 3% max perdida diaria
MAX_PORTFOLIO_HEAT=0.06    # 6% max riesgo total abierto
MAX_DRAWDOWN=0.10          # 10% max drawdown -> cierra todo
MAX_SECTOR_EXPOSURE=0.25   # 25% max en un sector
```

## Tests

```bash
uv sync --all-extras
uv run pytest tests/ -v
# 66 tests passing
```

## Arquitectura

```
alpha-trader/
├── src/
│   ├── agents/           # 5 agentes: tecnico, fundamental, sentimiento, riesgo, decisor
│   ├── core/             # Motor de ejecucion, scheduler, portfolio manager, maintenance
│   ├── api/              # Dashboard FastAPI + HTMX (6 paginas)
│   ├── models/           # SQLAlchemy models (trades, signals, risk events, snapshots)
│   ├── notifications/    # Telegram bot
│   └── utils/            # Screening, indicadores
├── tests/                # 66 tests
├── Dockerfile            # Deploy con Docker
├── docker-compose.yml    # App + PostgreSQL
└── railway.toml          # Deploy en Railway (cloud)
```

## Deploy en cloud (Railway)

Para ejecutar 24/7 sin tener el ordenador encendido:

1. Conecta el repo en [Railway](https://railway.app)
2. Agrega un addon de PostgreSQL
3. Configura las variables de entorno
4. Railway despliega automaticamente en cada push a main

Coste estimado: $5-10/mes (hosting) + coste del LLM en cloud si no usas Ollama.

## Licencia

MIT
