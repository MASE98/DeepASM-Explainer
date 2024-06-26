import lexical
import directives
import f_sintactical
import re

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

#********** IDIOMAS INTERNACIONALES **********
i18n = {
    'lang': {
        'en': "English",
        'es': "Español",
        'it': "L'italiano - Google-translate",
        'kr': "한국어 - Google-translate",
        'hi': "हिन्दी - Google-translate",
        'fr': "Français - Google-translate",
        'pt': "Português - Google-translate",
        'ja': "日本語 - Google-translate",
        'zh_cn': "汉语 - Thanks to shiptux@github",
        'ru': "русский язык - Google-translate",
        'sv': "Svenska - Google-translate",
        'de': "Deutsch - Google-translate"
    },
    'eltos': {
        'gui': {},
        'cfg': {},
        'examples': {},
        'states': {},
        'help': {},
        'dialogs': {},
        'compiler': {},
        'hw': {},
        'tutorial_welcome': {},
        'tutorial_simpleusage': {},
        'tour_intro': {}
    }
}

#********** FUNCIONES DE REGLAS INTERNACIONALES *********
def i18_getTagFor (component, key):
    try:
        crea_idiom = get_cfg ('cre_idiom')
    except KeyError:
        crea_idiom = 'en'

    translation = key + ''
    if key in i18n['eltos'].get(component, {}).get(crea_idiom,{}):
        translation = i18n['eltos'][component][crea_idiom][key]
    
    return translation

#********** CONFIGURACIONES *********
def get_cfg (field):
    WSCFG = {
        'crea_idiom': {'value': 'es'}
    }
    return WSCFG[field]['value']


#********** FUNCIONES PARA DATA **********
def creasm_new_objEl (b_elto):

    elto = {
        "comments": [],
        "labels": [],
        "track_source": [],
        "seg_name": '',
        "datatype": '',
        "byte_size": 0,
        "value": '0',
        "format": '',
        "endian": 'none',
        "binary": '',
        "firm_reference": None,
        "firm_reference_index": -1,
        "pending": []
    }

    if b_elto is not None:
        elto["seg_name"] = b_elto.get("seg_name", '')
        elto["datatype"] = b_elto.get("datatype", '')
        elto["byte_size"] = b_elto.get("byte_size", 0)
        elto["endian"] = b_elto.get("endian", 'none')

    return elto

def creasm_is_ValidTag(tag):
    tg = tag.strip() #eliminamos espacios en blancos
    if tg == "": #Se verifica si la cadena esta vacia
        return False
    #Verificamos si es un digito
    if tg [0].isdigit():

        #Se verifica que no comience con cero a menos que lo sea
        if len (tg) > 1 and tg [0] == '0':
            return False
        #verificacion de decimal
        if '.' in tg:
            return False
    #Verificacion de caracteres invalidos    
    myRegEx = re.compile (r'[^a-zA-Z,_\d]', re.IGNORECASE)
    return not myRegEx.search(tg)    

#********** CATCH DE SINTACTICAL DATA AND TEXT **********
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
           sintactical_data1 (context, ret)
        else:
           sintactical_text1 (context, ret)
           
    return ret #hay que devolver un array de objetos

#********** DATA **********
def sintactical_data (context, ret):
    possible_tag = ""
    possible_value = ""
    tag = ""
    acc_cmt = ""
    retr1 = None
    elto = None

    #.data
    #.text

    seg_name = lexical.asm_get_token(context)
    lexical.asm_get_token (context)

    elto = creasm_new_objEl (None)
    elto.seg_name = seg_name


    #bucle para leer token que no es un directiva (.text/.data y final de fichero)
    while (not directives.creasm_is_directive_segment(lexical.asm_get_token(context)) and not lexical.creasm_is_end_of_file(context)):

        #label1:
        #label2 : .double 

        acc_cmt = lexical.asm_get_comments(context)
        lexical.asm_reset_comments(context)


        # ** Detectar posible TAG **
        possible_tag = ""
        #NOT.text/.data y final de fichero
        while (not directives.creasm_is_directive_datatype(lexical.asm_get_token(context)) and not lexical.creasm_is_end_of_file(context)):

            #extrae y lo almacena en possible_tag
            possible_tag = lexical.asm_get_token(context)

            #Verifica etiqueta TAG
            if "TAG" != lexical.asm_get_token(context):
                if "" == possible_tag:
                    possible_tag = "EMPTY"                
                return lexical.asm_lang_error(context, i18_getTagFor ('compiler', 'NO TAG OR DIRECTIVE') + "'" + possible_tag + "'")
            
            #Elimina el ultimo caracter
            tag = possible_tag [:-1]

            #Verifica que TAG no sea una instruccion, que no se repita y que no tenga un formato invalido
            if not creasm_is_ValidTag(tag):
                return lexical.asm_lang_error(context, i18_getTagFor ('compiler', 'INVALID TAG FORMAT') + "'" + tag + "'")
            
            if context ['assembly'].get(tag):
                return lexical.asm_lang_error(context, i18_getTagFor('compilar', 'TAG OR INSTRUCTION') + "'" + tag + "'")
            
            if tag in ret['labels_asm']:
                return lexical.asm_langError(context, i18_getTagFor('compiler', 'REPEATED TAG') + "'" + tag + "'")
            
            elto ['labels'].append(tag)
            ret ['labels_asm'][tag] = 0

            #Si es .datatype y avanza al otro tag
            lexical.asm_next_token(context)
                
#
#********** SINTACTICO DE PRUEBA **********
#
# Syntax

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
def sintactical_data1 (context,ret):
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
def sintactical_text1 (context, ret):
    while context.t < len (context.asm_t) and lexical.asm_get_token(context) != ".data":
        token = lexical.asm_get_token(context)
        token_type = lexical.asm_get_token_type (context)
        ret.append({"type": token_type, "value": token})
        print ("Primero: " +str(context.t))
        
        context = lexical.asm_next_token(context)    
    return ret #hay que devolver un array de objetos