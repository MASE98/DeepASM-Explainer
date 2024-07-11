import lexical
import directives
import f_of_data_text
import datatypes
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
    my_reg_ex = re.compile(r'[^a-z,_\d]', re.IGNORECASE)
    return not my_reg_ex.search(tg)
   
#******** FUNCIONES PARA TEXT **********
#SIGNATURE USER
def creasm_signature_user(elto, use_as_around):
    offset = len(elto['signature_type_arr']) - len(elto['signature_size_arr'])

    elto['signature_user'] = ''

    for j in range(len(elto['signature_size_arr'])):
        elto['signature_user'] += (
            '[' +
            elto['signature_type_arr'][j + offset] + ', ' +
            str(elto['signature_size_arr'][j]) + use_as_around + ' bits' +
            ']'
        )

    return elto['signature_user']

#BITS
def creasm_get_sel_valbin(value, start_bit, stop_bit):
    sel_start = 0
    sel_stop = 0
    valbin = 0
    a = None

    if start_bit > stop_bit:
        sel_start = (WORD_LENGTH - 1) - start_bit
        sel_stop = (WORD_LENGTH - 1) - stop_bit

    else:
        sel_stop = (WORD_LENGTH - 1) - start_bit
        sel_start = (WORD_LENGTH -1) - stop_bit

    a = datatypes.dt_get_decimal_value(value)
    valbin = int(a['number'])

    if valbin < 0:
        valbin = bin((valbin + (1 << WORD_LENGTH)) % (1 << WORD_LENGTH))[2:]
    else:
        valbin = bin(valbin)[2:].zfill(WORD_LENGTH)

    valbin = valbin[sel_start:sel_stop + 1]
    return valbin


#MUESTRA CANDIDATOS SIMILARES A UNA INSTRUCCION
def creasm_get_similar_candidates(context, elto):
    msg = elto['source']
    if 'associated_pseudo' in elto:
        msg = elto['source'] + f' (part of pseudoinstruction "{elto["associated_pseudo"]["source"]}")'

    msg = f_of_data_text.i18n_getTagFor('compiler', 'REMEMBER FORMAT USED') + \
          f"'{msg}': <br>" + \
          "<span class='m-2'>\u2718</span> " + \
          elto['value']['signature_user'] + "<br>"
    
    msg = f_of_data_text.i18n_getTagFor('compiler', 'NOT MATCH FORMAT') + ":<br>"

    for key in context.assembly:
        if (key in elto['value']['instruction']) or (elto['value']['instruction'] in key):
            # Asegurándonos de que context.assembly[key] sea un iterable
            if isinstance(context.assembly[key], list):
                for entry in context.assembly[key]:
                    msg += "<span class='m-1'>\u2714</span> " + entry['signature_user'] + "<br>"
            else:
                msg += "<span class='m-1'>\u2714</span> " + str(context.assembly[key]) + "<br>"
    
    msg += f_of_data_text.i18n_getTagFor('compiler', 'CHECKS')

    return msg

#
def creasm_encoded_field(arr_encoded, value, start_bit, stop_bit):
    val_i = 0
    
    for m in range(len(start_bit)):
        for k in range(start_bit[m],stop_bit[m] + 1):
            if val_i >= len(value):
                print("creasm_encoded_field: value.length < encode space :-)")
                return
            arr_encoded[k] = value[val_i]
            val_i += 1

