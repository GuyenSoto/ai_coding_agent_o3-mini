from typing import Optional, Dict, Any
import streamlit as st
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
import os
import re
from PIL import Image
from io import BytesIO
import base64

def initialize_session_state() -> None:
    if 'openai_key' not in st.session_state:
        st.session_state.openai_key = ''
    if 'gemini_key' not in st.session_state:
        st.session_state.gemini_key = ''
    if 'e2b_key' not in st.session_state:
        st.session_state.e2b_key = ''
    # Se inhabilita el sandbox asignándole None
    st.session_state.sandbox = None
    # Agregamos estados para los scripts a comparar
    if 'script1' not in st.session_state:
        st.session_state.script1 = ''
    if 'script2' not in st.session_state:
        st.session_state.script2 = ''

def setup_sidebar() -> None:
    with st.sidebar:
        st.title("API Configuration")
        st.session_state.openai_key = st.text_input("OpenAI API Key", 
                                                   value=st.session_state.openai_key,
                                                   type="password")
        st.session_state.gemini_key = st.text_input("Gemini API Key", 
                                                   value=st.session_state.gemini_key,
                                                   type="password")
        st.session_state.e2b_key = st.text_input("E2B API Key",
                                                value=st.session_state.e2b_key,
                                                type="password")

def create_agents() -> tuple[Agent, Agent, Agent, Agent]:
    # Se mantiene el agente de visión como "dummy"
    vision_agent = Agent(
        model=OpenAIChat(
            id="o3-mini", 
            api_key=st.session_state.openai_key,
            system_prompt="Imagenes deshabilitadas. No se procesa entrada visual."
        ),
        markdown=True
    )

    coding_agent = Agent(
        model=OpenAIChat(
            id="o3-mini", 
            api_key=st.session_state.openai_key,
            system_prompt="""You are an expert Python programmer. You will receive coding problems similar to LeetCode questions, 
            which may include problem statements, sample inputs, and examples. Your task is to:
            1. Analyze the problem carefully and Optimally with best possible time and space complexities.
            2. Write clean, efficient Python code to solve it
            3. Include proper documentation and type hints
            Please always respond using markdown code blocks.          
            Please ensure your code is complete and handles edge cases appropriately."""
        ),
        markdown=True
    )
    
    execution_agent = Agent(
        model=OpenAIChat(
            id="o3-mini",
            api_key=st.session_state.openai_key,
            system_prompt="""You are an expert at executing Python code in sandbox environments.
            Your task is to:
            1. Take the provided Python code
            2. Execute it in the e2b sandbox
            3. Format and explain the results clearly
            4. Handle any execution errors gracefully
            Always ensure proper error handling and clear output formatting."""
        ),
        markdown=True
    )
    
    # Nuevo agente para comparar scripts
    comparison_agent = Agent(
        model=OpenAIChat(
            id="o3-mini",
            api_key=st.session_state.openai_key,
            system_prompt="""You are an expert Python code analyzer. Your task is to compare two Python scripts and provide a detailed analysis of their similarities and differences.

            For each comparison, you should:
            1. Identify structural differences (functions, classes, imports)
            2. Analyze algorithmic approaches and efficiency
            3. Highlight code style and best practices
            4. Suggest improvements
            
            IMPORTANT: Always format your response with proper markdown, using code blocks for any code snippets.
            ALWAYS begin your response with a code block showing key differences.
            Example:
            ```python
            # Script 1 differences:
            # - Uses recursion
            # - O(n^2) time complexity
            
            # Script 2 differences:
            # - Uses iteration
            # - O(n) time complexity
            ```
            
            Then provide your detailed analysis."""
        ),
        markdown=True
    )
    
    return vision_agent, coding_agent, execution_agent, comparison_agent

def extract_code_blocks(response_content: str) -> list:
    """
    Extrae bloques de código Python de una respuesta en markdown.
    """
    code_blocks = []
    # Patrón para encontrar bloques de código Python
    pattern = r"```python\s+(.*?)\s+```"
    matches = re.findall(pattern, response_content, re.DOTALL)
    
    # También busca bloques sin especificar el lenguaje
    if not matches:
        pattern = r"```\s+(.*?)\s+```"
        matches = re.findall(pattern, response_content, re.DOTALL)
    
    return matches

