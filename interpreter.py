"""
Interpreter Module

Implements the interpreter for the mini programming language, including:
- Tokenizer: Decomposes source code strings into tokens
- Parser: Parses syntax structures and checks constraints
- Executor: Executes parsed programs
"""

from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import re
from bot import Bot
from world import World


class TokenType(Enum):
    """Token type enumeration"""
    # Action instructions
    MOVE = "MOVE"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    PICK = "PICK"
    OPEN = "OPEN"
    
    # Control structures
    IF = "IF"
    ELSE = "ELSE"
    ENDIF = "ENDIF"
    LOOP = "LOOP"
    ENDLOOP = "ENDLOOP"
    TIMES = "TIMES"
    END = "END"
    
    # Sensors
    FRONT_CLEAR = "FRONT_CLEAR"
    ON_KEY = "ON_KEY"
    AT_DOOR = "AT_DOOR"
    AT_EXIT = "AT_EXIT"
    HAVE_KEY = "HAVE_KEY"
    
    # Logical operators
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Others
    COLON = ":"
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    WHITESPACE = "WHITESPACE"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


class Token:
    """Token class"""
    
    def __init__(self, token_type: TokenType, value: str, line: int, column: int):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"


class NestingDepthExceededError(Exception):
    """Nesting depth exceeded exception"""
    pass


class LoopLimitExceededError(Exception):
    """Loop limit exceeded exception"""
    pass


class InvalidTokenError(Exception):
    """Invalid token exception"""
    pass


class ParserError(Exception):
    """Parser error exception"""
    pass


class Tokenizer:
    """Lexical analyzer"""
    
    def __init__(self):
        # Define keyword mapping
        self.keywords = {
            'MOVE': TokenType.MOVE,
            'LEFT': TokenType.LEFT,
            'RIGHT': TokenType.RIGHT,
            'PICK': TokenType.PICK,
            'OPEN': TokenType.OPEN,
            'IF': TokenType.IF,
            'ELSE': TokenType.ELSE,
            'ENDIF': TokenType.ENDIF,
            'LOOP': TokenType.LOOP,
            'ENDLOOP': TokenType.ENDLOOP,
            'TIMES': TokenType.TIMES,
            'END': TokenType.END,
            'FRONT_CLEAR': TokenType.FRONT_CLEAR,
            'ON_KEY': TokenType.ON_KEY,
            'AT_DOOR': TokenType.AT_DOOR,
            'AT_EXIT': TokenType.AT_EXIT,
            'HAVE_KEY': TokenType.HAVE_KEY,
            'AND': TokenType.AND,
            'OR': TokenType.OR,
            'NOT': TokenType.NOT,
        }
        
        # Check that keyword count doesn't exceed 20
        if len(self.keywords) > 20:
            raise ValueError(f"Keyword count ({len(self.keywords)}) exceeds 20 limit")
    
    def tokenize(self, source: str) -> List[Token]:
        """
        Decompose source code string into token list
        
        Args:
            source: Source code string
            
        Returns:
            List[Token]: Token list
        """
        tokens = []
        line = 1
        column = 1
        i = 0
        
        while i < len(source):
            char = source[i]
            
            # Skip whitespace characters
            if char.isspace():
                if char == '\n':
                    line += 1
                    column = 1
                else:
                    column += 1
                i += 1
                continue
            
            # Handle numbers
            if char.isdigit():
                number = ""
                start_column = column
                while i < len(source) and source[i].isdigit():
                    number += source[i]
                    i += 1
                    column += 1
                tokens.append(Token(TokenType.NUMBER, number, line, start_column))
                continue
            
            # Handle identifiers and keywords
            if char.isalpha():
                identifier = ""
                start_column = column
                while i < len(source) and (source[i].isalnum() or source[i] == '_'):
                    identifier += source[i]
                    i += 1
                    column += 1
                
                # Check if it's a keyword
                if identifier.upper() in self.keywords:
                    token_type = self.keywords[identifier.upper()]
                    tokens.append(Token(token_type, identifier.upper(), line, start_column))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, identifier, line, start_column))
                continue
            
            # Handle colon
            if char == ':':
                tokens.append(Token(TokenType.COLON, ':', line, column))
                i += 1
                column += 1
                continue
            
            # Unknown character
            raise InvalidTokenError(f"Unknown character '{char}' at line {line}, column {column}")
        
        # Add EOF token
        tokens.append(Token(TokenType.EOF, '', line, column))
        return tokens


