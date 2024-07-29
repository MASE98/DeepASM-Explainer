import lexical
import directives
import f_of_data_text
import datatypes
import re
import json

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
        self.assembly = {} #Para almacenar etiquetas y valores - Diccionario
        self.endian = 'little' #Valor predeterminado para endian
        self.register = {} #Diccionario que almacena los registros
        self.options = {'mandatory_comma': False}

#Constants
BYTE_LENGTH = 8 
WORD_BYTES  = 4 
WORD_LENGTH = WORD_BYTES * BYTE_LENGTH 
#COMENTAR CTRL + K + C // DESCOMENTAR CTRL + K + U  

#********** FUNCIONES PARA DATA **********
def creasm_new_objEl (b_elto):

    elto = {
        'comments': [],
        'labels': [],
        'track_source': [],
        'seg_name': '',
        'datatype': '',
        'byte_size': 0,
        'value': {
            'signature_size_arr': [], 
            'signature_size_str': '', 
            'instruction': '',
            'fields' : [],
            'signature_type_arr': []
        },
        'format': '',
        'endian': 'none',
        'binary': '',
        'assembly_reference': None,
        'assembly_reference_index': -1,
        'pending': []
    }

    if b_elto is not None:
        elto['seg_name'] = b_elto['seg_name']
        elto['datatype'] = b_elto['datatype']
        elto['byte_size'] = b_elto['byte_size']
        elto['endian'] = b_elto['endian']

    return elto

def creasm_eltoErro (context, elto, msg):
    lexical.asm_set_label_context(context, elto['associated_context'])
    return lexical.asm_lang_error(context, msg)

def creasm_is_ValidTag(tag):
    tg = tag.strip()
    if tg == "":
        return False

    # Check if the first character is a decimal digit
    ret = datatypes.is_decimal(tg[0])
    if ret['isDecimal'] == True:
        return False

    # Regular expression to check for invalid characters
    #my_reg_ex = re.compile(r'[^a-z,_\d]', re.IGNORECASE)
    #return not my_reg_ex.search(tg)
    return True #do to
   
