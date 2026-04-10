# Alpha Trader — Spec de Diseno

**Fecha:** 2026-04-10
**Autor:** Natalia Cuadrado
**Repo:** github.com/naattiiiiii/alpha-trader
**Estado:** Aprobado

---

## 1. Vision General

Agente de inversiones automatizado que opera acciones USA en Alpaca Markets con gestion de riesgo profesional de 5 niveles. Arquitectura hibrida: logica programatica para calculos y ejecucion, LLM (Claude) solo para analisis de sentimiento y decisiones estrategicas.

**Objetivo principal:** Operar de forma autonoma 24/7 en paper trading ($100K simulados), con sistema de riesgo que garantice no perder mas del 2% por operacion y un maximo de 10% de drawdown total.

---

## 2. Decisiones de Diseno

| Aspecto | Decision | Razon |
|---|---|---|
| Activos | Acciones USA (todo tipo) | Mercado mas liquido, bien soportado por Alpaca |
| Horizonte | Adaptativo (day/swing/position) | El agente decide segun condiciones de mercado |
| Capital | Paper trading $100K | Validacion sin riesgo real |
| Infraestructura | Servicio autonomo 24/7 | Maximo aprovechamiento de oportunidades |
| Stack | Full Python | Estandar de la industria financiera, mejores librerias |
| Autonomia | Autonoma con limites + supervision | Opera dentro de parametros, humano supervisa via dashboard |
| Analisis | Multi-agente (5 agentes especializados) | Simula equipo de trading institucional |
| Enfoque LLM | Hibrido: Python puro + LLM estrategico | 90% mas barato, determinista donde importa |

---

## 3. Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   ALPHA TRADER                       │
│              (Servicio Python 24/7)                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ Agente   │ │ Agente   │ │ Agente           │   │
│  │ Tecnico  │ │ Fundamen.│ │ Sentimiento      │   │
│  │ (Python) │ │ (Python) │ │ (Claude Haiku)   │   │
│  └────┬─────┘ └────┬─────┘ └────────┬─────────┘   │
│       │             │                │              │
│       ▼             ▼                ▼              │
│  ┌──────────────────────────────────────────────┐  │
│  │         AGENTE DECISOR (Claude Sonnet)       │  │
│  │   Pondera senales + contexto macro           │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                               │
│                     ▼                               │
│  ┌──────────────────────────────────────────────┐  │
│  │         AGENTE DE RIESGO (Python puro)       │  │
│  │   5 niveles / Pre-trade checks / Stops       │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                               │
│                     ▼                               │
│  ┌──────────────────────────────────────────────┐  │
│  │         MOTOR DE EJECUCION                   │  │
│  │   Alpaca API (ordenes, posiciones, cuenta)   │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌────────────┐  ┌─────────────┐ │
│  │ Scheduler   │  │ WebSocket  │  │ PostgreSQL  │ │
│  │ (APScheduler│  │ (Market    │  │ + SQLAlch.  │ │
│  │  )          │  │  Stream)   │  │             │ │
│  └─────────────┘  └────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐  │
│  │         DASHBOARD (FastAPI + HTMX)           │  │
│  │   Estado, posiciones, logs, controles        │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Flujo principal

1. **Scheduler** dispara ciclos de analisis (cada 1min para day trading, cada 1h para swing, cada dia para position)
2. Los 3 agentes de analisis se ejecutan en paralelo y generan senales con score de confianza (-100 a +100)
3. El **Decisor** (Claude Sonnet) pondera las senales, considera el contexto macro y emite una decision: BUY/SELL/HOLD con simbolo, cantidad y razon
4. El **Agente de Riesgo** valida la decision contra los 5 niveles. Si no pasa, se bloquea
5. El **Motor de Ejecucion** envia la orden a Alpaca con bracket order (take-profit + stop-loss automaticos)
6. Todo se loguea en PostgreSQL y se muestra en el dashboard

### Optimizacion de tokens

- El Decisor solo se invoca cuando al menos 2 de los 3 agentes dan senal significativa (score > |40|)
- El Agente de Sentimiento cachea resultados si no hay noticias nuevas
- Se usa Haiku para sentimiento (~$0.01/ciclo) y Sonnet para decisor (~$0.04/ciclo)
- Coste estimado: $20-40/mes

---

## 4. Los 5 Agentes

### 4.1 Agente Tecnico (Python puro)

**Libreria:** pandas-ta

**Indicadores:**
- Tendencia: EMA 9/21/50/200, MACD, ADX
- Momentum: RSI (14), Stochastic RSI, Williams %R
- Volatilidad: Bollinger Bands, ATR (14), Keltner Channels
- Volumen: OBV, VWAP, Volume Profile
- Patrones: Soporte/resistencia dinamicos