#CODIFICA LA INSTRUCCION EN FORMATO BINARIO
def creasm_encode_instruction(context, ret, elto, candidate):
    start_bit = 0
    stop_bit = 0
    n_bits = 0
    value = 0
    val_encoded = ""
    arr_encoded = ""
    #arr_encoded = []
    ret1 = None
    bit_size = 0

    bit_size = elto['byte_size'] * BYTE_LENGTH
    val_encoded = "0" *bit_size
    arr_encoded = list(val_encoded)

    creasm_encoded_field(arr_encoded, candidate['oc']['value'], candidate['oc']['asm_start_bit'], candidate['oc']['asm_stop_bit'])
    creasm_encoded_field(arr_encoded, candidate['eoc']['value'], candidate['eoc']['asm_start_bit'], candidate['eoc']['asm_stop_bit'])

    for j in range(len(candidate['fields'])):
        start_bit = candidate['fields'][j]['asm_start_bit']
        stop_bit = candidate['fields'][j]['asm_stop_bit']
        n_bits = candidate['fields'][j]['asm_n_bits']

        if elto['value']['signature_type_arr'][j+1] in ["imm", "(imm)", "address", "(address)"]:
            value = elto['value']['fields'][j]
            if value[0] == '(':
                value = value.replace('(','').replace(')','')

            ret1 = datatypes.dt_get_imm_value(value)
            if not ret1['isDecimal'] and not ret1['isFloat']:
                pinfo = {
                    "type": "field-instruction",
                    "label": elto['value']['fields'][j],
                    "addr": 0,
                    "start_bit": start_bit,
                    "stop_bit": stop_bit,
                    "n_bits": n_bits,
                    "rel": False,
                    "labelContext": lexical.asm_get_label_context(context),
                    "field_j": j
                }
                elto['pending'].append(pinfo)

                if elto['value']['signature_type_arr'][j+1] in ["address", "(address)"]:
                    if 'address_type' in candidate['fields'][j] and candidate['fields'][j]['address_type'] != "abs":
                        pinfo['rel'] = True
                continue
            
            if ret1['isDecimal']:
                a = f_of_data_text.decimal2binary(ret1['number'],n_bits)
            else:
                a = f_of_data_text.float2binary(ret1['number'], n_bits)

            value = a[0]
            if a[1] < 0:
                return creasm_eltoErro(
                    context, elto,
                    f"EXPECTED VALUE immediate ({n_bits} bits), BUT INSERTED {elto['value']['fields'][j - 1]} ({len(value)} bits) INSTEAD"
                )
            value = value.zfill(n_bits)

        elif elto['value']['signature_type_arr'][j+1] in ["reg", "(reg)"]:
            value = elto['value']['fields'][j]
            if value[0] == '(':
                value = value.replace('(', '').replace(')', '')
            value = context.register[value]#['register'][value]
            value = bin(value)[2:]
            value = value.zfill(n_bits)
        else:
                value = "0".zfill(n_bits)

        creasm_encoded_field(arr_encoded, value, start_bit, stop_bit)

    return ''.join(arr_encoded)                      

#COMPARA DOS SIGNATURE PARA DEVOLVER LA DISTANCIA NUMERICA ENTRE ELLOS 
def creasm_text_getDistance(elto_assembly_reference_i, elto_value):
    candidate_type_as_string = f_of_data_text.base_replace_all(elto_assembly_reference_i['signature_type_str'], 'address','imm')
    candidate_size_as_intarr = elto_assembly_reference_i['signature_size_arr']

    signature_type_as_string = f_of_data_text.base_replace_all(' '.join(elto_value['signature_type_arr']), 'address', 'imm')
    signature_size_as_intarr = elto_value['signature_size_arr']

    if candidate_type_as_string != signature_type_as_string:
        return -1
    
    distance = 0
    distance_j = 0
    offset_j = 0

    offset_j = len(candidate_size_as_intarr) - len(signature_size_as_intarr)

    for j in range(len(candidate_size_as_intarr)):
        distance_j = candidate_size_as_intarr[j+offset_j] - signature_size_as_intarr[j]
        if distance_j < 0:
            return -1
        distance += distance_j

    return distance

#DETERMINA LOS CANDIDATOS DE INSTRUCCI'ON
def creasm_candidates_instr(context, ret, elto):
    candidates = 0
    distance = 0

    elto['assembly_reference_distance'] = -1
    elto['assembly_reference_index'] = 0

    if not elto['assembly_reference']:
        ret[0]['error'] = "NO ASSEMBLY REFERENCE FOUND"
        #return creasm_eltoErro(context,elto,"NO ASSEMBLY REFERENCE FOUND")

    for i in range(len(elto['assembly_reference'])):
        distance = creasm_text_getDistance(elto['assembly_reference'][i], elto['value'])

        if distance < 0:
            continue

        candidates += 1

        if elto['assembly_reference_distance'] < 0 or elto['assembly_reference_distance'] > distance:
            elto['assembly_reference_distance'] = distance
            elto['assembly_reference_index'] = i
    
    if candidates == 0:
        msg = creasm_get_similar_candidates(context, elto)
        #return creasm_eltoErro(context, elto, msg)
        ret[0]['error'] = msg 
        return ret
    
    elto['byte_size'] = elto['assembly_reference'][elto['assembly_reference_index']]['nwords'] * WORD_BYTES
    
    return ret