#********** DATA **********
def sintactical_data (context, ret):
    possible_tag = ""
    possible_value = ""
    tag = ""
    acc_cmt = ""
    ret1 = None
    elto = None

    #.data
    #.text - label1: .directive "value"
    print(f"Entrando en sintactical_data con: {context.t}")
    seg_name = lexical.asm_get_token(context)
    print(f"Segmento encontrado: {seg_name}")
    lexical.asm_next_token(context)
    print(f"Índice después de avanzar desde segmento: {context.t}")

    elto = creasm_new_objEl (None)
    elto ["seg_name"] = seg_name

    #.data - .data
    #.text - label: .directive "value"

    #bucle para leer token que no es una directiva (.text/.data y final de fichero)
    while not directives.creasm_is_directive_segment(lexical.asm_get_token(context)) and not lexical.creasm_is_end_of_file(context):
        #label1:
        #label2 : .double 
        token = lexical.asm_get_token(context)
        print(f"Token dentro de sintactical_data: {token}, Índice: {context.t}")

        acc_cmt = lexical.asm_get_comments(context)
        lexical.asm_reset_comments(context)

        # ** Detectar posible TAG **
        possible_tag = ""
        #NOT.text/.data y final de fichero
        while not directives.creasm_is_directive_datatype(lexical.asm_get_token(context)) and not lexical.creasm_is_end_of_file(context):
            #Extrae y lo almacena en possible_tag
            possible_tag = lexical.asm_get_token(context)            
            print(f"Etiqueta posible: {possible_tag}, Índice: {context.t}")

            #Verifica etiqueta TAG
            if "TAG" != lexical.asm_get_token_type(context):
                if "" == possible_tag:
                    possible_tag = "EMPTY"                
                return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor ('compiler', 'NO TAG OR DIRECTIVE') + "'" + possible_tag + "'")
            
            #Elimina el ultimo caracter
            tag = possible_tag [:-1]

            #Verifica que TAG no sea una instruccion, que no se repita y que no tenga un formato invalido
            if not creasm_is_ValidTag(tag):
                return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'INVALID TAG FORMAT') + "'" + tag + "'")                       
            if tag in context.assembly:
                return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'TAG OR INSTRUCTION') + "'" + tag + "'")
            if tag in ret[0]['labels_asm']:
                return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'REPEATED TAG') + "'" + tag + "'")
            
            elto ['labels'].append(tag) 
            context.assembly[tag] = 0  # Almacena la etiqueta en el diccionario de assembly          
            ret[0]['labels_asm'][tag] = 0

            #Si es .datatype y avanza al otro tag
            lexical.asm_next_token(context)
            print(f"Índice después de avanzar (data): {context.t}")

        elto ['associated_context'] = lexical.asm_get_label_context(context)

        #Se comprueba nuevamente si se ha alcanzado el final del archivo    
        if lexical.creasm_is_end_of_file(context):
            #Si terminca en 'label' pero sin valores
            if elto ['labels']:
                ret[0].setdefault('obj', []).append(elto)
            break

        #    
        #label1:
        #label2 : .double
        #
        elto ['datatype'] = lexical.asm_get_token(context)
        
        #.WORD || .FLOAT || .DOUBLE
        if directives.creasm_has_datatype_attr(elto['datatype'], "numeric"):

            #.float 1.23
            #.word  2, 4, 0x8F, 'a', 077

            #Se obtiene el tamano en bytes
            elto ['byte_size'] = directives.creasm_get_datatype_size(elto['datatype'])
            if elto ['byte_size'] > 1:
                elto ['endian'] = context.endian

            # <value> | .<directive>
            lexical.asm_next_token(context)
            possible_value = lexical.asm_get_token(context)

            while not directives.creasm_is_directive(lexical.asm_get_token(context)) and not lexical.creasm_is_end_of_file(context):
                number = 0
                num_bits = "0"

                #Obtiene el valor 
                ret1 = datatypes.dt_get_imm_value(possible_value)
                if not ret1['isDecimal'] and not ret1 ['isFloat']:
                    #Revisa si el datatypes es numerico
                    if elto ['datatype'] != ".word" and elto ['datatype'] != ".float" and elto ['datatype'] != ".double":  #".word || .float || .double":
                        return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler','NO NUMERIC DATATYPE') + "'" + possible_value + "'")                    
                    #Revisa etiqueta (label) valida
                    if not creasm_is_ValidTag (possible_value):
                        return lexical.asm_lang_error(context,f_of_data_text.i18n_getTagFor('compiler','INVALID TAG FORMAT') + "'" + possible_value + "'")                    
                    if possible_value in context.assembly:
                        return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'TAG OR INSTRUCTION') + "'" + possible_value + "'")
                    
                    #Etiqueta (label) como n'umero
                    elto['pending'].append({
                        "type": "field-data",
                        "label": possible_value,
                        "addr": elto['seg_ptr'],
                        "start_bit": [0],
                        "stop_bit": [WORD_BYTES * BYTE_LENGTH - 1],  # [4 * 8 -1]
                        "n_bits": WORD_BYTES * BYTE_LENGTH, # 4 * 8
                        "rel":False,
                        "labelContext": lexical.asm_get_label_context(context),
                        "field_j":0
                    })
                
                else:
                    number = ret1 ['number']

                    #Decimal y float a binario
                    if ret1 ['isDecimal']:
                        a = f_of_data_text.decimal2binary(number, elto ['byte_size'] * BYTE_LENGTH)
                    else:
                        a = f_of_data_text.float2binary(number, elto ['byte_size'] * BYTE_LENGTH)

                    num_bits = a[0]
                    free_space = a[1]

                    #Revisa el espacio
                    if free_space < 0:
                        return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler','EXPECTED VALUE') + elto['datatype']+
                                                      "' (" + str(elto['byte_size'] * BYTE_LENGTH) + "bits), " +
                                                      f_of_data_text.i18n_getTagFor('compiler', 'BUT INSERTED') + possible_value +
                                                      "' (" + str(len(num_bits)) + " bits) " +
                                                      f_of_data_text.i18n_getTagFor('compiler', 'INSTEAD'))
                #Anade elemento
                elto['seg_name'] = seg_name
                elto['source'] = possible_value
                elto['track_source'].append(possible_value)
                elto['comments'].append(acc_cmt)
                elto['value'] = num_bits
                elto['source_alt'] = elto['datatype'] + ' ' + possible_value
                elto['format'] = ret1['format']

                ret[0].setdefault('obj', []).append(elto)
                elto = creasm_new_objEl(elto)

                #Por si detecta una ','
                lexical.asm_next_token(context)
                if lexical.asm_get_token(context) == ",":
                    lexical.asm_next_token(context)

                if directives.creasm_is_directive(lexical.asm_get_token(context)) or lexical.asm_get_token_type(context) == "TAG" or lexical.asm_get_token(context) and lexical.asm_get_token(context)[0] == ".":
                    break
                #Finaliza el bluce luego de leer una etiqueta (TAG) o directiva (directive)

                # <value> | .<directive>
                possible_value = lexical.asm_get_token(context)
                    
        #SPACE | .ZERO
        elif directives.creasm_has_datatype_attr(elto['datatype'], "space"):
            lexical.asm_next_token(context)
            possible_value = lexical.asm_get_token(context)

            ret1 = datatypes.is_decimal(possible_value)
            possible_value = ret1['number']
            if not ret1['isDecimal']:
                return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'NO NUMBER OF BYTES') + "'" + possible_value + "'")
            if possible_value < 0:
                return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'NO POSITIVE NUMBER') + "'" + possible_value + "'")
            
            byte_val = '0x0' if elto['datatype'] != ".zero" else '_'

            elto['seg_name'] = seg_name
            elto['comments'].append(acc_cmt)
            elto['byte_size'] = possible_value
            elto['value'] = byte_val
            elto['track_source'] = ['_'] * ret1['number']
            elto['source_alt'] = elto['datatype'] + ' ' + str(possible_value)  #revisar

            ret[0].setdefault('obj', []).append(elto)
            elto = creasm_new_objEl(None)

            lexical.asm_next_token(context)
        
        #.ALIGN
        elif directives.creasm_has_datatype_attr(elto['datatype'], "align"):
            lexical.asm_next_token(context)
            possible_value = lexical.asm_get_token(context)

            ret1 = datatypes.is_decimal(possible_value)
            possible_value = ret1['number']
            if not ret1['isDecimal'] or possible_value < 0:
                return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'INVALID ALIGN VALUE') + 
                                              "'" + possible_value + "'. " +
                                              f_of_data_text.i18n_getTagFor('compiler', 'REMEMBER ALIGN VAL'))
            
            align_offest = int (possible_value)
            if elto['datatype'] == ".align":
                align_offest = 2 ** align_offest

            elto['seg_name'] = seg_name
            elto['track_source'].append('.aling ' + str(possible_value)) #revisar
            elto['comments'].append(acc_cmt)
            elto['byte_size'] = align_offest
            elto['value'] = possible_value
            elto['source_alt'] = elto['datatype'] + ' ' + str(possible_value)

            ret[0].setdefault('obj', []).append(elto)
            elto = creasm_new_objEl(None)

            lexical.asm_next_token(context)

        #elif STRING
        elif directives.creasm_has_datatype_attr(elto['datatype'],"string"):
            lexical.asm_next_token(context)
            possible_value = lexical.asm_get_token(context)

            ret1 = f_of_data_text.treat_control_sequences(possible_value)
            if ret1['error']:
                return lexical.asm_lang_error(context, ret1['string'])
            
            possible_value = ret1['string']

            while not directives.creasm_is_directive(lexical.asm_get_token(context)) and not lexical.creasm_is_end_of_file(context):
                if possible_value[0] != "\"":
                    return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'NO QUOTATION MARKS') + "'" + possible_value + "'")
                if possible_value[-1] != "\"":
                    return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'NOT CLOSED STRING'))
                if not possible_value:
                    return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'NOT CLOSED STRING'))
                if lexical.asm_get_token_type(context) != "STRING":
                    return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'NO QUOTATION MARKS') + "'" + possible_value + "'")
                
                elto['seg_name'] = seg_name
                elto['comments'].append(acc_cmt)

                elto['value']=[]
                for char in possible_value:
                    if char == "\"":
                        continue

                    elto['track_source'].append(char)
                    num_bits = ord(char)
                    elto['value'].append(num_bits)

                if elto['datatype'] in [".string", ".asciiz"]:
                    elto['value'].append(0)
                    elto['track_source'].append('0x0')

                    ret[0].setdefault('obj', []).append(elto)
                    elto = creasm_new_objEl(elto)

                    lexical.asm_next_token(context)
                    if lexical.asm_get_token(context) == ",":
                        lexical.asm_next_token(context)

                    #Verificamos si la cadena está vacía antes de seguir accediendo:
                    #Se comprueba si el token es una directiva
                    #Se no es una directiva, se comprueba si el tipo del token es "TAG".
                    #Si el tipo no es "TAG", entonces se verifica si el token es válido y si el primer carácter es un punto ('.').
                    if directives.creasm_is_directive(lexical.asm_get_token(context)) or lexical.asm_get_token_type(context) == "TAG" or lexical.asm_get_token(context) and lexical.asm_get_token(context)[0] == ".":
                        break

                    possible_value = lexical.asm_get_token(context)
                    ret1 = f_of_data_text.treat_control_sequences(possible_value)
                    if ret1['error']:
                        return lexical.asm_lang_error(context, ret1['string'])
                    
                    possible_value = ret1['string']
        else:
            return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'UNEXPECTED DATATYPE') + "'" + elto['datatype']+ "'")
                
    return ret

