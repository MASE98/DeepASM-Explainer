import lexical
import sintacticals
import sys
import pprint
#import f_of_data_text
   
#Funciona para leer fichero
def read_file(file_path):
    with open (file_path, 'r') as file:
        return file.read()

#Funcion main    
def main (file_path):
    #f_of_data_text.initialize_active()
    input_text = read_file (file_path)
    ret = sintacticals.sintactical (input_text)
    pprint.pprint(ret)
    
#main
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print ("Usage: python3 script.py file.s")
    else:
        main (sys.argv[1])
    #main (input_text)