#CLASIFICACION DE OPERANDOS
def creasm_text_instr_op_match(context, ret, elto, atom, parentheses):
    opx = ''
    #result = {'error': None}

    if atom in context.register: #['register']:
        if parentheses:
            elto['value']['fields'].append(f'({atom})')
            elto['value']['signature_type_arr'].append('(reg)')
        else:
            elto['value']['fields'].append(atom)
            elto['value']['signature_type_arr'].append('reg')

        elto['value']['signature_size_arr'].append(len(bin(context.register[atom])[2:]))#['register'][atom])[2:]))

        return ret #result
    
    ret1 = datatypes.dt_get_imm_value(atom)
    if ret1['isDecimal'] or ret1['isFloat']:
        a = None
        if ret1['isDecimal']:
            a = f_of_data_text.decimal2binary(ret1['number'], elto['byte_size'] * BYTE_LENGTH)
        else:
            a = f_of_data_text.float2binary(ret1['number'], elto['byte_size'] * BYTE_LENGTH)
        
        if parentheses:
            elto['value']['fields'].append(f'({atom})')
            elto['value']['signature_type_arr'].append('(imm)')
        
        else:
            elto['value']['fields'].append(atom)
            elto['value']['signature_type_arr'].append('(imm)')
        
        elto['value']['signature_size_arr'].append(a[2])

        return ret #ret
    
    if parentheses:
        elto['value']['fields'].append(f'({atom})')
        elto['value']['signature_type_arr'].append('(address)')
    else:
        elto['value']['fields'].append(atom)
        elto['value']['signature_type_arr'].append('address')

    elto['value']['signature_size_arr'].append(1)

    return ret #ret

#OBTIENE UNIDAD BASICA DE UNA INSTRUCI'ON
def creasm_text_ops_getAtom(context, pseudo_context):
    opx = ''

    if pseudo_context is not None:
        if pseudo_context['index'] >= len(pseudo_context['parts']):
            return ''
        
        pseudo_context['index'] += 1
        opx = pseudo_context['parts'][pseudo_context['index']]
    
    else:
        lexical.asm_next_token(context)
        opx = lexical.asm_get_token(context)

        if lexical.creasm_is_end_of_file(context) or lexical.asm_get_token_type(context) == "TAG":
            return ''
        
    if opx in context.assembly or directives.creasm_is_directive_segment(opx):
        return ''
    
    return opx