def filter_fields(fields):
    fiels_filtrados = []
    for field in fields:
        if isinstance(field, dict) and field.get('type') not in ['co', 'cop']:
            fiels_filtrados.append(field)
    return fiels_filtrados #[field for field in fields if isinstance(field, dict) and field.get('type') not in ['co', 'cop']]

#******** TEXT ********
def sintactical_text(context,ret,creator_arch):
    possible_tag = ""
    possible_inst = ""
    tag = ""
    acc_cmt = ""
    elto = None
    candidate = None

    print(f"Entrando a sintactical_text: {context.t}")
    seg_name = lexical.asm_get_token(context)
    print(f"Segmento encontrado: {seg_name}")
    lexical.asm_next_token(context)
    print(f"Indice despues de avanzar desde segmento: {context.t}")

    elto = creasm_new_objEl(None)
    elto['seg_name'] = seg_name #".text"
    elto['endian'] = context.endian

#   while not directives.creasm_is_directive_segment(lexical.asm_get_token(context)) and not lexical.creasm_is_end_of_file(context):
    #token = lexical.asm_get_token(context)
    while not directives.creasm_is_directive_segment(lexical.asm_get_token(context)) and not lexical.creasm_is_end_of_file(context):
        token = lexical.asm_get_token(context)
        print(f"Token dentro de sintactical text: {token}, I: {context.t}")

        acc_cmt = lexical.asm_get_comments(context)
        lexical.asm_reset_comments(context)

        possible_tag = lexical.asm_get_token(context)
        while not lexical.creasm_is_end_of_file(context) and possible_tag[-1] == ':':
            possible_tag = lexical.asm_get_token(context)

            if lexical.asm_get_token_type(context) != "TAG":
                if possible_tag == "":
                    possible_tag = "EMPTY"
                return lexical.asm_lang_error(context,f_of_data_text.i18n_getTagFor('compiler','NO TAG, DIR OR INS') + "'" + possible_tag + "'")
            
            tag = possible_tag[:-1]

            if not creasm_is_ValidTag(tag):
                return lexical.asm_lang_error(context,f_of_data_text.i18n_getTagFor('compiler', 'INVALID TAG FORMAT') + "'" + tag + "'")
            
            if tag in context.assembly:
                return lexical.asm_lang_error(context,f_of_data_text.i18n_getTagFor('compiler', 'TAG OR INSTRUCTION') + "'" + tag + "'")
            #ret es una lista de diccionarios y accede al primer elemento de la lista
            if tag in ret[0]['labels_asm']:
                return lexical.asm_lang_error(context,f_of_data_text.i18n_getTagFor('compiler', 'REPEATED TAG') + "'" + tag + "'")
            
            elto['labels'].append(tag)
            context.assembly[tag] = 0  # Almacena la etiqueta en el diccionario de assembly          
            ret[0]['labels_asm'][tag] = 0

            lexical.asm_next_token(context)
            possible_tag = lexical.asm_get_token(context)

        elto['associated_context'] = lexical.asm_get_label_context(context)

        if lexical.creasm_is_end_of_file(context):
            if elto['labels']:
                ret[0].setdefault('obj', []).append(elto)
            break

        possible_inst = lexical.asm_get_token(context)
        elto['byte_size'] = WORD_BYTES
        elto['value'] = {}
        elto['value']['instruction'] = possible_inst
        elto['assembly_reference'] = context.assembly.get(possible_inst)
        elto['value']['fields'] = []
        elto['value']['signature_type_arr'] = [possible_inst]
        #elto['value']['signature_size_arr'] = [oc_size]

        item = None
        isPseudoinstruction = False

        for instr in creator_arch['instructions']:
            if instr['name'] == possible_inst:
                item = instr
                elto['value']['fields'] = filter_fields(elto['value']['fields'])
                break

        if item is None:
            for pseudo in creator_arch.get('pseudoinstructions', []):
                if pseudo['name'] == possible_inst:
                    item = pseudo
                    isPseudoinstruction = True
                    elto['value']['fields'] = filter_fields(elto['value']['fields'])
                    break

        #Se valida una instrucciones y pseudoinstrucciones
        if item is None:
            print("Error: Instrucción no reconocida...")
            lexical.asm_next_token(context)
            continue

        #Si es una instrucción
        if not isPseudoinstruction:
            elto['datatype'] = "instruction"
            elto['value']['signature_size_arr'] = [len(elto['value']['signature_type_arr'])]
            #Llama a la función para generar el binario (standby)
            elto['binary'] = "binary_encoding_of_instruction"
                        
        #Si es una pseudoinstrucción
        else:
            elto['datatype'] = "pseudoinstruction"
            elto['value']['signature_size_arr'] = [0]
            elto['binary'] = ""

        j = 0
        while j<len(item['fields']):
            possible_field = lexical.asm_get_token(context)
            elto['value']['fields'].append(possible_field)
            j = j + 1

        ret[0].setdefault('obj',[]).append(elto)

        elto = creasm_new_objEl(elto)
        lexical.asm_next_token(context)
        
    return ret    

#********** CATCH DE SINTACTICAL DATA AND TEXT **********
#Funcion para analizar el sintactical de datos y texto
def sintactical (input_text):
    # Opening JSON file
    f = open('RISC_V_RV32IMFD.json')
    creator_arch = json.load(f)
    f.close()

    #Inicializa el contexto con el texto
    context = Context (input_text)

    ret = [{}] #ret como lista que contiene un dicionario vacio
    ret[0]['labels_asm'] = {} #labels_asm dentro de la lista
    ret[0]['error'] = None

    print(f"Índice antes de next_token: {context.t}")
    context = lexical.asm_next_token(context)

    #Tokeniza el texto de entrada    
    while not lexical.creasm_is_end_of_file(context):
        print(f"Índice después de next_token: {context.t}")
        token = lexical.asm_get_token(context)
        print(f"Token actual: {token}, Índice: {context.t} \n")
        print(f"Verificación de ret antes de procesar token: {ret} \n")
        print("Probando Token:" +" " +str(token))

        if token == ".data":     
           sintactical_data (context, ret)
        elif token == ".text":
            sintactical_text(context, ret, creator_arch)
        else: 
            print(f"unknown token> " + str(token)) 
    return ret #hay que devolver un array de objetos
