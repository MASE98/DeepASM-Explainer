import lexical

class Context:
    def __init__(self, asm_t):
        self.asm_t = asm_t #Para el texto que analiza
        self.t = 0 #Indice actual en el texto
        self.line = 1 #Para la linea actual del texto
        self.tokens = [] #Para listar los tokens encontrados
        self.token_types = [] #Para diferenciar los tipos de tokens
        self.comments = [] #Comentarios encontrados
        self.newlines = [] #Para el salto de linea
        self.i = 0 #Indice actual en la lista de tokens
        self.error = "" #Para mensaje de error

#
# Syntax
#

def sintactical_debug(input_text):
    #Initialize the context with the input text
    context = Context(input_text)

    #Function to process all tokens in the text
    tokens = []
    while not lexical.creasm_is_end_of_file(context):
        context = lexical.asm_next_token(context)
        token = lexical.asm_get_token(context)
        token_type = lexical.asm_get_token_type(context)
        tokens.append((token, token_type))
        context.i += 1

    #Print the tokens
    for token, token_type in tokens:
        print(f"Token: '{token}', Type: '{token_type}'")

#Funcion para procesar data
def sintactical_data (context,ret):
    print ("Entrando por sintactical_data..." +str(context.t) +"" +str(len(context.asm_t)) +"" +lexical.asm_get_token(context))
    while context.t < len (context.asm_t) and lexical.asm_get_token(context) != ".text":
        token = lexical.asm_get_token (context)
        token_type = lexical.asm_get_token_type (context)
        print ("1...." +token)
        ret.append ({"type":token_type, "value":token})
        print ("Primero: " +str(context.t))
        
        context = lexical.asm_next_token(context)
    return ret #hay que devolver un array de objetos

#Funcion para procesar texto
def sintactical_text (context, ret):
    while context.t < len (context.asm_t) and lexical.asm_get_token(context) != ".data":
        token = lexical.asm_get_token(context)
        token_type = lexical.asm_get_token_type (context)
        ret.append({"type": token_type, "value": token})
        print ("Primero: " +str(context.t))
        
        context = lexical.asm_next_token(context)    
    return ret #hay que devolver un array de objetos

#Funcion para analizar el sintactical de datos y texto
def sintactical (input_text):
    #Initialize the context with the input text
    context = Context (input_text)
    #context.t = 0
    ret = []
    context = lexical.asm_next_token(context)
    
    #Tokenizar el input_text    
    while not lexical.creasm_is_end_of_file(context):
        
        token = lexical.asm_get_token(context)
        print("probando...." +" " +str(token))
        if token == ".data":          
           sintactical_data (context, ret)
        else:
           sintactical_text (context, ret)
           
    return ret #hay que devolver un array de objetos
