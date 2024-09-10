# -T5-Model

# T5-Based Assembler Error Detection and Correction

This repository contains a project that leverages the T5 model to analyze RISC-V assembly language and provide feedback on potential errors. The system is integrated with a REST service for efficient and scalable use. 

## Table of Contents
1. [Project Overview](#project-overview)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
    - [REST API](#rest-api)
    - [Model Training](#model-training)
5. [Model Details](#model-details)
6. [Contributing](#contributing)
7. [License](#license)

## Project Overview

This project implements a compiler for assembly language using the T5 model. The system focuses on detecting and correcting errors in RISC-V assembly instructions. It includes:
- A REST service that processes assembly instructions and returns corrections if errors are detected.
- A pre-trained T5 model that has been adapted to handle RISC-V instructions.
- An interface for testing and validating assembly code.

The system also provides extensibility for additional instruction sets and operand variations.

## Requirements

To run this project, you will need the following:
- Python 3.8 or higher
- TensorFlow or PyTorch (depending on your T5 model implementation)
- Flask (for the REST API)
- GPU support (optional but recommended for faster model inference)
- The following Python libraries:
  - `transformers`
  - `torch` or `tensorflow`
  - `flask`
  - `requests`

### Optional Dependencies
- `gdbgui` for debugging assembly code

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/T5_assembler_detection.git
    ```
2. Navigate to the project directory:
    ```bash
    cd T5_assembler_detection
    ```
3. Install the required Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Set up the environment for the T5 model by downloading the pre-trained weights or training a new model.

## Usage

### REST API
To start the REST API server, run:
```bash
python app.py
