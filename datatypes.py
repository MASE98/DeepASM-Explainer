import re
import struct

# BYTE_LENGTH = 8 
# WORD_BYTES  = 4 
# WORD_LENGTH = WORD_BYTES * BYTE_LENGTH 

#********** DECIMAL, OCTAL, HEXADECIMAL, FLOAT, CHAR **********
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

def isChar (n):
    ret = {
        'number':0,
        'isDecimal': False,
        'format': ''
    }
    return ret

def is_float (n):
    ret = {
        'number': 0.0,
        'isFloat': False,
        'format': ''
    }
    
    #Verificar errores
    non_float = re.compile(r'[a-df-zA-DF-Z]+')
    if non_float.search(n):
        return ret
    
    try:
        ret['number'] = float(n)
        ret['isFloat'] = True
        ret['format'] = 'ieee754'
    except ValueError:
        ret['number'] = 0.0
        ret['isFloat'] = False
        ret['format'] = ''

    return ret

#********* FUNCION PARA GET VALUE (API) ********
def dt_get_decimal_value(possible_value):
    ret = {
        'number':  0,
        'isDecimal': True,
        'format': ''
    }

    ret = is_octal (possible_value)
    if ret.get('isDecimal', False):
        return ret
    
    ret = is_hex (possible_value)
    if ret.get('isDecimal', False):
        return ret
    
    ret = is_decimal (possible_value)
    if ret.get('isDecimal', False):
        return ret
    
    ret = isChar (possible_value)
    if ret.get('isDecimal', False):
        return ret
    
    return ret

def dt_get_imm_value (value):

    ret1 = {}
    ret = {
        'number': 0,
        'isDecimal':False,
        'isFloat': False
    }

    ret1 = dt_get_decimal_value(value)
    if ret1 ['isDecimal']:
        ret1['isFloat'] = False
        return ret1
    
    ret1 = is_float(value)
    if ret1['isFloat']:
        ret1['isDecimal'] = False
        return ret1
    
    return ret

def dt_binary2format(valbin,format):
    val = int(valbin,2)
    ret = 0

    if format == 'dec':
        ret = str(val)
    elif format == 'octal':
        ret = '0' + oct(val)[2:]
    elif format == 'hex':
        ret = '0x' + hex(val)[2:]
    elif format == 'ascii':
        ret = chr(val)
    elif format == 'ieee754':
        #valor de 32 bits
        if len(valbin) == 32:
            ret = struct.unpack('!f',struct.pack('!I', val))[0]
        else:
            raise ValueError("Se requiere una cadena binaria de 32 bits")
    else:
        ret = str(val)

    return ret
