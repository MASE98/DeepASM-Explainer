# Directivas

as_directives = {
    # segmentos
    ".data":    {"name": ".data", "kindof": "segment", "size": 0, "attrs": ["data"]},
    ".text":    {"name": ".text", "kindof": "segment", "size": 0, "attrs": ["text"]},
    ".bss":     {"name": ".bss",  "kindof": "segment", "size": 0, "attrs": ["bss"]},
    ".section": {"name": ".section", "kindof": "segment", "size": 0, "attrs": ["section"]},
    ".foo":     {"name": ".foo", "kindof": "segment", "size": 0, "attrs": ["foo"]},
    
    # tipos de datos
    ".byte":    {"name": ".byte", "kindof": "datatype", "size": 1, "attrs": ["numeric"]},
    ".zero":    {"name": ".zero",   "kindof": "datatype", "size": 1, "attrs": ["space"]},
    ".string":  {"name": ".string", "kindof": "datatype", "size": 1, "attrs": ["string"]},
    ".half":    {"name": ".half", "kindof": "datatype", "size": 2, "attrs": ["numeric"]},
    ".word":    {"name": ".word", "kindof": "datatype", "size": 4, "attrs": ["numeric"]},
    ".float":   {"name": ".float", "kindof": "datatype", "size": 4, "attrs": ["numeric"]},
    ".double":  {"name": ".double", "kindof": "datatype", "size": 8, "attrs": ["numeric"]},
    ".dword":   {"name": ".dword", "kindof": "datatype", "size": 8, "attrs": ["numeric"]},

    # modificadores
    ".align":   {"name": ".align", "kindof": "datatype", "size": 0, "attrs": ["align"]},
    ".balign":  {"name": ".balign", "kindof": "datatype", "size": 0, "attrs": ["align"]},
    ".global":   {"name": ".globl", "kindof": "modifier", "size": 0, "attrs": ["global"]},
    ".option rvc": {"name": ".option rvc", "kindof": "modifier", "size": 0, "attrs": ["option"]},
    ".option norvc": {"name": ".option norvc", "kindof": "modifier", "size": 0, "attrs": ["option"]},
    ".option relax": {"name": ".option relax", "kindof": "modifier", "size": 0, "attrs": ["option"]},
    ".option norelax": {"name": ".option norelax", "kindof": "modifier", "size": 0, "attrs": ["option"]},
    ".option pic": {"name": ".option pic", "kindof": "modifier", "size": 0, "attrs": ["option"]},
    ".option nopic": {"name": ".option nopic", "kindof": "modifier", "size": 0, "attrs": ["option"]},
    ".option push": {"name": ".option push", "kindof": "modifier", "size": 0, "attrs": ["option"]},
    ".option pop": {"name": ".option pop", "kindof": "modifier", "size": 0, "attrs": ["option"]}
    
}

def creasm_is_directive_kindof(text, kindof):
    if text not in as_directives:
        # print(f"ERROR: not defined directive: {text}\n")
        return False
    return as_directives[text]["kindof"] == kindof

def creasm_is_directive(text):
    return text in as_directives

def creasm_is_directive_segment(text):
    return creasm_is_directive_kindof(text, "segment")

def creasm_is_directive_datatype(text):
    return creasm_is_directive_kindof(text, "datatype")

def creasm_get_datatype_size(datatype):
    if datatype not in as_directives:
        print(f"ERROR: not defined datatype: {datatype}\n")
        return 0
    return as_directives[datatype]["size"]

def creasm_has_datatype_attr(datatype, attr):
    if datatype not in as_directives:
        # print(f"ERROR: not defined directive: {datatype}\n")
        return False
    return attr in as_directives[datatype]["attrs"]
