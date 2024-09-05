import lexical
import sintacticals
import sys
import pprint
import requests
#import f_of_data_text
   
#Funciona para leer fichero
def read_file(file_path):
    with open (file_path, 'r') as file:
        return file.readlines()  # Devolver líneas en vez de texto completo
        #return file.read()

# Función para enviar las instrucciones al servicio REST (NUEVO)
def enviar_error_a_servicio(instruccion):
    url = "http://localhost:5000/procesar_error"  # Servicio REST en localhost
    headers = {'Content-Type': 'application/json'}
    data = {"mensaje_error": instruccion}

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json().get("respuesta")
        else:
            return f"Error en el servicio REST: {response.status_code}"
    except Exception as e:
        return f"Error al enviar al servicio REST: {str(e)}"

#Funcion main    
def main (file_path):
    # Leer archivo ensamblador (NUEVO)
    instrucciones = read_file(file_path)

    #f_of_data_text.initialize_active()
    #input_text = read_file (file_path)
    input_text = ''.join(instrucciones)  # Unir las líneas para el análisis (NUEVO)
    ret = sintacticals.sintactical (input_text)
    pprint.pprint(ret)

    # Verificar cada instrucción con el modelo LLM (NUEVO)
    for idx, instruccion in enumerate(instrucciones):
        instrucion = instruccion.strip()
        print(f"\nVerificando instrucción en línea {idx + 1}: {instrucion}")
        #Envia instruccion al servicio rest
        resultado = enviar_error_a_servicio(instrucion)
        #print(f"Resultado del modelo: {resultado}")

        if instrucion != resultado:
            print(f" La instrucción '{instrucion}' es incorrecta.")
            print(f" Se sugiere: '{resultado}'")
    
#main
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print ("Usage: python3 script.py file.s")
    else:
        main (sys.argv[1])
    #main (input_text)
