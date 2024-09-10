import random
import csv

#Lista de operaciones
operaciones = ["add", "sub", "xor", "or", "and", "sll", "srl", "sra", "slt", "sltu", "addi", "xori", "ori", "andi", "slli", "srli", "srai", "slti", "sltiu",
               "lb", "lh", "lw", "lbu", "lhu", "sb", "sh", "sw", "beq", "bne", "blt", "bge", "bltu", "bgeu", "j", "ja", "jr" ,"mul", "mulh", "mulsu", "mulu", 
               "div", "divu", "rem", "flw", "fsw", "feq.s", "flt.s", "fle.s", "fmadd.s", "fmsub.s", "la", "li", "mv"]

#Función para generar una instrucciones
def generar_instruccion_valida():
    operacion = random.choice(operaciones)
    rd = "rd"
    rs1 = "rs1"
    
    #Operaciones con numero inmediato se usa "imm"
    if operacion in ["addi", "xori", "ori", "andi", "slli", "srli", "srai", "slti", "sltiu"]:
        rs2 = "imm"
        return f"{operacion} {rd}, {rs1}, {rs2}"
    
    #Operaciones como lb, lh, lw, lbu, lhu usan el formato: operacion rd, rs1, imm, rs2
    elif operacion in ["lb", "lh", "lw", "lbu", "lhu", "sb", "sh", "sw", "flw", "fsw"]:
        imm = "imm"
        rs2 = "rs2"
        return f"{operacion} {rd}, {imm}, {rs2}"
    
    #Operaciones con el formato: operacion rd, rs1, address
    elif operacion in ["beq", "bne", "blt", "bge", "bltu", "bgeu"]:
        address = "address"
        return f"{operacion} {rd}, {rs1}, {address}"
    
    #Operaciones con la, li
    elif operacion in ["la", "li"]:
        imm = "imm"
        return f"{operacion} {rd}, {imm}"
    
    #Operaciones con la, li
    elif operacion in ["mv"]:
        rs = "rs"
        return f"{operacion} {rd}, {rs}"

    #Operaciones j, ja, jr
    elif operacion in ["j"]:
        imm = "imm"
        return f"{operacion} {imm}"
    
    elif operacion in ["ja"]:
        address = "address"
        return f"{operacion} {rd}, {address}"
    
    elif operacion in ["jr"]:
        imm = "imm"
        return f"{operacion} {rd}"

    #Operaciones de punto flotante como fmadd.s
    elif operacion in ["fmadd.s", "fmsub.s"]:
        rs2 = "rs2"
        rs3 = "rs3"
        return f"{operacion} {rd}, {rs1}, {rs2}, {rs3}"
    
    #Para las demás operaciones se usa el formato estándar: operacion rd, rs1, rs2
    else:
        rs2 = "rs2"
    return f"{operacion} {rd}, {rs1}, {rs2}"

#Función para generar una instrucción incorrecta
def generar_instruccion_incorrecta():
    instruccion_valida = generar_instruccion_valida()
    partes = instruccion_valida.split(", ")

    #Introduce errores
    if len(partes) > 1:
        if random.choice([True, False]):
       	    #Elimina un operando
            partes = partes[:-1]  

    #Hace que falte el segundo registro
    if len(partes[0].split()) > 2:
        if random.choice([True, False]):
            #Elimina el segundo registro
            partes[0] = partes[0].replace("rs2", "")  
    return ", ".join(partes), instruccion_valida

# Genera el dataset
dataset = []
#Genera n ejemplos
for _ in range(3000): 
    incorrecta, corregida = generar_instruccion_incorrecta()
    dataset.append((incorrecta, corregida))

#Guarda el dataset en un archivo CSV
with open("dataset_de_instrucciones.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Instruccion incorrecta", "Instruccion correcta"])
    writer.writerows(dataset)
