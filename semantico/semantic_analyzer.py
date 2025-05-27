
class SemanticError(Exception):

    pass

#  Analizador

class SemanticAnalyzer:
    def __init__(self, tables):

        self.tables = tables

    def analyze(self, tokens):
        pos = 0
        while pos < len(tokens):
            token_type, value, *_ = tokens[pos]
            if token_type == 'SELECT':
                pos = self.check_select(tokens, pos)
            elif token_type == 'INSERT':
                pos = self.check_insert(tokens, pos)
            elif token_type == 'UPDATE':
                pos = self.check_update(tokens, pos)
            elif token_type == 'DELETE':
                pos = self.check_delete(tokens, pos)
            elif token_type == 'FUNCTION':
                pos = self.skip_function(tokens, pos)
            else:
                pos += 1
        return True

#  Analiza cada token en busca de errores semanticos y continua la posicion

    def _expect_token(self, tokens, pos, expected_type, error_message):

        if pos >= len(tokens) or tokens[pos][0] != expected_type:
            raise SemanticError(error_message)
        return pos + 1

#  Analiza una sentencia SELECT

    def check_select(self, tokens, pos):

        pos = self._expect_token(tokens, pos, 'SELECT', "Se esperaba SELECT")
        columns = []
        while pos < len(tokens) and tokens[pos][0] == 'IDENTIFIER':
            columns.append(tokens[pos][1])
            pos += 1
            if pos < len(tokens) and tokens[pos][0] == 'COMMA':
                pos += 1
            else:
                break

        pos = self._expect_token(tokens, pos, 'FROM', "Falta FROM despues de SELECT")
        table = tokens[pos][1]
        pos += 1

        if table not in self.tables:
            raise SemanticError(f"La tabla '{table}' No existe")

        for col in columns:
            if col not in self.tables[table]:
                raise SemanticError(f"La columna '{col}' no existe en '{table}'")

        if pos < len(tokens) and tokens[pos][0] == 'WHERE':
            pos = self.check_where_clause(tokens, pos, table)

        return self.skip_to_next_statement(tokens, pos)


#  Analiza una sentencia INSERT

    def check_insert(self, tokens, pos):

        pos = self._expect_token(tokens, pos, 'INSERT', "Se esperaba INSERT")
        pos = self._expect_token(tokens, pos, 'INTO', "Falta INTO después de INSERT")
        table = tokens[pos][1]
        pos += 1

        if table not in self.tables:
            raise SemanticError(f"La tabla '{table}' no existe")

        pos = self._expect_token(tokens, pos, 'VALUES', "Falta VALUES en INSERT")
        pos = self._expect_token(tokens, pos, 'LPAREN', "Falta paréntesis en VALUES")

        values = []
        column_names = list(self.tables[table].keys())
        while pos < len(tokens) and tokens[pos][0] in ('STRING', 'NUMBER', 'NULL'):
            values.append(tokens[pos][1])
            pos += 1
            if pos < len(tokens) and tokens[pos][0] == 'COMMA':
                pos += 1
            else:
                break

        pos = self._expect_token(tokens, pos, 'RPAREN', "Falta cierre de paréntesis en VALUES")

        if len(values) != len(column_names):
            raise SemanticError(f"Se esperaban {len(column_names)} valores, se recibieron {len(values)}")

        for i, column_name in enumerate(column_names):
            expected_type = self.tables[table][column_name]
            value_type = self.get_value_type(values[i])
            if value_type != expected_type and not self.is_compatible_type(value_type, expected_type):
                raise SemanticError(f"Tipo de dato incorrecto para la columna '{column_name}'. Se esperaba {expected_type}, se recibió {value_type}")

        return self.skip_to_next_statement(tokens, pos)

