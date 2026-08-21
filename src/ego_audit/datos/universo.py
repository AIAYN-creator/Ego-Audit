"""datos-02: universo de tickers para v1."""

BENCHMARK = "SPY"
"""ETF que replica el S&P 500 -- se usa el ETF, no el indice ^GSPC: el indice
no es directamente invertible y no incluye dividendos, SPY si. Una estrategia
buy-and-hold real compraria SPY, no el indice -- para que la comparacion sea
honesta tiene que ser contra algo que de verdad se podria haber comprado."""

TICKERS_ADICIONALES = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
"""Puñado de tickers populares y liquidos con historial largo, pensados para
que los ejemplos del README y las pruebas manuales tengan sentido para el
publico objetivo (perfil tech/dev). No es una recomendacion de inversion,
son simplemente nombres conocidos para demostrar la herramienta."""

UNIVERSO = [BENCHMARK] + TICKERS_ADICIONALES
