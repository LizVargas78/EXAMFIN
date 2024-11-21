import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from Calculo import calcular_rendimiento_riesgo
from VAR import calcular_var

# Configuración de estilo minimalista para seaborn
sns.set(style="whitegrid")
plt.rcParams.update({
    "axes.facecolor": "white",
    "axes.edgecolor": "#E5E5E5",
    "grid.color": "#E5E5E5",
    "axes.labelcolor": "#333333",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "font.size": 8,
    "axes.titlesize": 10,
    "axes.labelsize": 8,
    "legend.fontsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7
})

# Función para validar y ajustar los pesos de los instrumentos seleccionados
def asignar_pesos():
    seleccionados = st.session_state.get("seleccionados", [])
    if len(seleccionados) == 0:
        st.sidebar.warning("No se han seleccionado instrumentos financieros en la sección de Resumen.")
        return

    # Título de Asignación de Pesos
    st.sidebar.markdown("<h2 class='section-title'>Asignación de Pesos</h2>", unsafe_allow_html=True)

    total_peso = 0
    if len(seleccionados) == 1:
        st.sidebar.write(f"Asignación automática: 100% en {seleccionados[0]}")
        st.session_state[f"peso_{seleccionados[0]}"] = 100
    else:
        for instrumento in seleccionados:
            peso = st.sidebar.number_input(
                f"Porcentaje de inversión para {instrumento}", min_value=0, max_value=100, value=0, step=1
            )
            st.session_state[f"peso_{instrumento}"] = peso
            total_peso += peso

        if total_peso != 100:
            st.sidebar.error("La suma de los porcentajes debe ser exactamente 100%. Ajuste los valores.")
            return
        else:
            st.sidebar.success("Asignación de pesos completada con éxito.")

    # Título de Capital
    st.sidebar.markdown("<h2 class='section-title'>Capital</h2>", unsafe_allow_html=True)

    # Entrada de capital a invertir con un mínimo de $500,000
    capital_invertir = st.sidebar.number_input(
        "Ingrese la cantidad a invertir", min_value=500000, value=500000, step=10000, format="%d"
    )
    st.session_state["capital_invertir"] = capital_invertir

    # Selección de periodo
    st.sidebar.markdown("<h2 class='section-title'>Periodo</h2>", unsafe_allow_html=True)
    periodos = {
        "1 mes": "1mo",
        "3 meses": "3mo",
        "6 meses": "6mo",
        "1 año": "1y",
        "YTD": "ytd",
        "3 años": "3y",
        "5 años": "5y",
        "10 años": "10y"
    }
    periodo_seleccionado_nombre = st.sidebar.selectbox("Seleccione el periodo de inversión", list(periodos.keys()))
    st.session_state["periodo_seleccionado"] = periodos[periodo_seleccionado_nombre]

    # Confirmar cálculo
    if st.sidebar.button("Calcular"):
        st.sidebar.success("Cálculo realizado exitosamente con los parámetros seleccionados.")
        st.session_state["mostrar_resultados"] = True

