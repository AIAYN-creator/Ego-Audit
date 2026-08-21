# sandbox-01: imagen minima para ejecutar estrategia(datos) -> señales.
# Sin conexion a internet en build time mas alla de instalar estas dos librerias;
# en runtime el contenedor se lanza con --network none (ver sandbox-02).
FROM python:3.12-slim

RUN useradd --create-home --uid 1000 --shell /usr/sbin/nologin sandbox \
    && pip install --no-cache-dir pandas numpy \
    && rm -rf /root/.cache

USER sandbox
WORKDIR /work

ENTRYPOINT ["python"]