class ASTNode:
    """Abstract syntax tree node base class"""
    
    def __init__(self, token: Token):
        self.token = token
        self.children = []


class StatementNode(ASTNode):
    """Statement node"""
    pass


class IfStatementNode(ASTNode):
    """IF statement node"""
    
    def __init__(self, token: Token, condition, then_body, else_body=None):
        super().__init__(token)
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body


class LoopStatementNode(ASTNode):
    """LOOP statement node"""
    
    def __init__(self, token: Token, times: int, body):
        super().__init__(token)
        self.times = times
        self.body = body


class ConditionNode(ASTNode):
    """Condition node"""
    
    def __init__(self, token: Token, operator: str = None, left=None, right=None):
        super().__init__(token)
        self.operator = operator
        self.left = left
        self.right = right


class Parser:
    """Syntax analyzer"""
    
    def __init__(self):
        self.tokens = []
        self.current = 0
        self.max_nesting_depth = 3
        self.max_loop_iterations = 50
    
    def parse(self, tokens: List[Token]) -> List[ASTNode]:
        """
        Parse token list into AST
        
        Args:
            tokens: Token list
            
        Returns:
            List[ASTNode]: AST node list
        """
        self.tokens = tokens
        self.current = 0
        
        statements = []
        while not self.is_at_end():
            if self.peek().type == TokenType.EOF:
                break
            statements.append(self.parse_statement(0))
        
        return statements
    
    def parse_statement(self, nesting_depth: int) -> ASTNode:
        """
        Parse statement
        
        Args:
            nesting_depth: Current nesting depth
            
        Returns:
            ASTNode: Parsed statement node
        """
        if nesting_depth > self.max_nesting_depth:
            raise NestingDepthExceededError(
                f"Nesting depth ({nesting_depth}) exceeds limit ({self.max_nesting_depth})"
            )
        
        token = self.peek()
        
        if token.type == TokenType.IF:
            return self.parse_if_statement(nesting_depth)
        elif token.type == TokenType.LOOP:
            return self.parse_loop_statement(nesting_depth)
        elif token.type == TokenType.MOVE:
            self.advance()
            return StatementNode(token)
        elif token.type == TokenType.LEFT:
            self.advance()
            return StatementNode(token)
        elif token.type == TokenType.RIGHT:
            self.advance()
            return StatementNode(token)
        elif token.type == TokenType.PICK:
            self.advance()
            return StatementNode(token)
        elif token.type == TokenType.OPEN:
            self.advance()
            return StatementNode(token)
        elif token.type == TokenType.END:
            self.advance()
            return StatementNode(token)
        else:
            raise ParserError(f"Unexpected token: {token}")
    
    def parse_if_statement(self, nesting_depth: int) -> IfStatementNode:
        """Parse IF statement"""
        if_token = self.advance()  # Consume IF
        
        # Parse condition
        condition = self.parse_condition()
        
        # Consume colon
        if self.peek().type != TokenType.COLON:
            raise ParserError("IF statement missing colon")
        self.advance()
        
        # Parse then branch
        then_body = []
        while not self.is_at_end() and self.peek().type not in [TokenType.ELSE, TokenType.ENDIF]:
            then_body.append(self.parse_statement(nesting_depth + 1))
        
        # Parse else branch (if exists)
        else_body = None
        if self.peek().type == TokenType.ELSE:
            self.advance()  # Consume ELSE
            if self.peek().type != TokenType.COLON:
                raise ParserError("ELSE missing colon")
            self.advance()
            
            else_body = []
            while not self.is_at_end() and self.peek().type != TokenType.ENDIF:
                else_body.append(self.parse_statement(nesting_depth + 1))
        
        # Consume ENDIF
        if self.peek().type != TokenType.ENDIF:
            raise ParserError("IF statement missing ENDIF")
        self.advance()
        
        return IfStatementNode(if_token, condition, then_body, else_body)
    
    def parse_loop_statement(self, nesting_depth: int) -> LoopStatementNode:
        """Parse LOOP statement"""
        loop_token = self.advance()  # Consume LOOP
        
        # Parse loop count
        if self.peek().type != TokenType.NUMBER:
            raise ParserError("LOOP statement missing number")
        times_token = self.advance()
        times = int(times_token.value)
        
        # Check loop limit
        if times > self.max_loop_iterations:
            raise LoopLimitExceededError(
                f"Loop count ({times}) exceeds limit ({self.max_loop_iterations})"
            )
        
        # Consume colon (simplified syntax, no TIMES keyword needed)
        if self.peek().type != TokenType.COLON:
            raise ParserError("LOOP statement missing colon")
        self.advance()
        
        # Parse loop body
        body = []
        while not self.is_at_end() and self.peek().type != TokenType.ENDLOOP:
            body.append(self.parse_statement(nesting_depth + 1))
        
        # Consume ENDLOOP
        if self.peek().type != TokenType.ENDLOOP:
            raise ParserError("LOOP statement missing ENDLOOP")
        self.advance()
        
        return LoopStatementNode(loop_token, times, body)
    
    def parse_condition(self) -> ConditionNode:
        """Parse condition expression supporting NOT, AND, OR with precedence"""
        return self.parse_or_condition()
    
    def parse_or_condition(self) -> ConditionNode:
        left = self.parse_and_condition()
        while self.peek().type == TokenType.OR:
            op_token = self.advance()
            right = self.parse_and_condition()
            left = ConditionNode(op_token, "OR", left, right)
        return left
    
    def parse_and_condition(self) -> ConditionNode:
        left = self.parse_not_condition()
        while self.peek().type == TokenType.AND:
            op_token = self.advance()
            right = self.parse_not_condition()
            left = ConditionNode(op_token, "AND", left, right)
        return left
    
    def parse_not_condition(self) -> ConditionNode:
        token = self.peek()
        if token.type == TokenType.NOT:
            op_token = self.advance()
            operand = self.parse_not_condition()
            return ConditionNode(op_token, "NOT", operand)
        return self.parse_primary_condition()
    
    def parse_primary_condition(self) -> ConditionNode:
        token = self.peek()
        
        if token.type in [TokenType.FRONT_CLEAR, TokenType.ON_KEY, TokenType.AT_DOOR, TokenType.AT_EXIT, TokenType.HAVE_KEY]:
            self.advance()
            return ConditionNode(token)
        elif token.type == TokenType.IDENTIFIER:
            # Check if it's a valid sensor
            if token.value.upper() in ['FRONT_CLEAR', 'ON_KEY', 'AT_DOOR', 'AT_EXIT', 'HAVE_KEY']:
                self.advance()
                return ConditionNode(Token(token.type, token.value.upper(), token.line, token.column))
            else:
                raise ParserError(f"Invalid sensor: {token.value}")
        else:
            raise ParserError(f"Unexpected condition token: {token}")
    
    def peek(self) -> Token:
        """Peek at current token"""
        if self.current >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.current]
    
    def advance(self) -> Token:
        """Advance to next token"""
        if not self.is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]
    
    def is_at_end(self) -> bool:
        """Check if reached end"""
        return self.current >= len(self.tokens)


