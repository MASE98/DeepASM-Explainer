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


#********** DECIMAL, OCTAL, HEXADECIMAL **********
def is_decimal(n):
    ret = {
        'number': 0,
        'isDecimal': False,
        'format': ''
    }

    # Chequeo de errores
    if len(n) > 1 and n[0] == '0':
        return ret
    if '.' in n:
        return ret

    # Convierte
    try:
        if n.isdigit():
            ret['isDecimal'] = True
            ret['format'] = 'dec'
            ret['number'] = int(n)
            return ret
    except ValueError:
        return ret

    return ret


def is_octal(n):
    ret = {
        'number': 0,
        'isDecimal': False,
        'format': ''
    }

    if n[0] == '0' and len(n) > 1:
        octal = n[1:].lstrip('0')
        try:
            ret['number'] = int(octal, 8)
            ret['isDecimal'] = (n == '0' + oct(ret['number'])[2:])
            ret['format'] = 'octal'
            return ret
        except ValueError:
            return ret

    return ret


def is_hex(n):
    ret = {
        'number': 0,
        'isDecimal': False,
        'format': ''
    }

    if n[:2].lower() == '0x':
        hex_num = n[2:].lstrip('0')
        if hex_num == '':
            return ret  # Considerar "0x" como inválido

        try:
            ret['number'] = int(hex_num, 16)
            ret['isDecimal'] = (n.lower() == '0x' + hex(ret['number'])[2:])
            ret['format'] = 'hex'
            return ret
        except ValueError:
            return ret

    return ret
    