#PROCESAR INSTRUCCIONES Y PSEUDOINSTRUCCIONES
def creasm_text_elto_fields(context, ret, elto, pseudo_context):
    ret1 = None
    opx = ''
    atom = ''
    par = False

    print(f"Inicio de creasm_text_elto_fields, ret: {ret}")

    #***CREAR LA FUNCION getAtom con este nombre : creasm_text_ops_getAtom***
    opx = creasm_text_ops_getAtom(context, pseudo_context)

    while opx != '' and len(elto['value']['fields']) < 100:
        atom = opx
        par = False

        if opx == 'sel':
            sel = {'start': 0, 'stop': 0, 'label': '' }
            valbin = '0'

            opx = creasm_text_ops_getAtom(context, pseudo_context)
            if opx != '(':
                return creasm_eltoErro(context, elto, f_of_data_text.i18n_getTagFor('compiler','OPEN PARENTHESIS NOT FOUND'))
            
            sel['stop'] = int(creasm_text_ops_getAtom(context, pseudo_context)) #creasm_text_ops_getAtom(context, pseudo_context)
            #sel['stop'] = int(sel['stop'])
            if not isinstance(sel['stop'], int):
                return creasm_eltoErro(context, elto, f_of_data_text.i18n_getTagFor('compiler', 'NO POSITIVE NUMBER') + str(sel['stop']))
            
            #opx = creasm_text_ops_getAtom(context, pseudo_context)
            #if opx != ',':
            if creasm_text_ops_getAtom(context, pseudo_context) != ',':
                return creasm_eltoErro(context, elto, f_of_data_text.i18n_getTagFor('compiler', 'COMMA NOT FOUND'))
            
            sel['start'] = int(creasm_text_ops_getAtom(context,pseudo_context)) #creasm_text_ops_getAtom(context,pseudo_context)
            #sel['start'] = int(sel['start'])
            if not isinstance(sel['start'], int):
                return creasm_eltoErro(context,elto,f_of_data_text.i18n_getTagFor('compiler','NO POSITIVE NUMBER') + str(sel['start']))

            #opx = creasm_text_ops_getAtom(context,pseudo_context)
            #if opx != ',':
            if creasm_text_ops_getAtom(context, pseudo_context) != ',':
                return creasm_eltoErro(context, elto, f_of_data_text.i18n_getTagFor('compiler', 'COMMA NOT FOUND'))
            
            sel['label'] = creasm_text_ops_getAtom(context,pseudo_context)

            #opx = creasm_text_ops_getAtom(context,pseudo_context)
            #if opx != ')':
            if creasm_text_ops_getAtom(context, pseudo_context) != ')':
                return creasm_eltoErro(context, elto, f_of_data_text.i18n_getTagFor('compiler', 'CLOSE PARENTHESIS NOT FOUND'))
            
            a = datatypes.dt_get_imm_value(sel['label'])
            if a['isDecimal']:
                #**CREAR FUNCION VALBIN: creasm_get_sel_valbin
                valbin = creasm_get_sel_valbin(sel['label'], sel['start'], sel['stop'])
                #** CREAR FUNCION: dt_binary2format
                atom = datatypes.dt_binary2format(valbin,a['format'])
            else:
                if not creasm_is_ValidTag(sel['label']):
                    return creasm_eltoErro(context,elto,f_of_data_text.i18n_getTagFor('compiler','LABEL NOT DEFINED') + ": '" + sel['label'] + "'")             
                
                atom = f"{sel['label']}[{sel['start']}:{sel['stop']}]"
        
        elif opx == '(':
            par = True

            atom = creasm_text_ops_getAtom(context,pseudo_context)
            if atom == '':
                return creasm_eltoErro(context,elto, f_of_data_text.i18n_getTagFor('compiler', 'CLOSE PARENTHESIS NOT FOUND'))
            
            #opx = creasm_text_ops_getAtom(context,pseudo_context)
            #if opx != ')':
            if creasm_text_ops_getAtom(context, pseudo_context) != ')':
                return creasm_eltoErro(context,elto, f_of_data_text.i18n_getTagFor('compiler','CLOSE PARENTHESIS NOT FOUND'))
            
        #**CREAR FUNCION MATCH
        ret1 = creasm_text_instr_op_match(context,ret,elto,atom,par)
        print(f"Después de creasm_text_instr_op_match, ret: {ret}, ret1: {ret1}")  # Añad
        if ret1.get('error') is not None:
            ret[0]['error'] = ret1['error'] #Asigna el error al diccionario correcto dentro de ret
            print(f"Error encontrado, ret: {ret}")  # Añadido para verificar ret
            return ret
        
        opx = creasm_text_ops_getAtom(context, pseudo_context)
        if opx == ',':
            while opx == ',':
                opx = creasm_text_ops_getAtom(context,pseudo_context)
        elif opx != '' and context.options['mandatory_comma']: #['options']['mandatory_comma']:
            return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'COMMA NOT FOUND'))
        
    if len(elto['value']['fields']) > 100:
        return creasm_eltoErro(context, elto,
                               f_of_data_text.i18n_getTagFor('compiler', 'NOT MATCH FORMAT') + ".<br>" +
                               f_of_data_text.i18n_getTagFor('compiler', 'REMEMBER FORMAT USED') + " '" + elto['source'] + "'.<br>" +
                               f_of_data_text.i18n_getTagFor('compiler', 'CHECK CODE'))
    
    elto['value']['signature_type_str'] = ' '.join(elto['value']['signature_type_arr'])
    elto['value']['signature_size_str'] = ' '.join(map(str, elto['value']['signature_size_arr']))#.join(elto['value']['signature_size_arr']) convierte entero a cadena
    #CREAR wsasm_make_signature_user con el nombre: creasm_signature_user
    elto['value']['signature_user'] = creasm_signature_user(elto['value'],'+')

    print(f"Finalizando creasm_text_elto_fields, ret: {ret}")  # Añadido para verificar ret al final
    return ret

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
            #extrae y lo almacena en possible_tag
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

                #if directives.creasm_is_directive(lexical.asm_get_token(context)) or lexical.asm_get_token_type(context) == "TAG" or lexical.asm_get_token(context)[0] == ".":
                #Se comprueba si el token es una directiva
                #Se no es una directiva, se comprueba si el tipo del token es "TAG".
                #Si el tipo no es "TAG", entonces se verifica si el token es válido y si el primer carácter es un punto ('.').
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
            elto['source_alt'] = elto['datatype'] + ' ' + str(possible_value) #revisar

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

                    #token = lexical.asm_get_token(context)
                    #directives.creasm_is_directive(lexical.asm_get_token(context)) or lexical.asm_get_token_type(context) == "TAG" or (token and token[0] == "."): 
                    
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
        # Asegurar avance del contexto después de procesar un token de tipo de datos
        #lexical.asm_next_token(context)
        #print(f"Índice después de procesar tipo de dato: {context.t}")
    #return ret