class Executor:
    """Executor"""
    
    def __init__(self, world: World, bot: Bot):
        self.world = world
        self.bot = bot
        self.execution_count = 0
        self.max_executions = 1000  # Prevent infinite execution
    
    def execute(self, ast_nodes: List[ASTNode]) -> bool:
        """
        Execute AST node list
        
        Args:
            ast_nodes: AST node list
            
        Returns:
            bool: Whether execution was successful
        """
        try:
            for node in ast_nodes:
                if self.execution_count >= self.max_executions:
                    raise RuntimeError("Execution count exceeded limit")
                
                self.execute_node(node)
                
                # Check if reached exit
                if self.bot.is_on_exit():
                    return True
                    
        except Exception as e:
            print(f"Execution error: {e}")
            return False
        
        return False
    
    def execute_node(self, node: ASTNode):
        """Execute single AST node"""
        if isinstance(node, StatementNode):
            self.execute_statement(node)
        elif isinstance(node, IfStatementNode):
            self.execute_if_statement(node)
        elif isinstance(node, LoopStatementNode):
            self.execute_loop_statement(node)
        else:
            raise RuntimeError(f"Unknown node type: {type(node)}")
    
    def execute_statement(self, node: StatementNode):
        """Execute statement node"""
        token_type = node.token.type
        
        if token_type == TokenType.MOVE:
            self.bot.move_forward()
        elif token_type == TokenType.LEFT:
            self.bot.turn_left()
        elif token_type == TokenType.RIGHT:
            self.bot.turn_right()
        elif token_type == TokenType.PICK:
            self.bot.pick_key()
        elif token_type == TokenType.OPEN:
            self.bot.open_door()
        elif token_type == TokenType.END:
            pass  # Program end
        
        self.execution_count += 1
    
    def execute_if_statement(self, node: IfStatementNode):
        """Execute IF statement"""
        if self.evaluate_condition(node.condition):
            for stmt in node.then_body:
                self.execute_node(stmt)
        elif node.else_body:
            for stmt in node.else_body:
                self.execute_node(stmt)
    
    def execute_loop_statement(self, node: LoopStatementNode):
        """Execute LOOP statement"""
        for _ in range(node.times):
            for stmt in node.body:
                self.execute_node(stmt)
                # Check if reached exit
                if self.bot.is_on_exit():
                    break
            if self.bot.is_on_exit():
                break
    
    def evaluate_condition(self, condition: ConditionNode) -> bool:
        """Evaluate condition expression"""
        if condition.operator == "NOT":
            return not self.evaluate_condition(condition.left)
        if condition.operator == "AND":
            return self.evaluate_condition(condition.left) and self.evaluate_condition(condition.right)
        if condition.operator == "OR":
            return self.evaluate_condition(condition.left) or self.evaluate_condition(condition.right)
        
        # Basic sensor conditions
        if condition.token.type == TokenType.FRONT_CLEAR:
            return self.bot.front_is_clear()
        elif condition.token.type == TokenType.ON_KEY:
            return self.bot.is_on_key()
        elif condition.token.type == TokenType.AT_DOOR:
            return self.bot.is_on_door()
        elif condition.token.type == TokenType.AT_EXIT:
            return self.bot.is_on_exit()
        elif condition.token.type == TokenType.HAVE_KEY:
            return self.bot.have_key
        
        return False


class Interpreter:
    """Main interpreter class"""
    
    def __init__(self, world: World, bot: Bot):
        self.world = world
        self.bot = bot
        self.tokenizer = Tokenizer()
        self.parser = Parser()
        self.executor = Executor(world, bot)
    
    def run(self, source: str) -> bool:
        """
        Run source code
        
        Args:
            source: Source code string
            
        Returns:
            bool: Whether execution was successful
        """
        try:
            # Lexical analysis
            tokens = self.tokenizer.tokenize(source)
            
            # Syntax analysis
            ast = self.parser.parse(tokens)
            
            # Execution
            return self.executor.execute(ast)
            
        except Exception as e:
            print(f"Interpreter error: {e}")
            return False
    
    def get_token_count(self, source: str) -> int:
        """Get token count of source code"""
        try:
            tokens = self.tokenizer.tokenize(source)
            # Filter out whitespace and EOF tokens
            meaningful_tokens = [t for t in tokens if t.type not in [TokenType.WHITESPACE, TokenType.EOF]]
            return len(meaningful_tokens)
        except:
            return 0 