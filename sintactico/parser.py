class SyntaxError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', '', -1, -1)

    def match(self, expected_type):
        token_type, value, line, col = self.current_token()
        if token_type == expected_type:
            self.pos += 1
            return value
        else:
            raise SyntaxError(f"Se esperaba '{expected_type}' pero se encontró '{value}' en línea {line}")

    def parse(self):
        while self.pos < len(self.tokens):
            token_type, *_ = self.current_token()
            if token_type == 'SELECT':
                self.parse_select()
            elif token_type == 'INSERT':
                self.parse_insert()
            elif token_type == 'UPDATE':
                self.parse_update()
            elif token_type == 'FUNCTION':
                self.parse_function()
            elif token_type == 'EOF':
                break
            else:
                raise SyntaxError(f"Instrucción desconocida: {token_type}")

    def parse_select(self):
        self.match('SELECT')
        self.parse_identifier_list()
        self.match('FROM')
        self.match('IDENTIFIER')
        if self.current_token()[0] == 'WHERE':
            self.match('WHERE')
            self.parse_condition()
        self.match('SEMICOLON')

    def parse_insert(self):
        self.match('INSERT')
        self.match('INTO')
        self.match('IDENTIFIER')
        self.match('VALUES')
        self.match('LPAREN')
        self.parse_value_list()
        self.match('RPAREN')
        self.match('SEMICOLON')

    def parse_update(self):
        self.match('UPDATE')
        self.match('IDENTIFIER')
        self.match('SET')
        self.parse_set_list()
        if self.current_token()[0] == 'WHERE':
            self.match('WHERE')
            self.parse_condition()
        self.match('SEMICOLON')

    def parse_set_list(self):
        self.match('IDENTIFIER')   # columna
        self.match('EQ')           # '='
        self.parse_expression()    # valor

        while self.current_token()[0] == 'COMMA':
            self.match('COMMA')
            self.match('IDENTIFIER')
            self.match('EQ')
            self.parse_expression()

    def parse_function(self):
        self.match('FUNCTION')
        self.match('IDENTIFIER')
        while self.current_token()[0] != 'END':
            self.parse()  
        self.match('END')

    def parse_identifier_list(self):
        self.match('IDENTIFIER')
        while self.current_token()[0] == 'COMMA':
            self.match('COMMA')
            self.match('IDENTIFIER')



    def parse_value_list(self):
        # Aquí puedes aceptar valores o expresiones aritméticas
        self.parse_expression()
        while self.current_token()[0] == 'COMMA':
            self.match('COMMA')
            self.parse_expression()

   
    def parse_condition(self):
        self.parse_expression()  # lado izquierdo
        op = self.current_token()[0]
        if op not in ('EQ', 'GT', 'LT', 'GE', 'LE', 'NE'):
            raise SyntaxError(f"Operador de comparación inválido: {op}")
        self.match(op)
        self.parse_expression()  # lado derecho

    def parse_expression(self):
        # parse_expression maneja términos y operadores aritméticos básicos (sin precedencia compleja)
        self.parse_term()
        while self.current_token()[0] in ('PLUS', 'MINUS'):
            self.match(self.current_token()[0])
            self.parse_term()

    def parse_term(self):
        # parse_term maneja factores y operadores multiplicativos
        self.parse_factor()
        while self.current_token()[0] in ('MUL', 'DIV'):
            self.match(self.current_token()[0])
            self.parse_factor()

    def parse_factor(self):
        token_type, value, line, col = self.current_token()
        if token_type in ('IDENTIFIER', 'NUMBER','STRING'):
            self.match(token_type)
        elif token_type == 'LPAREN':
            self.match('LPAREN')
            self.parse_expression()
            self.match('RPAREN')
        else:
            raise SyntaxError(f"Se esperaba IDENTIFIER, NUMBER o '(' en línea {line} pero se encontró '{value}'")

    