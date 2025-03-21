import sys, os

# Directorio raíz del proyecto (donde está AllinOne.py)
project_root = os.path.abspath(os.path.dirname(__file__))

# Ruta absoluta de la carpeta modules
modules_path = os.path.join(project_root, "modules")

# Eliminar todas las entradas que sean exactamente la carpeta modules
while modules_path in sys.path:
    sys.path.remove(modules_path)

# Si project_root no está ya en sys.path, lo insertamos al principio
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# (Opcional) Imprimir sys.path para verificar
# print("sys.path:", sys.path)




import streamlit as st
import threading
import asyncio
from main import main
# Importamos los módulos desde la carpeta "modules"
from modules import data_layer, processing_layer, analysis_layer, decision_layer, execution_layer
import sys
# st.write(sys.path)
# AllinOne.py

def run_bot():
    asyncio.run(main())

st.title("Trading Bot Interface")
st.write("Configura y ejecuta el bot de trading.")

# Menú en la barra lateral para seleccionar módulos a ejecutar
st.sidebar.header("Seleccionar módulos a ejecutar")
execute_data       = st.sidebar.checkbox("Data Layer", value=False)
execute_processing = st.sidebar.checkbox("Processing Layer", value=False)
execute_analysis   = st.sidebar.checkbox("Analysis Layer", value=False)
execute_decision   = st.sidebar.checkbox("Decision Layer", value=False)
execute_execution  = st.sidebar.checkbox("Execution Layer", value=False)

if st.sidebar.button("Ejecutar módulos seleccionados"):
    output = []
    if execute_data:
        try:
            result = data_layer.run_module()
            output.append("Data Layer: " + str(result))
        except Exception as e:
            output.append("Data Layer error: " + str(e))
    if execute_processing:
        try:
            result = processing_layer.run_module()
            output.append("Processing Layer: " + str(result))
        except Exception as e:
            output.append("Processing Layer error: " + str(e))
    if execute_analysis:
        try:
            result = analysis_layer.run_module()
            output.append("Analysis Layer: " + str(result))
        except Exception as e:
            output.append("Analysis Layer error: " + str(e))
    if execute_decision:
        try:
            result = decision_layer.run_module()
            output.append("Decision Layer: " + str(result))
        except Exception as e:
            output.append("Decision Layer error: " + str(e))
    if execute_execution:
        try:
            result = execution_layer.run_module()
            output.append("Execution Layer: " + str(result))
        except Exception as e:
            output.append("Execution Layer error: " + str(e))
    st.write("Resultados de la ejecución de módulos:")
    for line in output:
        st.write(line)

if st.button("Iniciar Bot completo"):
    st.write("Iniciando bot completo...")
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
