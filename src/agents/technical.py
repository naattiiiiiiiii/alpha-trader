import pandas as pd
import pandas_ta as ta

from src.agents.base import BaseAgent, AgentResult

MIN_BARS = 50


class TechnicalAgent(BaseAgent):
    name = "technical"

    def analyze(self, df: pd.DataFrame) -> AgentResult:
        if len(df) < MIN_BARS:
            return AgentResult(score=0, indicators={}, reasoning="Insufficient data")

        indicators = self._compute_indicators(df)
        score = self._compute_score(indicators)
        return AgentResult(score=score, indicators=indicators)

    def _compute_indicators(self, df: pd.DataFrame) -> dict:
        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        # Trend
        ema_9 = ta.ema(close, length=9).iloc[-1]
        ema_21 = ta.ema(close, length=21).iloc[-1]
        ema_50 = ta.ema(close, length=50).iloc[-1]
        macd_df = ta.macd(close)
        macd_val = macd_df.iloc[-1, 0]  # MACD line
        macd_signal = macd_df.iloc[-1, 1]  # Signal line
        macd_hist = macd_df.iloc[-1, 2]  # Histogram
        adx_df = ta.adx(high, low, close)
        adx_val = adx_df.iloc[-1, 0]  # ADX value

        # Momentum
        rsi = ta.rsi(close, length=14).iloc[-1]
        stoch_rsi = ta.stochrsi(close)
        stoch_k = stoch_rsi.iloc[-1, 0] if stoch_rsi is not None else 50.0
        willr = ta.willr(high, low, close).iloc[-1]

        # Volatility
        bbands = ta.bbands(close)
        bb_upper = bbands.iloc[-1, 0]
        bb_lower = bbands.iloc[-1, 2]
        atr = ta.atr(high, low, close, length=14).iloc[-1]

        # Volume
        obv = ta.obv(close, volume).iloc[-1]
        obv_prev = ta.obv(close, volume).iloc[-5]

        current_price = close.iloc[-1]

        return {
            "price": current_price,
            "ema_9": ema_9,
            "ema_21": ema_21,
            "ema_50": ema_50,
            "macd": macd_val,
            "macd_signal": macd_signal,
            "macd_hist": macd_hist,
            "adx": adx_val,
            "rsi": rsi,
            "stoch_k": stoch_k,
            "willr": willr,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "atr": atr,
            "obv": obv,
            "obv_trend": "up" if obv > obv_prev else "down",
        }

    def _compute_score(self, ind: dict) -> float:
        score = 0.0
        price = ind["price"]

        # Trend signals (weight: 35)
        if ind["ema_9"] > ind["ema_21"] > ind["ema_50"]:
            score += 20  # Strong uptrend alignment
        elif ind["ema_9"] < ind["ema_21"] < ind["ema_50"]:
            score -= 20  # Strong downtrend alignment

        if ind["macd_hist"] > 0:
            score += 10
        else:
            score -= 10

        if ind["adx"] > 25:  # Strong trend
            score += 5 if ind["ema_9"] > ind["ema_21"] else -5

        # Momentum signals (weight: 35)
        if ind["rsi"] < 30:
            score += 15  # Oversold — buy signal
        elif ind["rsi"] > 70:
            score -= 15  # Overbought — sell signal
        elif ind["rsi"] < 45:
            score += 5
        elif ind["rsi"] > 55:
            score -= 5

        if ind["stoch_k"] < 20:
            score += 10
        elif ind["stoch_k"] > 80:
            score -= 10

        if ind["willr"] < -80:
            score += 10  # Oversold
        elif ind["willr"] > -20:
            score -= 10  # Overbought

        # Volatility signals (weight: 15)
        if price < ind["bb_lower"]:
            score += 15  # Below lower band — potential bounce
        elif price > ind["bb_upper"]:
            score -= 15  # Above upper band — potential pullback

        # Volume signals (weight: 15)
        if ind["obv_trend"] == "up":
            score += 10 if score > 0 else 5  # Volume confirms direction
        else:
            score -= 10 if score < 0 else 5

        return max(-100, min(100, score))
