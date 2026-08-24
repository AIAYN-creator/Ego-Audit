use pyo3::prelude::*;

/// Calcula la serie de valor de portfolio (base 1.0) a partir de precios de
/// cierre y una serie de posicion objetivo (fraccion de capital, 0.0-1.0),
/// alineadas por indice -- misma longitud, mismo orden que `precios`.
///
/// retorno_dia\[t\] = posiciones\[t-1\] * (precios\[t\] / precios\[t-1] - 1)
/// valor\[t\]      = valor\[t-1] * (1 + retorno_dia\[t\])
///
/// La posicion se aplica con UN DIA DE REZAGO (posiciones[t-1], no
/// posiciones[t]) a proposito: la senal calculada con el cierre del dia t
/// no se puede haber ejecutado antes de ese cierre -- aplicarla ese mismo
/// dia seria look-ahead bias, inflaria la rentabilidad de forma irreal.
/// Es la decision de correctitud mas importante de este motor.
#[pyfunction]
fn calcular_valor_portfolio(precios: Vec<f64>, posiciones: Vec<f64>) -> PyResult<Vec<f64>> {
    if precios.len() != posiciones.len() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "precios y posiciones deben tener la misma longitud",
        ));
    }
    if precios.is_empty() {
        return Ok(vec![]);
    }

    let mut valor = vec![1.0_f64; precios.len()];
    for t in 1..precios.len() {
        let retorno_precio = precios[t] / precios[t - 1] - 1.0;
        let retorno_dia = posiciones[t - 1] * retorno_precio;
        valor[t] = valor[t - 1] * (1.0 + retorno_dia);
    }
    Ok(valor)
}

#[pymodule]
fn ego_audit_engine(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calcular_valor_portfolio, m)?)?;
    Ok(())
}
