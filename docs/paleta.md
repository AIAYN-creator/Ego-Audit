# Paleta de Ego Audit

Definida siguiendo la skill de dataviz del autor: color al final del proceso, validado con `scripts/validate_palette.js`, nunca a ojo. Base: los 3 primeros slots de la paleta de referencia (los únicos que validan *todos los pares*, no solo los adyacentes, en ambos modos — ver `references/palette.md` de la skill).

## Validado

```
node scripts/validate_palette.js "#2a78d6,#eb6834,#1baf7a" --mode light --pairs all
node scripts/validate_palette.js "#3987e5,#d95926,#199e70" --mode dark --pairs all
```

- **Light**: todo PASS. WARN de contraste en aqua (2.74:1, bajo 3:1) — mitigado porque el aqua nunca lleva texto encima ni carga significado solo por color: el reporte y el README siempre acompañan el gráfico con la tabla de valores.
- **Dark**: todo PASS, sin warnings.

## Roles del gráfico (desglose bruto → neto vs. benchmark)

| Serie | Rol | Light | Dark |
|---|---|---|---|
| `bruto` | "parece sólido" — la ilusión | azul `#2a78d6` | `#3987e5` |
| `tras_comisiones` | primer aviso, todavía no alarma | aqua `#1baf7a` | `#199e70` |
| `neto` | la cifra que importa de verdad | naranja `#eb6834` | `#d95926` |
| `buy_and_hold` | el árbitro aburrido, no compite por atención | gris neutro (baseline/axis) `#c3c2b7` | `#383835` |

`buy_and_hold` a propósito **no** es un 4º color categórico: es la referencia, no un competidor por atención — gris neutro, convención estándar para líneas de benchmark.

## Identidad de marca (logo, README, no el gráfico)

| Rol | Hex | Uso |
|---|---|---|
| Primario | `#0b0b0b` (tinta primaria) | wordmark, texto de marca — serio, "informe de auditoría", no azul SaaS genérico |
| Secundario | `#2a78d6` (mismo azul del gráfico) | coherencia visual entre marca y producto |
| Acento ("lo mordaz") | `#d03b3b` (status-critical de la skill) | uso puntual y deliberadamente escaso — el logo, un detalle del README. Nunca en el gráfico (ahí ya significa otra cosa) ni en texto de cuerpo |

## Reutilizado tal cual de la skill (sin cambios, no hacía falta reinventarlo)

- Superficies: light `#fcfcfb` / dark `#1a1a19`.
- Tinta primaria/secundaria/muted, gridlines, baseline — tabla completa en `references/palette.md` de la skill.
- Tipografía: sans del sistema (`system-ui, -apple-system, "Segoe UI", sans-serif`) — coherente con una herramienta dev, no hace falta una fuente de marca custom.

## Qué NO se resuelve aquí

Aplicar esto al `reporte.py` (que hoy usa los colores por defecto de matplotlib) y al README es [[estetica-03-aplicar-identidad]], no esta card. El logo en sí es [[estetica-02-logo]].
