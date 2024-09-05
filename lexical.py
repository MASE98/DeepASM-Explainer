#Check the end of the file
def creasm_is_end_of_file(context):
    return (context.t >= len(context.asm_t)) and ("" == asm_get_token(context))

#For the text and extract the following token
def asm_next_token(context):
    tok = ""
    first = 0
    last = 0
    token_type = ""

    # skip whitespaces
    while context.t < len(context.asm_t) and context.asm_t[context.t] in "# \t\n\r":
        if context.asm_t[context.t] == '#':
            first = context.t + 1
            while context.t < len(context.asm_t) and context.asm_t[context.t] != '\n':
                context.t += 1
            last = context.t
            tok = context.asm_t[first:last].strip()
            context.comments.append(tok)
        if context.asm_t[context.t] == '\n':
            context.line += 1
            context.newlines.append(context.t)
        context.t += 1

    # if ,() token, insert token
    if context.t < len(context.asm_t) and context.asm_t[context.t] in ",()":
        tok = context.asm_t[context.t]
        context.t += 1
        context.tokens.append(tok)
        context.token_types.append("TOKEN")
        context.i = len(context.tokens) - 1
        return context

    # read string "...." or token
    if context.t < len(context.asm_t) and context.asm_t[context.t] == "\"":
        first = context.t
        context.t += 1
        while context.t < len(context.asm_t) and context.asm_t[context.t] != '\"':
            if context.asm_t[context.t] == '\\':
                context.t += 1
            context.t += 1
        context.t += 1
        last = context.t
        token_type = "STRING"
    elif context.t < len(context.asm_t) and context.asm_t[context.t] == "'":
        first = context.t
        context.t += 1
        while context.t < len(context.asm_t) and context.asm_t[context.t] != '\'':
            if context.asm_t[context.t] == '\\':
                context.t += 1
            context.t += 1
        context.t += 1
        last = context.t
        token_type = "STRING"
    else:
        first = context.t
        while context.t < len(context.asm_t) and context.asm_t[context.t] not in ",() # \t\n\r":
            context.t += 1
        last = context.t
        token_type = "TOKEN"

    tok = context.asm_t[first:last].strip()
    if token_type == "TOKEN":
       if tok.isdigit():
            token_type = "NUMBER"
       elif tok.endswith(':'):
            token_type = "TAG"
       elif tok.startswith('.'):
            token_type ="DIRECTIVE"
       #elif tok.startswith('"\''):
            #token_type ="STRING"

    context.tokens.append(tok)
    context.token_types.append(token_type)
    context.i = len(context.tokens) - 1
    return context

#Functions
#Get the token
def asm_get_token(context):
    return context.tokens[context.i] 

#Get the type_token
def asm_get_token_type(context):
    return context.token_types[context.i] #if context.i < len(context.token_types) else None

#Verify if the token matches with the text
def asm_is_token(context, text):
    return asm_get_token(context) == text.strip()

#Verify if the token matches any elements in the list
def asm_is_token_arr(context, arr):
    return any(asm_get_token(context) == item.strip() for item in arr)

#Analyze with error context.
def asm_lang_error(context, msg_error):
    line2 = context.newlines[-1] + 1 if context.newlines else 0
    line1 = context.newlines[-2] + 1 if len(context.newlines) > 1 else 0
    low_i = line1

    high_i = min(context.t - 1, line2 + 32)
    while high_i + 1 < len(context.asm_t) and context.asm_t[high_i + 1] != '\n':
        high_i += 1
    line3 = high_i + 2

    high_i += 1
    while high_i + 1 < len(context.asm_t) and context.asm_t[high_i + 1] != '\n':
        high_i += 1
    high_i += 1

    context.error = "<br><pre class='border rounded p-3 bg-dark text-white'>...\n"
    for i in range(low_i, high_i):
        if i == line1:
            context.error += " " + str(context.line - 1) + "\t"
        if i == line2:
            context.error += "*" + str(context.line) + "\t"
        if i == line3:
            context.error += " " + str(context.line + 1) + "\t"
        context.error += context.asm_t[i] if i < len(context.asm_t) else "<EOF>"
    context.error += "\n...\n</pre>(*) PROBLEM AROUND LINE " + str(context.line) + ": <br>" + msg_error + ".<br>"

    return context

#Get the current context
def asm_get_label_context(context):
    return {'t': context.t, 'line': context.line, 'newlines': context.newlines[:]}

#Set the context for the label
def asm_set_label_context(context, label_context):
    context.t = label_context['t']
    context.line = label_context['line']
    context.newlines = label_context['newlines']

#Get all comments
def asm_get_comments(context):
    return '\n'.join(context.comments)

#Resets the list of comments
def asm_reset_comments(context):
    context.comments = []