#******** TEXT ********
def sintactical_text(context, ret):
    possible_tag = ""
    possible_inst = ""
    tag = ""
    acc_cmt = ""
    elto = None
    candidate = None

    #xr_info = f_of_data_text.ctrlStates_get()
    # if xr_info is None:
    #     raise ValueError("ctrlStates_get devolvió None")
    # oc_size = int(xr_info.get('ir', {}).get('default_eltos', {}).get('oc', 0))
    #oc_size = int(xr_info['ir']['default_eltos']['oc'])

    #.text - .text
    #.data - label1: instr op1 op2 op3
    print(f"Entrando en sintactical_text: {context.t}")
    seg_name = lexical.asm_get_token(context)
    print(f"Segmento encontrado: {seg_name}")
    lexical.asm_next_token(context)
    print(f"Índice después de avanzar desde segmento: {context.t}")

    elto = creasm_new_objEl (None)
    elto ["seg_name"] = seg_name #["seg_name"]
    elto['endian'] = context.endian

    #.text - .text
    #.data - label1: instr op1 op2 op3
    while not directives.creasm_is_directive_segment(lexical.asm_get_token(context)) and not lexical.creasm_is_end_of_file(context):
        
        token = lexical.asm_get_token(context)
        print(f"Token dentro de sintactical text : {token}, Indice: {context.t}")

        acc_cmt = lexical.asm_get_comments(context)
        lexical.asm_reset_comments(context)

        possible_tag = ""
        while lexical.asm_get_token(context) not in context.assembly and not lexical.creasm_is_end_of_file(context):
            possible_tag = lexical.asm_get_token(context)
            print(f"Etiqueta posible: {possible_tag}, Índice: {context.t}")
            
            #revisa TAG
            if "TAG" != lexical.asm_get_token_type(context):
                if "" == possible_tag:
                    possible_tag = "EMPTY"
                return lexical.asm_lang_error(context, f_of_data_text.i18n_getTagFor('compiler', 'NO TAG, DIR OR INS') + "'" + possible_tag + "'")
            
            #Elimina el ultimo caracter
            tag = possible_tag[:-1]

            #Verifica TAG valido
            if not creasm_is_ValidTag(tag):
                return lexical.asm_lang_error(context,f_of_data_text.i18n_getTagFor('compiler','INVALID TAG FORMAT') + "'" + tag + "'")
            if tag in context.assembly:
                return lexical.asm_lang_error(context,f_of_data_text.i18n_getTagFor('compiler','TAG OR INSTRUCTION') + "'" + tag + "'")
            if tag in ret[0]['labels_asm']:
                return lexical.asm_lang_error(context,f_of_data_text.i18n_getTagFor('compiler','REPEATED TAG') + "'" + tag + "'")
            
            elto['labels'].append(tag)
            context.assembly[tag] = 0
            ret[0]['labels_asm'][tag] = 0

            lexical.asm_next_token(context)
        elto['associated_context'] = lexical.asm_get_label_context(context)

        #se comprueba si se ha alcanzado el final del archivo
        if lexical.creasm_is_end_of_file(context):
            if elto['labels']:
                ret[0].setdefault('obj', []).append(elto)
            break

        possible_inst = lexical.asm_get_token(context)
        elto['byte_size'] = WORD_BYTES
        #elto['value'] = {}
        elto['value'] = {
            'instruction': possible_inst,
            'fields': [],
            'signature_type_arr': [possible_inst],
            'signature_size_arr': [],
            'signature_user': ''
        }
        #elto['value']['instruction'] = possible_inst
        elto['assembly_reference'] = context.assembly.get(possible_inst,[]) #[possible_inst]
        if not isinstance(elto['assembly_reference'],list):
            elto['assembly_reference'] = []
        #elto['value']['fields'] = []
        #elto['value']['signature_type_arr'] = [possible_inst]
        #elto['value']['signature_size_arr'] = [oc_size]

        #
        #label: instr op1 op2 op3
        #
        print("Estructura inicial de elto:", elto)
        ret = creasm_text_elto_fields(context, ret , elto, None)
        print("Estructura final de elto:", elto)
        #if ret['error'] is not None:
        print(f"Verificación de ret en línea 857: {ret}")
        if ret[0].get('error') is not None: #Se asegura de acceder al diccionario correcto dentro de ret
            return ret
        
        if elto['value']['fields']:
            elto['source'] = elto['value']['instruction'] + ' ' + ' '.join(elto['value']['fields'])
            elto['source_alt'] = elto['value']['instruction'] + ' ' + ', '.join(elto['value']['fields'])
        else:
            elto['source'] = elto['value']['instruction']
            elto['source_alt'] = elto['source']

        elto['comments'].append(acc_cmt)
        elto['track_source'].append(elto['source'])

        print(f"Verificación de ret antes de creasm_candidates_instr: {ret}")
        ret = creasm_candidates_instr(context, ret, elto)
        print(f"Verificación de ret después de creasm_candidates_instr: {ret}")

        #if ret['error'] is not None:
        print(f"Verificación de ret en línea 874: {ret}")
        if ret[0].get('error') is not None: #Se asegura de acceder al diccionario correcto dentro de ret
            return ret
        
        candidate = elto['assembly_reference'][elto['assembly_reference_index']]

        if not candidate['isPseudoinstruction']:
            elto['datatype'] = "instruction"
            elto['value']['signature_size_arr'].insert(0,len(elto['assembly_reference'][0]['oc']))
            elto['binary'] = creasm_encode_instruction(context,ret, elto, candidate)
        else:
            elto['datatype'] = "pseudoinstruction"
            elto['value']['signature_size_arr'].insert(0, 0)
            elto['binary'] = ''

        #ret['obj'].append(elto)
        ret[0].setdefault('obj',[]).append(elto)

        elto = creasm_new_objEl(elto)
        #lexical.asm_next_token(context)
        #print(f"Índice después de procesar tipo de dato: {context.t}")
    return ret