# Código principal para la sección de Estadística
def estadistica():
    asignar_pesos()

    # Validar los estados necesarios
    seleccionados = st.session_state.get("seleccionados", [])
    periodo = st.session_state.get("periodo_seleccionado", None)
    capital = st.session_state.get("capital_invertir", None)
    calculo_realizado = st.session_state.get("mostrar_resultados", False)

    if not seleccionados:
        st.warning("Por favor, selecciona los ETFs en la sección 'Resumen'.")
        return

    if not periodo or not capital:
        st.warning("Por favor, completa la asignación de pesos, capital y periodo en el panel lateral.")
        return

    if not calculo_realizado:
        st.info("Haz clic en 'Calcular' después de completar todos los pasos para ver los resultados.")
        return

    # Si todo está completo, mostrar los resultados
    periodos_fijos = ["1mo", "3mo", "6mo", "1y", "ytd", "3y", "5y", "10y"]
    resultados = calcular_rendimiento_riesgo(seleccionados, periodos_fijos)

    # Convertir resultados a DataFrame y mostrar tabla
    data = []
    for resultado in resultados:
        for etf, valores in resultado.items():
            fila = {"ETF": etf}
            for periodo_key, metrics in valores.items():
                fila[f"Rendimiento {periodo_key.upper()}"] = metrics.get("rendimiento")
                fila[f"Riesgo {periodo_key.upper()}"] = metrics.get("riesgo")
            data.append(fila)

    resultados_df = pd.DataFrame(data)

    if not resultados_df.empty:
        # Formatear tablas de rendimiento y riesgo con porcentaje y dos decimales
        resultados_df_display = resultados_df.copy()
        for col in resultados_df_display.columns[1:]:
            resultados_df_display[col] = resultados_df_display[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "-")

        st.markdown("<h3 class='section-title'>Tabla de Rendimientos</h3>", unsafe_allow_html=True)
        columnas_rendimiento = [col for col in resultados_df_display.columns if "Rendimiento" in col]
        st.table(resultados_df_display[["ETF"] + columnas_rendimiento])

        st.markdown("<h3 class='section-title'>Tabla de Riesgos</h3>", unsafe_allow_html=True)
        columnas_riesgo = [col for col in resultados_df_display.columns if "Riesgo" in col]
        st.table(resultados_df_display[["ETF"] + columnas_riesgo])

        # Mostrar la tabla de Máxima Pérdida (VaR)
        resultados_var = calcular_var(seleccionados, periodos_fijos)
        data_var = []
        for resultado in resultados_var:
            for etf, valores in resultado.items():
                fila = {"ETF": etf}
                for periodo_key, metrics in valores.items():
                    fila[f"VaR {periodo_key.upper()}"] = metrics.get("VaR")
                data_var.append(fila)

        resultados_var_df = pd.DataFrame(data_var)

        # Formatear valores de VaR como porcentaje con dos decimales
        for col in resultados_var_df.columns[1:]:
            resultados_var_df[col] = resultados_var_df[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "-")

        st.markdown("<h3 class='section-title'>Tabla de Máxima Pérdida (VaR)</h3>", unsafe_allow_html=True)
        st.table(resultados_var_df)

        # Graficar Rendimiento y Riesgo
        resultados_long_df = resultados_df.melt(id_vars="ETF", var_name="Métrica", value_name="Valor")

        # Gráfico de rendimiento
        rendimiento_df = resultados_long_df[resultados_long_df["Métrica"].str.contains("Rendimiento")]
        plt.figure(figsize=(6, 3))
        sns.lineplot(data=rendimiento_df, x="Métrica", y="Valor", hue="ETF", marker="o", palette="Blues_r")
        plt.title("Evolución del Rendimiento por Periodo")
        plt.xlabel("Periodo")
        plt.ylabel("Rendimiento (%)")
        plt.xticks(rotation=45)
        st.pyplot(plt)

        # Gráfico de riesgo
        riesgo_df = resultados_long_df[resultados_long_df["Métrica"].str.contains("Riesgo")]
        plt.figure(figsize=(6, 3))
        sns.lineplot(data=riesgo_df, x="Métrica", y="Valor", hue="ETF", marker="o", palette="Reds_r")
        plt.title("Evolución del Riesgo por Periodo")
        plt.xlabel("Periodo")
        plt.ylabel("Riesgo (%)")
        plt.xticks(rotation=45)
        st.pyplot(plt)

        # NUEVA SECCIÓN: Tabla de Portafolio
        st.markdown("<h3 class='section-title'>Portafolio</h3>", unsafe_allow_html=True)

        # Validar que seleccionados está definido
        seleccionados = st.session_state.get("seleccionados", [])
        pesos = {etf: st.session_state.get(f"peso_{etf}", 0) / 100 for etf in seleccionados}  # Convertir a proporciones
        rendimiento_portafolio = 0
        capital_invertido = st.session_state.get("capital_invertir", 0)

        data_portafolio = {
            "ETF": [],
            "Peso (%)": [],
            "Rendimiento (%)": [],
            "Capital Asignado": []
        }

        for resultado in resultados:
            for etf, valores in resultado.items():
                rendimiento = valores.get(periodo, {}).get("rendimiento", 0) / 100  # Convertir a decimal
                peso = pesos.get(etf, 0)
                capital_asignado = peso * capital_invertido
                retorno_etf = capital_asignado * rendimiento

                # Sumar al rendimiento total del portafolio
                rendimiento_portafolio += retorno_etf

                # Añadir datos a la tabla con formato de dos decimales
                data_portafolio["ETF"].append(etf)
                data_portafolio["Peso (%)"].append(f"{peso * 100:.2f}")  # Formatear a dos decimales
                data_portafolio["Rendimiento (%)"].append(f"{rendimiento * 100:.2f}")  # Formatear a dos decimales
                data_portafolio["Capital Asignado"].append(f"{capital_asignado:,.2f}")  # Formatear a dos decimales

        # Mostrar tabla del portafolio
        df_portafolio = pd.DataFrame(data_portafolio)
        st.table(df_portafolio)

        # Mostrar el rendimiento total esperado
        st.markdown(f"**Retorno Total Esperado:** ${rendimiento_portafolio:,.2f}")
