# from typing import List, Tuple, Optional, Any, Dict
from dataclasses import dataclass
from enum import Enum
import json
from typing import List, Optional,Tuple, Any, Dict

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
            elif token_type == 'CREATE':
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
        
        while True:
            token_type, *_ = self.current_token()
            if token_type == 'END':
                self.match('END')
                break
            elif token_type in {'SELECT', 'INSERT', 'UPDATE','CREATE'}:
                self.parse_statement()
            else:
                raise SyntaxError(f"Token inesperado dentro de la función: {token_type}")

    def parse_statement(self):
        token_type, *_ = self.current_token()
        if token_type == 'SELECT':
            self.parse_select()
        elif token_type == 'INSERT':
            self.parse_insert()
        elif token_type == 'UPDATE':
            self.parse_update()
        elif token_type == 'CREATE':
            self.parse_update()
        else:
            raise SyntaxError(f"Instrucción desconocida: {token_type}")
   

    def parse_identifier_list(self):
        self.match('IDENTIFIER')
        while self.current_token()[0] == 'COMMA':
            self.match('COMMA')
            self.match('IDENTIFIER')



    def parse_value_list(self):
        self.parse_expression()
        while self.current_token()[0] == 'COMMA':
            self.match('COMMA')
            self.parse_expression()

   
    def parse_condition(self):
        self.parse_expression()  
        op = self.current_token()[0]
        if op not in ('EQ', 'GT', 'LT', 'GE', 'LE', 'NE'):
            raise SyntaxError(f"Operador de comparación inválido: {op}")
        self.match(op)
        self.parse_expression()  

    def parse_expression(self):
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

# DEFINICIÓN DE TOKENS Y AST

class TokenType(Enum):
    # SQL Keywords
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    FROM = "FROM"
    INTO = "INTO"
    VALUES = "VALUES"
    WHERE = "WHERE"
    SET = "SET"
    FUNCTION = "FUNCTION"
    END = "END"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    RETURN = "RETURN"
    
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    POWER = "POWER"
    
    # Comparison operators
    EQ = "EQ"
    NE = "NE"
    LT = "LT"
    LE = "LE"
    GT = "GT"
    GE = "GE"
    
    # Logical operators
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Punctuation
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    DOT = "DOT"
    
    # Literals and identifiers
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    
    # Special
    EOF = "EOF"
    NEWLINE = "NEWLINE"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    
    def _str_(self):
        return f"Token({self.type.value}, '{self.value}', {self.line}:{self.column})"

# ============================================================================
# NODOS DEL AST (Abstract Syntax Tree)
# ============================================================================

@dataclass
class ASTNode:
    """Clase base para todos los nodos del AST"""
    line: int
    column: int

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

@dataclass
class SelectStatement(ASTNode):
    columns: List['Expression']
    table: str
    where_clause: Optional['Expression'] = None

@dataclass
class InsertStatement(ASTNode):
    table: str
    values: List['Expression']

@dataclass
class UpdateStatement(ASTNode):
    table: str
    assignments: List[Tuple[str, 'Expression']]
    where_clause: Optional['Expression'] = None

@dataclass
class DeleteStatement(ASTNode):
    table: str
    where_clause: Optional['Expression'] = None

@dataclass
class FunctionDeclaration(ASTNode):
    name: str
    parameters: List[str]
    body: List[ASTNode]

@dataclass
class IfStatement(ASTNode):
    condition: 'Expression'
    then_body: List[ASTNode]
    else_body: Optional[List[ASTNode]] = None

@dataclass
class WhileStatement(ASTNode):
    condition: 'Expression'
    body: List[ASTNode]

@dataclass
class ReturnStatement(ASTNode):
    value: Optional['Expression'] = None

@dataclass
class Expression(ASTNode):
    """Clase base para expresiones"""
    pass

@dataclass
class BinaryExpression(Expression):
    left: Expression
    operator: TokenType
    right: Expression

@dataclass
class UnaryExpression(Expression):
    operator: TokenType
    operand: Expression

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Literal(Expression):
    value: Any
    type: str  # 'number', 'string', 'boolean', 'null'

@dataclass
class FunctionCall(Expression):
    name: str
    arguments: List[Expression]

# ============================================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================================

