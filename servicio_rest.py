from flask import Flask, request, jsonify
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

app = Flask(__name__)

# Cargar el modelo T5-small
model_name = '/home/marco/TFM/Memoria/Modelo_T5_LLM/t5_trained_model'
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

@app.route('/procesar_error', methods=['POST'])
def procesar_error():
    try:
        # Obtener datos del error enviados en el request
        datos = request.json
        texto_error = datos.get("mensaje_error", "")

        if not texto_error:
            return jsonify({"error": "No se proporcionó ningún mensaje de error"}), 400

        # Tokenizar el input y generar la respuesta usando el modelo
        inputs = tokenizer.encode(texto_error, return_tensors="pt")
        outputs = model.generate(inputs, max_length=100)
        respuesta = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return jsonify({"respuesta": respuesta}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