**Output:** Score -100 a +100
- +60 a +100: senal fuerte de compra
- +20 a +60: senal moderada de compra
- -20 a +20: neutral
- -60 a -20: senal moderada de venta
- -100 a -60: senal fuerte de venta

### 4.2 Agente Fundamental (Python puro)

**Fuente:** yfinance (gratis)

**Metricas:**
- Valoracion: P/E, P/B, PEG ratio, EV/EBITDA
- Rentabilidad: ROE, ROA, margen neto, margen operativo
- Salud financiera: Debt/Equity, Current Ratio, Free Cash Flow
- Crecimiento: Revenue growth YoY, EPS growth
- Comparativa: Ranking vs sector/industria

**Output:** Score -100 a +100

### 4.3 Agente de Sentimiento (Claude Haiku)

**Fuentes:**
- Noticias de Alpaca (streaming gratuito)
- Web search para eventos macro (Fed, earnings, regulacion)
- Corporate actions de Alpaca (dividendos, splits)

**Proceso:**
1. Recopila noticias/eventos de las ultimas horas
2. Envia a Haiku: "Evalua el impacto en el precio de [SYMBOL]"
3. Haiku devuelve: score (-100 a +100), resumen de 1 linea, nivel de urgencia

**Cache:** Si no hay noticias nuevas, reutiliza ultimo analisis.

### 4.4 Agente de Riesgo (Python puro)

**5 niveles de control:**

**Nivel 1 — Por operacion:**
- Maximo 1-2% del portfolio en riesgo por trade
- Stop-loss obligatorio en CADA operacion (ATR-based)
- Ratio riesgo/recompensa minimo 1:2

**Nivel 2 — Diario:**
- Maximo 3% de perdida diaria — pausa automatica
- Maximo 3 operaciones perdedoras consecutivas — pausa y re-evaluacion

**Nivel 3 — Portfolio total:**
- Maximo 6% de portfolio heat (suma de riesgo abierto)
- Drawdown maximo 10% desde el pico
- Maximo 20-25% de exposicion por sector

**Nivel 4 — Circuit breaker progresivo:**
- Drawdown 5%: reduce tamano de posiciones al 50%
- Drawdown 8%: reduce al 25%
- Drawdown 10%: cierra todo, modo solo-observacion

**Nivel 5 — Pre-trade checks:**
- Buying power suficiente
- Portfolio heat no excedido
- Mercado abierto
- No estamos en circuit breaker
- Correlacion con posiciones existentes aceptable

### 4.5 Agente Decisor (Claude Sonnet)

**Input:**
```json
{
    "symbol": "AAPL",
    "technical_score": 72,
    "fundamental_score": 45,
    "sentiment_score": 85,
    "current_positions": [],
    "portfolio_state": {},
    "market_regime": "bullish",
    "risk_budget_available": 1.8
}
```

**Output:**
```json
{
    "action": "BUY",
    "symbol": "AAPL",
    "position_size_pct": 1.5,
    "entry_strategy": "limit",
    "take_profit_pct": 4.0,
    "stop_loss_pct": 2.0,
    "reasoning": "Confluencia de senales...",
    "time_horizon": "swing",
    "confidence": 0.82
}
```

**Solo se invoca cuando** al menos 2 de los 3 agentes dan senal significativa (score > |40|).

---

## 5. Dashboard (FastAPI + HTMX)

### Paginas

- **/ (Overview):** Estado del agente, P&L, equity curve, posiciones abiertas, ultimas decisiones
- **/positions:** Posiciones abiertas con P&L en tiempo real, boton cierre manual
- **/history:** Historial de trades, filtros, estadisticas (win rate, profit factor), export CSV
- **/signals:** Senales de los 3 agentes, scores por simbolo, reasoning del decisor
- **/settings:** Parametros de riesgo editables en vivo, watchlist, frecuencia, pausar/reanudar, modo paper/live
- **/logs:** Log en tiempo real, filtros por nivel (INFO, WARNING, TRADE, RISK_BLOCK)

Actualizacion en tiempo real via Server-Sent Events (SSE).

---

## 6. Notificaciones (Telegram Bot)

| Evento | Prioridad | Contenido |
|---|---|---|
| Trade ejecutado | Normal | Simbolo, qty, precio, razon |
| Trade cerrado | Normal | P&L absoluto y porcentual |
| Stop-loss activado | Alta | P&L de la perdida |
| Circuit breaker | Urgente | Nivel activado, accion tomada |
| Limite diario | Urgente | Perdida del dia, agente pausado |
| Resumen diario | Baja | Trades, wins/losses, P&L total |

---

## 7. Persistencia (PostgreSQL)

### Tablas