class ParseError(Exception):
    """Excepción base para errores de parsing"""
    def _init_(self, message: str, token: Token):
        self.message = message
        self.token = token
        super()._init_(f"{message} en línea {token.line}, columna {token.column}")

class UnexpectedTokenError(ParseError):
    """Error cuando se encuentra un token inesperado"""
    def _init_(self, expected: str, found: Token):
        message = f"Se esperaba {expected}, pero se encontró '{found.value}' ({found.type.value})"
        super()._init_(message, found)

class UnexpectedEOFError(ParseError):
    """Error cuando se alcanza el final del archivo inesperadamente"""
    def _init_(self, expected: str, token: Token):
        message = f"Final de archivo inesperado. Se esperaba {expected}"
        super()._init_(message, token)

# ============================================================================
# PARSER MEJORADO
# ============================================================================

class ImprovedParser:
    def _init_(self, tokens: List[Tuple[str, str, int, int]]):
        # Convertir tokens al nuevo formato
        self.tokens = []
        for token_type, value, line, col in tokens:
            try:
                token_enum = TokenType(token_type)
            except ValueError:
                # Si el token no está en el enum, tratarlo como IDENTIFIER
                token_enum = TokenType.IDENTIFIER
                value = token_type
            self.tokens.append(Token(token_enum, value, line, col))
        
        # Agregar token EOF si no existe
        if not self.tokens or self.tokens[-1].type != TokenType.EOF:
            last_line = self.tokens[-1].line if self.tokens else 1
            last_col = self.tokens[-1].column if self.tokens else 1
            self.tokens.append(Token(TokenType.EOF, '', last_line, last_col))
        
        self.pos = 0
        self.errors = []

    def current_token(self) -> Token:
        """Obtiene el token actual"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF token

    def peek_token(self, offset: int = 1) -> Token:
        """Mira hacia adelante sin consumir el token"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # EOF token

    def consume(self, expected_type: TokenType = None) -> Token:
        """Consume y retorna el token actual"""
        token = self.current_token()
        
        if expected_type and token.type != expected_type:
            if token.type == TokenType.EOF:
                raise UnexpectedEOFError(expected_type.value, token)
            else:
                raise UnexpectedTokenError(expected_type.value, token)
        
        if self.pos < len(self.tokens) - 1:  # No avanzar más allá del EOF
            self.pos += 1
        
        return token

    def match(self, token_type: TokenType) -> bool:
        """Verifica si el token actual es del tipo esperado"""
        return self.current_token().type == token_type

    def skip_newlines(self):
        """Salta tokens de nueva línea"""
        while self.match(TokenType.NEWLINE):
            self.consume()

    # ========================================================================
    # MÉTODOS DE PARSING PRINCIPALES
    # ========================================================================

    def parse(self) -> Program:
        """Punto de entrada principal del parser"""
        statements = []
        
        try:
            while not self.match(TokenType.EOF):
                self.skip_newlines()
                if self.match(TokenType.EOF):
                    break
                
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
                
                self.skip_newlines()
        
        except ParseError as e:
            self.errors.append(e)
            # Intentar recuperarse saltando al siguiente punto de sincronización
            self.synchronize()
        
        if self.errors:
            self.print_errors()
        
        return Program(statements, 1, 1)

    def parse_statement(self) -> Optional[ASTNode]:
        """Parsea una declaración"""
        token = self.current_token()
        
        try:
            if self.match(TokenType.SELECT):
                return self.parse_select_statement()
            elif self.match(TokenType.INSERT):
                return self.parse_insert_statement()
            elif self.match(TokenType.UPDATE):
                return self.parse_update_statement()
            elif self.match(TokenType.DELETE):
                return self.parse_delete_statement()
            elif self.match(TokenType.FUNCTION):
                return self.parse_function_declaration()
            elif self.match(TokenType.IF):
                return self.parse_if_statement()
            elif self.match(TokenType.WHILE):
                return self.parse_while_statement()
            elif self.match(TokenType.RETURN):
                return self.parse_return_statement()
            else:
                raise UnexpectedTokenError("declaración válida", token)
        
        except ParseError as e:
            self.errors.append(e)
            self.synchronize()
            return None

    def parse_select_statement(self) -> SelectStatement:
        """Parsea una declaración SELECT"""
        token = self.consume(TokenType.SELECT)
        
        # Parsear lista de columnas
        columns = self.parse_expression_list()
        
        self.consume(TokenType.FROM)
        table_token = self.consume(TokenType.IDENTIFIER)
        
        # Cláusula WHERE opcional
        where_clause = None
        if self.match(TokenType.WHERE):
            self.consume(TokenType.WHERE)
            where_clause = self.parse_expression()
        
        self.consume(TokenType.SEMICOLON)
        
        return SelectStatement(columns, table_token.value, where_clause, 
                             token.line, token.column)

    def parse_insert_statement(self) -> InsertStatement:
        """Parsea una declaración INSERT"""
        token = self.consume(TokenType.INSERT)
        self.consume(TokenType.INTO)
        table_token = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.VALUES)
        self.consume(TokenType.LPAREN)
        
        values = self.parse_expression_list()
        
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.SEMICOLON)
        
        return InsertStatement(table_token.value, values, token.line, token.column)

    def parse_update_statement(self) -> UpdateStatement:
        """Parsea una declaración UPDATE"""
        token = self.consume(TokenType.UPDATE)
        table_token = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.SET)
        
        # Parsear asignaciones
        assignments = []
        column_token = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.EQ)
        value = self.parse_expression()
        assignments.append((column_token.value, value))
        
        while self.match(TokenType.COMMA):
            self.consume(TokenType.COMMA)
            column_token = self.consume(TokenType.IDENTIFIER)
            self.consume(TokenType.EQ)
            value = self.parse_expression()
            assignments.append((column_token.value, value))
        
        # Cláusula WHERE opcional
        where_clause = None
        if self.match(TokenType.WHERE):
            self.consume(TokenType.WHERE)
            where_clause = self.parse_expression()
        
        self.consume(TokenType.SEMICOLON)
        
        return UpdateStatement(table_token.value, assignments, where_clause,
                             token.line, token.column)

    def parse_delete_statement(self) -> DeleteStatement:
        """Parsea una declaración DELETE"""
        token = self.consume(TokenType.DELETE)
        self.consume(TokenType.FROM)
        table_token = self.consume(TokenType.IDENTIFIER)
        
        # Cláusula WHERE opcional
        where_clause = None
        if self.match(TokenType.WHERE):
            self.consume(TokenType.WHERE)
            where_clause = self.parse_expression()
        
        self.consume(TokenType.SEMICOLON)
        
        return DeleteStatement(table_token.value, where_clause, 
                             token.line, token.column)

    def parse_function_declaration(self) -> FunctionDeclaration:
        """Parsea una declaración de función"""
        token = self.consume(TokenType.FUNCTION)
        name_token = self.consume(TokenType.IDENTIFIER)
        
        # Parámetros opcionales
        parameters = []
        if self.match(TokenType.LPAREN):
            self.consume(TokenType.LPAREN)
            if not self.match(TokenType.RPAREN):
                param_token = self.consume(TokenType.IDENTIFIER)
                parameters.append(param_token.value)
                
                while self.match(TokenType.COMMA):
                    self.consume(TokenType.COMMA)
                    param_token = self.consume(TokenType.IDENTIFIER)
                    parameters.append(param_token.value)
            
            self.consume(TokenType.RPAREN)
        
        # Cuerpo de la función
        body = []
        while not self.match(TokenType.END) and not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.consume(TokenType.END)
        
        return FunctionDeclaration(name_token.value, parameters, body,
                                 token.line, token.column)

    def parse_if_statement(self) -> IfStatement:
        """Parsea una declaración IF"""
        token = self.consume(TokenType.IF)
        condition = self.parse_expression()
        
        # Cuerpo del IF
        then_body = []
        while not self.match(TokenType.ELSE) and not self.match(TokenType.END) and not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                then_body.append(stmt)
        
        # Cláusula ELSE opcional
        else_body = None
        if self.match(TokenType.ELSE):
            self.consume(TokenType.ELSE)
            else_body = []
            while not self.match(TokenType.END) and not self.match(TokenType.EOF):
                stmt = self.parse_statement()
                if stmt:
                    else_body.append(stmt)
        
        self.consume(TokenType.END)
        
        return IfStatement(condition, then_body, else_body, token.line, token.column)

    def parse_while_statement(self) -> WhileStatement:
        """Parsea una declaración WHILE"""
        token = self.consume(TokenType.WHILE)
        condition = self.parse_expression()
        
        # Cuerpo del WHILE
        body = []
        while not self.match(TokenType.END) and not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.consume(TokenType.END)
        
        return WhileStatement(condition, body, token.line, token.column)

    def parse_return_statement(self) -> ReturnStatement:
        """Parsea una declaración RETURN"""
        token = self.consume(TokenType.RETURN)
        
        # Valor de retorno opcional
        value = None
        if not self.match(TokenType.SEMICOLON):
            value = self.parse_expression()
        
        self.consume(TokenType.SEMICOLON)
        
        return ReturnStatement(value, token.line, token.column)

    # PARSING DE EXPRESIONES CON PRECEDENCIA
  

    def parse_expression_list(self) -> List[Expression]:
        """Parsea una lista de expresiones separadas por comas"""
        expressions = [self.parse_expression()]
        
        while self.match(TokenType.COMMA):
            self.consume(TokenType.COMMA)
            expressions.append(self.parse_expression())
        
        return expressions

    def parse_expression(self) -> Expression:
        """Parsea una expresión (punto de entrada para precedencia)"""
        return self.parse_logical_or()

    def parse_logical_or(self) -> Expression:
        """Parsea OR lógico (menor precedencia)"""
        expr = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            operator = self.consume(TokenType.OR)
            right = self.parse_logical_and()
            expr = BinaryExpression(expr, operator.type, right, 
                                  expr.line, expr.column)
        
        return expr

    def parse_logical_and(self) -> Expression:
        """Parsea AND lógico"""
        expr = self.parse_equality()
        
        while self.match(TokenType.AND):
            operator = self.consume(TokenType.AND)
            right = self.parse_equality()
            expr = BinaryExpression(expr, operator.type, right,
                                  expr.line, expr.column)
        
        return expr

    def parse_equality(self) -> Expression:
        """Parsea operadores de igualdad"""
        expr = self.parse_comparison()
        
        while self.current_token().type in [TokenType.EQ, TokenType.NE]:
            operator = self.consume()
            right = self.parse_comparison()
            expr = BinaryExpression(expr, operator.type, right,
                                  expr.line, expr.column)
        
        return expr

    def parse_comparison(self) -> Expression:
        """Parsea operadores de comparación"""
        expr = self.parse_term()
        
        while self.current_token().type in [TokenType.LT, TokenType.LE, 
                                           TokenType.GT, TokenType.GE]:
            operator = self.consume()
            right = self.parse_term()
            expr = BinaryExpression(expr, operator.type, right,
                                  expr.line, expr.column)
        
        return expr

    def parse_term(self) -> Expression:
        """Parsea suma y resta"""
        expr = self.parse_factor()
        
        while self.current_token().type in [TokenType.PLUS, TokenType.MINUS]:
            operator = self.consume()
            right = self.parse_factor()
            expr = BinaryExpression(expr, operator.type, right,
                                  expr.line, expr.column)
        
        return expr

    def parse_factor(self) -> Expression:
        """Parsea multiplicación, división y módulo"""
        expr = self.parse_unary()
        
        while self.current_token().type in [TokenType.MUL, TokenType.DIV, TokenType.MOD]:
            operator = self.consume()
            right = self.parse_unary()
            expr = BinaryExpression(expr, operator.type, right,
                                  expr.line, expr.column)
        
        return expr

    def parse_unary(self) -> Expression:
        """Parsea operadores unarios"""
        if self.current_token().type in [TokenType.NOT, TokenType.MINUS]:
            operator = self.consume()
            operand = self.parse_unary()
            return UnaryExpression(operator.type, operand, operator.line, operator.column)
        
        return self.parse_power()

    def parse_power(self) -> Expression:
        """Parsea exponenciación (mayor precedencia)"""
        expr = self.parse_primary()
        
        if self.match(TokenType.POWER):
            operator = self.consume(TokenType.POWER)
            # La exponenciación es asociativa por la derecha
            right = self.parse_power()
            expr = BinaryExpression(expr, operator.type, right,
                                  expr.line, expr.column)
        
        return expr

    def parse_primary(self) -> Expression:
        """Parsea expresiones primarias"""
        token = self.current_token()
        
        if token.type == TokenType.NUMBER:
            self.consume()
            try:
                value = int(token.value)
            except ValueError:
                value = float(token.value)
            return Literal(value, 'number', token.line, token.column)
        
        elif token.type == TokenType.STRING:
            self.consume()
            return Literal(token.value, 'string', token.line, token.column)
        
        elif token.type == TokenType.BOOLEAN:
            self.consume()
            value = token.value.lower() == 'true'
            return Literal(value, 'boolean', token.line, token.column)
        
        elif token.type == TokenType.NULL:
            self.consume()
            return Literal(None, 'null', token.line, token.column)
        
        elif token.type == TokenType.IDENTIFIER:
            self.consume()
            
            # Verificar si es una llamada a función
            if self.match(TokenType.LPAREN):
                self.consume(TokenType.LPAREN)
                args = []
                
                if not self.match(TokenType.RPAREN):
                    args = self.parse_expression_list()
                
                self.consume(TokenType.RPAREN)
                return FunctionCall(token.value, args, token.line, token.column)
            
            return Identifier(token.value, token.line, token.column)
        
        elif token.type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN)
            return expr
        
        else:
            raise UnexpectedTokenError("expresión", token)

    # UTILIDADES Y MANEJO DE ERRORES
   
    def synchronize(self):
        """Busca el siguiente punto de sincronización después de un error"""
        self.pos += 1
        
        while not self.match(TokenType.EOF):
            if self.tokens[self.pos - 1].type == TokenType.SEMICOLON:
                return
            
            if self.current_token().type in [TokenType.SELECT, TokenType.INSERT, 
                                           TokenType.UPDATE, TokenType.DELETE,
                                           TokenType.FUNCTION, TokenType.IF, 
                                           TokenType.WHILE, TokenType.RETURN]:
                return
            
            self.pos += 1

    def print_errors(self):
        """Imprime todos los errores encontrados"""
        print(f"\n Se encontraron {len(self.errors)} errores de sintaxis:")
        for i, error in enumerate(self.errors, 1):
            print(f"  {i}. {error}")

    def get_ast_json(self, node: ASTNode) -> Dict:
        """Convierte el AST a formato JSON para debugging"""
        def serialize_node(n):
            if isinstance(n, list):
                return [serialize_node(item) for item in n]
            elif hasattr(n, '_dict_'):
                result = {'type': n._class.name_}
                for key, value in n._dict_.items():
                    if key not in ['line', 'column']:
                        result[key] = serialize_node(value)
                return result
            else:
                return n
        
        return serialize_node(node)

