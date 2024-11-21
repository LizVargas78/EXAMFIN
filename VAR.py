import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

def calcular_var(etf_symbols, periodos=["1mo", "3mo", "6mo", "1y", "3y", "5y", "10y"], nivel_confianza=0.95):
    """
    Calcula el Valor en Riesgo (VaR) para cada ETF seleccionado como porcentaje de pérdida máxima estimada.
    """
    resultados_var = []
    Z = abs(np.percentile(np.random.normal(0, 1, 1000000), (1 - nivel_confianza) * 100))  # Valor crítico de Z

    for etf in etf_symbols:
        data_periodos = {}
        for periodo in periodos:
            # Descargar datos históricos del ETF
            if periodo == "3y":
                end_date = datetime.now()
                start_date = end_date - timedelta(days=3 * 365)
                data = yf.Ticker(etf).history(start=start_date, end=end_date)
            else:
                data = yf.Ticker(etf).history(period=periodo)

            if data.empty:
                data_periodos[periodo] = {"VaR": None}
                continue

            # Calcular retornos diarios
            retornos_diarios = data['Close'].pct_change().dropna()

            # Calcular desviación estándar de los retornos diarios
            desviacion_diaria = retornos_diarios.std()

            # Ajustar desviación estándar para el período seleccionado
            dias_periodo = {"1mo": 21, "3mo": 63, "6mo": 126, "1y": 252, "3y": 756, "5y": 1260, "10y": 2520}
            desviacion_periodo = desviacion_diaria * np.sqrt(dias_periodo.get(periodo, 252))

            # Calcular el VaR
            var_periodo = Z * desviacion_periodo  # Escala al nivel de confianza
            data_periodos[periodo] = {"VaR": round(var_periodo * 100, 2)}  # Convertir a porcentaje

        resultados_var.append({etf: data_periodos})

    return resultados_var