def main() -> None:
    st.title("O3-Mini Coding Agent")
    
    # Inicializa el estado de la sesión y configura la barra lateral
    initialize_session_state()
    setup_sidebar()
    
    # Tabs para diferentes funcionalidades
    tab1, tab2 = st.tabs(["Soluciones de Código", "Comparar Scripts"])
    
    # Verificar que se hayan ingresado todas las claves API requeridas
    if not st.session_state.openai_key:
        st.warning("Por favor, ingresa al menos la clave API de OpenAI en la barra lateral.")
        return
    
    vision_agent, coding_agent, execution_agent, comparison_agent = create_agents()
    
    with tab1:
        st.header("Generador de Soluciones de Código")
        
        # Configuración de entrada: se permite imagen o texto
        uploaded_image = st.file_uploader(
            "Sube una imagen de tu problema de programación (opcional)",
            type=['png', 'jpg', 'jpeg']
        )
        
        if uploaded_image:
            st.image(uploaded_image, caption="Imagen Subida", use_container_width=True)
        
        user_query = st.text_area(
            "O escribe tu problema de programación aquí:",
            placeholder="Ejemplo: Escribe una función para encontrar la suma de dos números. Incluye casos de entrada/salida de ejemplo.",
            height=100
        )
        
        # Botón para procesar la consulta
        if st.button("Generar Solución", type="primary"):
            if uploaded_image and not user_query:
                # Se desactiva el procesamiento de imágenes
                st.error("El procesamiento de imágenes está deshabilitado. Por favor, utiliza la entrada de texto.")
                return
            elif user_query and not uploaded_image:
                # Procesamiento directo de texto
                with st.spinner("Generando solución..."):
                    response = coding_agent.run(user_query)
            elif user_query and uploaded_image:
                st.error("Por favor, utiliza ya sea la carga de imagen O la entrada de texto, no ambas.")
                return
            else:
                st.warning("Por favor, proporciona ya sea una imagen o una descripción de texto de tu problema de programación.")
                return
            
            # Mostrar la solución
            if 'response' in locals():
                st.divider()
                st.subheader("💻 Solución")
                
                # Mostrar la respuesta completa en markdown
                st.markdown(response.content)
                
                # Extraer código de la respuesta en markdown
                code_blocks = extract_code_blocks(response.content)
                
                if code_blocks:
                    st.divider()
                    st.subheader("🚀 Resultados de Ejecución")
                    st.markdown("La ejecución de código está deshabilitada porque la funcionalidad de sandbox está inactiva.")
                else:
                    st.info("No se encontró ningún bloque de código en la respuesta.")
    
    with tab2:
        st.header("Comparador de Scripts Python")
        
        # Opciones para ingresar scripts
        input_method = st.radio("Método de entrada", ["Áreas de texto", "Archivos .py"])
        
        if input_method == "Áreas de texto":
            col1, col2 = st.columns(2)
            
            with col1:
                script1 = st.text_area("Script 1", height=300, value=st.session_state.script1)
                st.session_state.script1 = script1
            
            with col2:
                script2 = st.text_area("Script 2", height=300, value=st.session_state.script2)
                st.session_state.script2 = script2
        
        else:  # Archivos .py
            col1, col2 = st.columns(2)
            
            with col1:
                file1 = st.file_uploader("Sube el primer script", type=["py"])
                if file1:
                    script1 = file1.read().decode("utf-8")
                    st.session_state.script1 = script1
                    st.code(script1, language="python")
            
            with col2:
                file2 = st.file_uploader("Sube el segundo script", type=["py"])
                if file2:
                    script2 = file2.read().decode("utf-8")
                    st.session_state.script2 = script2
                    st.code(script2, language="python")
        
        if st.button("Comparar Scripts", type="primary"):
            if not st.session_state.script1 or not st.session_state.script2:
                st.error("Por favor, proporciona ambos scripts para la comparación.")
                return
            
            with st.spinner("Analizando scripts..."):
                # Construimos un prompt que asegure que la respuesta contenga bloques de código
                prompt = f"""
                Compara los siguientes dos scripts de Python e identifica las diferencias y similitudes clave:
                
                Script 1:
                ```python
                {st.session_state.script1}
                ```
                
                Script 2:
                ```python
                {st.session_state.script2}
                ```
                
                Por favor, comienza tu respuesta con un bloque de código que resuma las principales diferencias.
                """
                
                response = comparison_agent.run(prompt)
            
            st.divider()
            st.subheader("🔍 Análisis de Comparación")
            
            # Mostrar la respuesta completa
            st.markdown(response.content)
            
            # Verificar si hay bloques de código en la respuesta
            code_blocks = extract_code_blocks(response.content)
            if not code_blocks:
                st.warning("No se encontraron bloques de código en la respuesta. La comparación puede no estar correctamente formateada.")

if __name__ == "__main__":
    main()