# -ASM-Compiler
Este proyecto implementa un compilador para ensamblador RISC-V que utiliza un modelo T5 para la detección y sugerencia de errores en el código. El compilador analiza instrucciones en ensamblador y proporciona una retroalimentación para corregir errores sintácticos. El compilador está diseñado para funcionar con la arquitectura RISC-V y ofrece una integracion mediante un servicio REST.

## Tabla de Contenido

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
  - [Ejecución Local](#ejecución-local)
  - [Uso del Servicio REST](#uso-del-servicio-rest)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Ejemplo](#ejemplo)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

## Requisitos

- Python 3.8 o superior
- Bibliotecas necesarias instalar mendiante `requirements.txt`):
  - `transformers`
  - `torch`
  - `flask`
  - Otras dependencias indicadas en `requirements.txt`

## Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/MASE98/ASMCompiler.git
   cd ASMCompiler

1. **Instalación de dependencia:**
   ```bash
   pip install -r requirements.txt