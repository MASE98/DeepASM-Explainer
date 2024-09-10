# Detección y corrección de errores en ensamblador con modelo T5


## Tabla de Contenidos
1. [Resumen del Proyecto](#resumen-del-proyecto)
2. [Requisitos](#requisitos)
3. [Instalación](#instalación)

## Resumen del Proyecto
El modelo T5 analiza instrucciones de RISC-V y proporcionar una sugerencia sobre los errores. El modelo está integrado con un servicio REST para su uso eficiente.
Incluye:
- Un servicio REST que procesa instrucciones ensambladoras y devuelve correcciones si se detectan errores.
- Un modelo T5 preentrenado que ha sido adaptado para manejar instrucciones de RISC-V.

## Requisitos

Requisitos previos para su ejecucion:
- Python 3.8 o superior
- TensorFlow 
- Flask (para la API REST)
- Soporte para GPU (opcional pero es recomendado para entrenar más rápida el modelo)
- Las siguientes librerías de Python:
  - `transformers`
  - `torch` o `tensorflow`
  - `flask`
  - `requests`

## Instalación
1. Clona este repositorio:
    ```bash
    git clone https://github.com/MASE98/ASMCompiler/tree/main/T5_model.git
    ```
2. Navega al directorio del proyecto y descarga el modelo T5 entrenado:
    ```bash
    cd T5_model
    ```

    ```bash
    cd t5_trained_model
    ```
3. Instala las dependencias requeridas de Python:
    ```bash
    pip install -r requirements.txt
    ```