#  Analiza una sentencia UPDATE

    def check_update(self, tokens, pos):

        pos = self._expect_token(tokens, pos, 'UPDATE', "Se esperaba UPDATE")
        table_name = tokens[pos][1]
        pos += 1

        if table_name not in self.tables:
            raise SemanticError(f"La tabla '{table_name}' no existe")

        pos = self._expect_token(tokens, pos, 'SET', "Falta SET en UPDATE")

        while pos < len(tokens) and tokens[pos][0] == 'IDENTIFIER':
            column_name = tokens[pos][1]
            if column_name not in self.tables[table_name]:
                raise SemanticError(f"La columna '{column_name}' no existe en la tabla '{table_name}'")
            pos += 1
            pos = self._expect_token(tokens, pos, 'EQ', "Falta '=' en la asignación de UPDATE")

            value = tokens[pos][1]
            value_type = self.get_value_type(value)
            expected_type = self.tables[table_name][column_name]

            if value_type != expected_type and not self.is_compatible_type(value_type, expected_type):
                raise SemanticError(f"Tipo de dato incorrecto para la columna '{column_name}'. Se esperaba {expected_type}, se recibió {value_type}")
            pos += 1
            if pos < len(tokens) and tokens[pos][0] == 'COMMA':
                pos += 1
            else:
                break
        if pos < len(tokens) and tokens[pos][0] == 'WHERE':
            pos = self.check_where_clause(tokens, pos, table_name)
        return self.skip_to_next_statement(tokens, pos)

#  Analiza una sentencia DELETE

    def check_delete(self, tokens, pos):

        pos = self._expect_token(tokens, pos, 'DELETE', "Se esperaba DELETE")
        pos = self._expect_token(tokens, pos, 'FROM', "Falta FROM en DELETE")
        table_name = tokens[pos][1]
        pos += 1

        if table_name not in self.tables:
            raise SemanticError(f"La tabla '{table_name}' No existe")

        if pos < len(tokens) and tokens[pos][0] == 'WHERE':
            pos = self.check_where_clause(tokens, pos, table_name)
        return self.skip_to_next_statement(tokens, pos)


# Analizar donde se muestre la clausula WHERE

    def check_where_clause(self, tokens, pos, table_name):

        pos = self._expect_token(tokens, pos, 'WHERE', "Se esperaba WHERE")
        while pos < len(tokens) and tokens[pos][0] != 'SEMICOLON':
            if tokens[pos][0] == 'IDENTIFIER':
                column_name = tokens[pos][1]
                if column_name not in self.tables[table_name]:
                    raise SemanticError(f"La columna '{column_name}' no existe en la tabla '{table_name}'")
                pos += 1
                if pos >= len(tokens) or tokens[pos][0] not in ('EQUAL', 'NOT_EQUAL', 'LESS_THAN', 'GREATER_THAN', 'LESS_OR_EQUAL', 'GREATER_OR_EQUAL'):
                    raise SemanticError("Se esperaba un operador de comparación en WHERE")
                pos += 1
                if pos >= len(tokens):
                    raise SemanticError("Falta valor de comparacion en WHERE")
                value_type = self.get_value_type(tokens[pos][1])
                expected_type = self.tables[table_name][column_name]
                if value_type != expected_type and not self.is_compatible_type(value_type, expected_type):
                     raise SemanticError(f"Tipo de dato incorrecto en la condición WHERE para la columna '{column_name}'. Se esperaba {expected_type}, se recibió {value_type}")
                pos += 1
            elif tokens[pos][0] in ('AND', 'OR', 'NOT'):
                pos += 1
            elif tokens[pos][0] == 'LPAREN':
                pos += 1
            elif tokens[pos][0] == 'RPAREN':
                pos += 1
            else:
                pos += 1
        return pos


#  Omitir el Codifo de una funcion

    def skip_function(self, tokens, pos):

        pos += 1
        while pos < len(tokens) and tokens[pos][0] != 'END':
            pos += 1
        if pos < len(tokens) and tokens[pos][0] == 'END':
            return pos + 1
        else:
            raise SemanticError("Falta 'END' para cerrar la funcion")


    def skip_to_next_statement(self, tokens, pos):

        while pos < len(tokens) and tokens[pos][0] != 'SEMICOLON':
            pos += 1
        if pos < len(tokens) and tokens[pos][0] == 'SEMICOLON':
            return pos + 1
        return pos

# Determinar el tipp de dato
    def get_value_type(self, value):

        if value is None:
            return 'NULL'
        if isinstance(value, str) and value.upper() == 'NULL':
            return 'NULL'
        try:
            int(value)
            return 'INT'
        except ValueError:
            try:
                float(value)
                return 'DECIMAL'
            except ValueError:
                return 'VARCHAR'
        return 'VARCHAR'

# compatibilidad de los tipos de variables

    def is_compatible_type(self, value_type, expected_type):

        if value_type == expected_type:
            return True
        if value_type == 'INT' and expected_type == 'DECIMAL':
            return True
        if value_type == 'NULL':
            return True
        return False
