# app.py
import streamlit as st
import asyncio
import threading
from main import main
from modules import data_layer, processing_layer

def run_bot():
    asyncio.run(main())

st.title("Trading Bot Interface")
st.write("Configura y ejecuta el bot de trading.")

if st.button("Iniciar Bot"):
    st.write("Iniciando bot...")
    # Ejecutar el bot en un hilo aparte para que la UI no se bloquee.
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()