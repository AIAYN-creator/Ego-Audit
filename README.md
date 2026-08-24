# Ego Audit

**El auditor de egos para bots de trading.**

Ego Audit audita estrategias de trading escritas en Python: las ejecuta en un sandbox aislado sobre datos históricos gratuitos, aplica walk-forward validation, y desglosa la rentabilidad bruta hasta neta (comisiones + slippage estimado) frente a un benchmark buy-and-hold.

No predice el mercado ni compite con él. Expone honestamente cuánto de la rentabilidad "de laboratorio" de una estrategia sobrevive al contacto con la realidad: overfitting, fricción de ejecución, validación fuera de muestra.

> Proyecto en desarrollo activo. Todavía no hay una versión instalable ni un ejemplo funcionando — ver Estado más abajo.

## Para quién es esto

Perfil tech/dev que construye (o quiere construir) bots de inversión en bolsa o cripto, y que sobrevalora los resultados de backtests ingenuos.

## Qué hace (v1.0.0)

1. **Input**: un script Python con una función `estrategia(datos) -> señales`.
2. **Datos**: histórico diario gratuito vía yfinance — S&P 500 como benchmark + un puñado de tickers populares. No intraday, no todo el mercado.
3. **Sandbox aislado**: contenedor Docker efímero, sin red saliente, límites estrictos de CPU/memoria/tiempo, filesystem read-only salvo el directorio de trabajo. Ejecuta código arbitrario de terceros, así que el aislamiento es la prioridad de diseño, no un detalle.
4. **Walk-forward validation**: ventanas deslizantes (ajuste en un periodo, validación en el periodo inmediatamente posterior) para separar rendimiento in-sample de out-of-sample.
5. **Output**: desglose bruto → menos comisiones → menos slippage estimado → neto, comparado contra buy-and-hold del S&P 500 en el mismo periodo.

## Qué NO hace (fuera de alcance en v1)

- Intraday o multi-asset amplio.
- Ejecutar órdenes reales — esto audita, no es un broker.
- Leaderboard social entre estrategias de distintos usuarios.
- Optimización automática de hiperparámetros (induciría el mismo overfitting que la herramienta existe para exponer).

## Estado

En desarrollo activo, por fases:

- [x] **Arquitectura decidida** — contrato de `estrategia()`, motor de contabilidad (Rust + PyO3), estructura del sandbox.
- [x] **Sandbox de ejecución aislada** — Docker con hardening (sin red saliente, límites de CPU/memoria, filesystem read-only, sin privilegios).
- [x] **Capa de datos** — descarga vía yfinance, universo de tickers, cache local, alineación de fechas entre tickers.
- [ ] **Walk-forward validation** — motor de ventanas deslizantes y motor de contabilidad (Rust) ya funcionando; falta cerrar la agregación final de resultados.
- [ ] **Modelo de comisiones y slippage.**
- [ ] **Output visual** — el desglose bruto → neto, la pieza de producto más importante.
- [ ] **CLI.**

Todavía no hay una versión instalable ni un ejemplo end-to-end funcionando.

## Licencia

MIT — ver [LICENSE](LICENSE).
