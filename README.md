# -ASM-Compiler
Este proyecto implementa un compilador para ensamblador RISC-V que utiliza un modelo T5 para la detección y sugerencia de errores en el código. El compilador analiza instrucciones en ensamblador y proporciona una retroalimentación para corregir errores sintácticos. El compilador está diseñado para funcionar con la arquitectura RISC-V y ofrece una integracion mediante un servicio REST.

## Tabla de Contenido

- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
  - [Ejecución Local](#ejecución-local)
  - [Uso del Servicio REST](#uso-del-servicio-rest)
- [Ejemplo](#ejemplo)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)


## Estructura del Proyecto

- **main.py**: Archivo principal que ejecuta el compilador.
- **lexical.py**: Analizador léxico que tokeniza el código ensamblador.
- **sintacticals.py**: Analizador sintáctico que valida la estructura del código ensamblador.
- **datatypes.py**: Define los tipos de datos utilizados durante el análisis.
- **directives.py**: Directivas específicas de la arquitectura RISC-V.
- **servicio_rest.py**: Servicio REST que permite la integración del modelo T5 con el compilador.
- **T5_model/**: Carpeta que contiene el modelo T5 entrenado para la sugerencias de instrucciones.
- **text.s**: Ejemplo de código ensamblador utilizado para pruebas.

## Requisitos

- Python 3.8 o superior
- Bibliotecas necesarias instalar mendiante `requirements.txt`:
  - `transformers`
  - `torch`
  - `flask`
  
## Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/MASE98/ASMCompiler.git

   ```
   cd ASMCompiler
   
2. **Instalación de dependencia:**
   ```bash
   pip install -r requirements.txt

3. **Utilizar el modelo entrendo en T5_model:**
   ```bash
   cd T5_model

## USO

- Se comienza iniciando el servicio REST:

   ```bash
   python3 servicio_rest.py
   ```

- Luego se ejecutar el compilador localmente proporcionando un archivo ensamblador como entrada

   ```bash
   python3 main.py text.s

