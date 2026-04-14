# Alpha Trader

Agente autonomo de trading de acciones USA con gestion de riesgo profesional de 5 niveles, analisis multi-agente y dashboard en tiempo real.

**Coste total: $0/mes** — usa LLMs gratuitos en la nube (Cerebras) y paper trading de Alpaca.

**Live demo**: [alpha-trader-production-9277.up.railway.app](https://alpha-trader-production-9277.up.railway.app)

## Que hace

Alpha Trader analiza acciones automaticamente combinando 3 tipos de analisis, toma decisiones de inversion y ejecuta ordenes con proteccion automatica (stop-loss + take-profit).

```
Noticias reales          Indicadores tecnicos       Datos fundamentales
(Alpaca News API)        (RSI, MACD, EMA, etc.)     (P/E, ROE, FCF, etc.)
        |                        |                          |
        v                        v                          v
  Agente Sentimiento      Agente Tecnico           Agente Fundamental
  (LLM: llama3.1-8b)     (Python puro)             (Python puro)
        |                        |                          |
        +------------------------+---------------------------+
                                 |
                                 v
                        Agente Decisor (LLM: llama3.1-8b)
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

## Funcionamiento en produccion

El agente esta desplegado en Railway y funciona 24/7 de forma autonoma:

- **Ciclo cada 15 minutos**: analiza 20 acciones del S&P 500 (AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, etc.)
- **Analisis tecnico**: 13 indicadores (RSI, MACD, EMA, Bollinger, ATR, volumen, etc.)
- **Analisis fundamental**: 10 metricas (P/E, ROE, FCF yield, deuda, margen, etc.)
- **Analisis de sentimiento**: noticias en tiempo real de Alpaca procesadas por LLM
- **Decisiones**: LLM evalua los 3 scores y decide BUY/SELL/HOLD con nivel de confianza
- **Ejecucion**: ordenes bracket automaticas con stop-loss y take-profit

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
| LLM | Cerebras (llama3.1-8b, cloud) | $0 |
| Analisis tecnico | pandas-ta (13 indicadores) | $0 |
| Analisis fundamental | yfinance (10 metricas) | $0 |
| Noticias | Alpaca News API (tiempo real) | $0 |
| Dashboard | FastAPI + HTMX | $0 |
| Hosting | Railway (24/7) | $0-5/mes |
| Notificaciones | Telegram Bot | $0 |

Compatible con cualquier API OpenAI-compatible: Cerebras, Groq, Ollama, ChatGPT, Gemini, etc. Solo cambia `LLM_BASE_URL` en `.env`.

## Quick Start

### Opcion 1: Local

```bash
# 1. Clonar
git clone https://github.com/naattiiiiiiiii/alpha-trader.git
cd alpha-trader

# 2. Configurar
cp .env.example .env
# Editar .env con tus API keys de Alpaca y LLM

# 3. Base de datos
docker compose up db -d

# 4. Instalar y ejecutar
uv sync
uv run python -m src.main
```

### Opcion 2: Deploy en Railway (24/7)

```bash
# 1. Instalar Railway CLI
brew install railway

# 2. Login y crear proyecto
railway login
railway init --name alpha-trader

# 3. Configurar variables de entorno
railway variables set \
  ALPACA_API_KEY=tu_key \
  ALPACA_SECRET_KEY=tu_secret \
  ALPACA_PAPER=true \
  LLM_BASE_URL=https://api.cerebras.ai/v1 \
  LLM_API_KEY=tu_cerebras_key \
  LLM_MODEL_FAST=llama3.1-8b \
  LLM_MODEL_SMART=llama3.1-8b

# 4. Deploy
railway up
```

### Dashboard

Abre `http://localhost:8000` (local) o la URL de Railway para ver:
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

# LLM (cualquier API OpenAI-compatible)
LLM_BASE_URL=https://api.cerebras.ai/v1
LLM_API_KEY=tu_key
LLM_MODEL_FAST=llama3.1-8b    # Sentimiento (rapido)
LLM_MODEL_SMART=llama3.1-8b   # Decisiones (mas capaz)

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
└── railway.toml          # Deploy en Railway (cloud, 24/7)
```

## Licencia

MIT
