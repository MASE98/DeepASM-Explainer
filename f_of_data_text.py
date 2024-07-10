import re
import struct
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
def i18n_getTagFor (component, key):
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

#******** FUNCION PARA CONVERTIR NUMEROS A REPRESENTACION BINARIA ********
def decimal2binary(number, size):
    num_base2 = bin(number)[2:]  # Convierte un número a binario y elimina el prefijo 0b
    num_base2_length = len(num_base2)

    WORD_LENGTH = 32  # Un tamaño de palabra de 32 bits

    if num_base2_length > WORD_LENGTH:
        return [num_base2, size - num_base2_length, num_base2_length]

    num_base2 = bin(number & ((1 << size) - 1))[2:]  # Convierte a binario sin signo
    num_base2_length = len(num_base2)
    if number >= 0:
        return [num_base2, size - num_base2_length, num_base2_length]

    num_base2 = "1" + num_base2.lstrip("1")
    num_base2_length = len(num_base2)
    if num_base2_length > size:
        return [num_base2, size - num_base2_length, num_base2_length]

    num_base2 = "1" * (size - len(num_base2)) + num_base2
    return [num_base2, size - len(num_base2), num_base2_length]

def float2binary(f, size):
    # Flotante con un valor de 32 bits
    uint = struct.unpack('I', struct.pack('f', f))[0]
    return decimal2binary(uint, size)

#******** FUNCION PARA CARACTERES **********
control_sequences = {
    'b':  '\b',
    'f':  '\f',
    'n':  '\n',
    'r':  '\r',
    't':  '\t',
    'v':  '\v',
    'a':  chr(0x0007),
    "'":  '\'',
    '"':  '\"',
    '0':  '\0'
}

def treat_control_sequences(possible_value):
    ret = {
        'string': "",
        'error': False
    }

    i = 0
    while i < len(possible_value):
        if possible_value[i] != "\\":
            ret['string'] += possible_value[i]
            i += 1
            continue

        i += 1

        if i >= len(possible_value):
            ret['string'] += "\\"
            break

        # Control de sequences
        if possible_value[i] in control_sequences:
            ret['string'] += control_sequences[possible_value[i]]
            i += 1
            continue

        # Unicode emojis
        if possible_value[i] == 'u':
            unicode_match = re.match(r'u\{([0-9A-Fa-f]+)\}', possible_value[i:])
            if unicode_match:
                unicode_char = chr(int(unicode_match.group(1), 16))
                ret['string'] += unicode_char
                i += len(unicode_match.group(0))
                continue

        # Para el control de errores o si se encuentra una secuencia Unicode
        ret['string'] = f"Unknown escape char '\\{possible_value[i]}'"
        ret['error'] = True
        return ret

    return ret

#******** ESTADO DEL SISTEMA *********
sim = {
    'systems': [],
    'active': None,
    'index': 0,
}

def ctrlStates_get():
    return sim['active']['ctrl_states']

# def ctrlStates_get():
#     if sim['active'] is not None and isinstance(sim['active'], dict) and 'ctrl_states' in sim['active']:
#         return sim['active']['ctrl_states']
#     else:
#         raise ValueError("'active' no está definido correctamente o no contiene 'ctrl_states'")
# def initialize_active():
#     sim['active'] = {
#         'ctrl_states': 'initial_value'  # Asigna un valor inicial adecuado
#     }

#******** REEMPLAZO A UNA CADENA BASE *********
def base_escapeRegExp(string):
    #caracteres especiales para uso de expresiones regulares
    return re.sub(r'[.*+?^${}()|[\]\\]', r'\\\g<0>', string)

def base_replace_all(base_str, match, replacement):
    return re.sub(base_escapeRegExp(match), replacement, base_str)