- **trades:** id, symbol, side, qty, entry_price, exit_price, entry_time, exit_time, status, stop_loss, take_profit, pnl, pnl_pct, alpaca_order_id, time_horizon
- **signals:** id, symbol, timestamp, technical_score, fundamental_score, sentiment_score, decision, confidence, reasoning
- **risk_events:** id, timestamp, event_type, details (JSON), level, action_taken
- **portfolio_snapshots:** id, timestamp, equity, cash, buying_power, total_pnl, daily_pnl, drawdown_pct, positions_count, portfolio_heat
- **agent_config:** key, value, updated_at

---

## 8. Estructura de Archivos

```
alpha-trader/
├── README.md
├── pyproject.toml
├── .env.example
├── alembic/
│   └── versions/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── agents/
│   │   ├── base.py
│   │   ├── technical.py
│   │   ├── fundamental.py
│   │   ├── sentiment.py
│   │   ├── risk.py
│   │   └── decision.py
│   ├── core/
│   │   ├── executor.py
│   │   ├── scheduler.py
│   │   ├── streamer.py
│   │   └── portfolio.py
│   ├── models/
│   │   ├── database.py
│   │   ├── trade.py
│   │   ├── signal.py
│   │   ├── risk_event.py
│   │   ├── snapshot.py
│   │   └── config.py
│   ├── api/
│   │   ├── app.py
│   │   ├── routes/
│   │   │   ├── dashboard.py
│   │   │   ├── positions.py
│   │   │   ├── history.py
│   │   │   ├── settings.py
│   │   │   └── signals.py
│   │   ├── templates/
│   │   └── static/
│   ├── notifications/
│   │   └── telegram.py
│   └── utils/
│       ├── indicators.py
│       ├── screening.py
│       └── helpers.py
├── tests/
│   ├── test_agents/
│   ├── test_core/
│   ├── test_risk/
│   └── conftest.py
├── Dockerfile
└── docker-compose.yml
```

---

## 9. Stack Tecnico

| Componente | Libreria |
|---|---|
| Runtime | Python 3.12+ |
| Package manager | uv |
| API Alpaca | alpaca-py |
| API Framework | FastAPI |
| Templates | Jinja2 + HTMX |
| LLM | anthropic (Claude API) |
| Analisis tecnico | pandas-ta |
| Datos fundamentales | yfinance |
| BD | PostgreSQL 16 + SQLAlchemy 2.0 |
| Migraciones | Alembic |
| Scheduler | APScheduler 4.x |
| Notificaciones | python-telegram-bot |
| Config | pydantic-settings |
| Deploy | Docker Compose |
| Hosting | Railway o Fly.io (~$5-10/mes) |

---

## 10. Variables de Entorno

```
ALPACA_API_KEY=
ALPACA_SECRET_KEY=
ALPACA_PAPER=true
ANTHROPIC_API_KEY=
DATABASE_URL=postgresql://...
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
MAX_RISK_PER_TRADE=0.02
MAX_DAILY_LOSS=0.03
MAX_PORTFOLIO_HEAT=0.06
MAX_DRAWDOWN=0.10
MAX_SECTOR_EXPOSURE=0.25
```

---

## 11. Costes Estimados

| Concepto | Coste/mes |
|---|---|
| Claude API (Haiku + Sonnet) | $20-40 |
| Alpaca paper trading | $0 |
| Datos de mercado (IEX) | $0 |
| PostgreSQL (Docker local o free tier) | $0 |
| Hosting (Railway/Fly.io) | $5-10 |
| **Total** | **$25-50/mes** |

---

## 12. Screening de Acciones (Universo de Trading)

El agente no puede monitorizar las ~8,000 acciones de Alpaca. Necesita un filtro:

**Watchlist base (configurable desde dashboard):**
- El usuario define una lista inicial de simbolos a monitorizar (ej: 20-50 acciones)
- Defaults sugeridos: S&P 500 top 50 por volumen

**Screener automatico (ejecuta 1x/dia antes de apertura):**
- Filtra por: volumen medio diario > 1M, market cap > $1B, spread < 0.1%
- Detecta: gap ups/downs significativos, volumen inusual, earnings proximos
- Agrega candidatos temporales a la watchlist para analisis del dia

**Limite operativo:** Maximo 50 simbolos activos en watchlist para mantener costes de LLM controlados.

---

## 13. Fases de Implementacion (alto nivel)

1. **Fundamentos:** Proyecto base, config, BD, conexion Alpaca
2. **Agentes Python:** Tecnico + Fundamental + Riesgo
3. **Agentes LLM:** Sentimiento + Decisor
4. **Motor de ejecucion:** Ordenes bracket, trailing stops, ciclo completo
5. **Dashboard:** FastAPI + HTMX, todas las paginas
6. **Notificaciones:** Telegram bot
7. **Integracion y testing:** Tests del sistema de riesgo, paper trading continuo
8. **Deploy:** Docker Compose, hosting, CI/CD