# ============================================================================
# def test_parser():
       
#     sample_tokens = [
#         ('SELECT', 'SELECT', 1, 1),
#         ('IDENTIFIER', 'nombre', 1, 8),
#         ('COMMA', ',', 1, 14),
#         ('IDENTIFIER', 'edad', 1, 16),
#         ('FROM', 'FROM', 1, 21),
#         ('IDENTIFIER', 'usuarios', 1, 26),
#         ('WHERE', 'WHERE', 1, 35),
#         ('IDENTIFIER', 'edad', 1, 41),
#         ('GT', '>', 1, 46),
#         ('NUMBER', '18', 1, 48),
#         ('SEMICOLON', ';', 1, 51),
        
#         ('INSERT', 'INSERT', 2, 1),
#         ('INTO', 'INTO', 2, 8),
#         ('IDENTIFIER', 'productos', 2, 13),
#         ('VALUES', 'VALUES', 2, 23),
#         ('LPAREN', '(', 2, 30),
#         ('STRING', 'Laptop', 2, 31),
#         ('COMMA', ',', 2, 39),
#         ('NUMBER', '999.99', 2, 41),
#         ('RPAREN', ')', 2, 48),
#         ('SEMICOLON', ';', 2, 49),
#     ]
    
#     parser = ImprovedParser(sample_tokens)
#     ast = parser.parse()
    
#     if not parser.errors:
#         print(" Parsing exitoso!")
#         print("\n AST generado:")
#         ast_json = parser.get_ast_json(ast)
#         print(json.dumps(ast_json, indent=2, ensure_ascii=False))
#     else:
#         print("Errores encontrados durante el parsing")

# if __name__ == "_main_":
#     test_parser() 