#********** CATCH DE SINTACTICAL DATA AND TEXT **********
#Funcion para analizar el sintactical de datos y texto
def sintactical (input_text):
    #Inicializa el contexto con el texto
    context = Context (input_text)
    #context.t = 0
    #ret = []
    ret = [{}] #ret como lista que contiene un dicionario vacio
    ret[0]['labels_asm'] = {} #labels_asm dentro de la lista
    ret[0]['error'] = None
    #ret = {
        #'labels_asm': {}
    #}

    #context = lexical.asm_next_token(context)
    
    #Tokeniza el texto de entrada    
    while not lexical.creasm_is_end_of_file(context):
        print(f"Índice antes de next_token: {context.t}")
        context = lexical.asm_next_token(context)
        print(f"Índice después de next_token: {context.t}")
        token = lexical.asm_get_token(context)
        print(f"Token actual: {token}, Índice: {context.t}")
        print(f"Verificación de ret antes de procesar token: {ret}")
        print("Probando Token:" +" " +str(token))

        
        if token == ".data":     
           sintactical_data (context, ret)
        else:
             sintactical_text(context,ret)
        #elif token == ".text":
              #sintactical_text(context,ret)
        #else:
              #lexical.creasm_is_end_of_file(context)
              #print("FIN \n")
      
    return ret #hay que devolver un array de objetos