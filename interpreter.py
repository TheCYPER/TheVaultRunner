"""
解释器模块

实现迷你编程语言的解释器，包括：
- Tokenizer: 将源代码字符串分解为token
- Parser: 解析语法结构并检查约束
- Executor: 执行解析后的程序
"""

from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import re
from bot import Bot
from world import World


class TokenType(Enum):
    """Token类型枚举"""
    # 动作指令
    MOVE = "MOVE"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    PICK = "PICK"
    OPEN = "OPEN"
    
    # 控制结构
    IF = "IF"
    ELSE = "ELSE"
    ENDIF = "ENDIF"
    LOOP = "LOOP"
    ENDLOOP = "ENDLOOP"
    TIMES = "TIMES"
    END = "END"
    
    # 传感器
    FRONT_CLEAR = "FRONT_CLEAR"
    ON_KEY = "ON_KEY"
    AT_DOOR = "AT_DOOR"
    AT_EXIT = "AT_EXIT"
    HAVE_KEY = "HAVE_KEY"
    
    # 逻辑操作符
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # 其他
    COLON = ":"
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    WHITESPACE = "WHITESPACE"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


class Token:
    """Token类"""
    
    def __init__(self, token_type: TokenType, value: str, line: int, column: int):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"


class NestingDepthExceededError(Exception):
    """嵌套深度超限异常"""
    pass


class LoopLimitExceededError(Exception):
    """循环上限超限异常"""
    pass


class InvalidTokenError(Exception):
    """无效Token异常"""
    pass


class ParserError(Exception):
    """解析错误异常"""
    pass


class Tokenizer:
    """词法分析器"""
    
    def __init__(self):
        # 定义关键词映射
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
        
        # 检查关键词数量不超过20个
        if len(self.keywords) > 20:
            raise ValueError(f"关键词数量({len(self.keywords)})超过20个限制")
    
    def tokenize(self, source: str) -> List[Token]:
        """
        将源代码字符串分解为token列表
        
        Args:
            source: 源代码字符串
            
        Returns:
            List[Token]: token列表
        """
        tokens = []
        line = 1
        column = 1
        i = 0
        
        while i < len(source):
            char = source[i]
            
            # 跳过空白字符
            if char.isspace():
                if char == '\n':
                    line += 1
                    column = 1
                else:
                    column += 1
                i += 1
                continue
            
            # 处理数字
            if char.isdigit():
                number = ""
                start_column = column
                while i < len(source) and source[i].isdigit():
                    number += source[i]
                    i += 1
                    column += 1
                tokens.append(Token(TokenType.NUMBER, number, line, start_column))
                continue
            
            # 处理标识符和关键词
            if char.isalpha():
                identifier = ""
                start_column = column
                while i < len(source) and (source[i].isalnum() or source[i] == '_'):
                    identifier += source[i]
                    i += 1
                    column += 1
                
                # 检查是否为关键词
                if identifier.upper() in self.keywords:
                    token_type = self.keywords[identifier.upper()]
                    tokens.append(Token(token_type, identifier.upper(), line, start_column))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, identifier, line, start_column))
                continue
            
            # 处理冒号
            if char == ':':
                tokens.append(Token(TokenType.COLON, ':', line, column))
                i += 1
                column += 1
                continue
            
            # 未知字符
            raise InvalidTokenError(f"未知字符 '{char}' at line {line}, column {column}")
        
        # 添加EOF token
        tokens.append(Token(TokenType.EOF, '', line, column))
        return tokens


class ASTNode:
    """抽象语法树节点基类"""
    
    def __init__(self, token: Token):
        self.token = token
        self.children = []


class StatementNode(ASTNode):
    """语句节点"""
    pass


class IfStatementNode(ASTNode):
    """IF语句节点"""
    
    def __init__(self, token: Token, condition, then_body, else_body=None):
        super().__init__(token)
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body


class LoopStatementNode(ASTNode):
    """LOOP语句节点"""
    
    def __init__(self, token: Token, times: int, body):
        super().__init__(token)
        self.times = times
        self.body = body


class ConditionNode(ASTNode):
    """条件节点"""
    
    def __init__(self, token: Token, operator: str = None, left=None, right=None):
        super().__init__(token)
        self.operator = operator
        self.left = left
        self.right = right


class Parser:
    """语法分析器"""
    
    def __init__(self):
        self.tokens = []
        self.current = 0
        self.max_nesting_depth = 3
        self.max_loop_iterations = 50
    
    def parse(self, tokens: List[Token]) -> List[ASTNode]:
        """
        解析token列表为AST
        
        Args:
            tokens: token列表
            
        Returns:
            List[ASTNode]: AST节点列表
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
        解析语句
        
        Args:
            nesting_depth: 当前嵌套深度
            
        Returns:
            ASTNode: 解析后的语句节点
        """
        if nesting_depth > self.max_nesting_depth:
            raise NestingDepthExceededError(
                f"嵌套深度({nesting_depth})超过限制({self.max_nesting_depth})"
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
            raise ParserError(f"意外的token: {token}")
    
    def parse_if_statement(self, nesting_depth: int) -> IfStatementNode:
        """解析IF语句"""
        if_token = self.advance()  # 消费IF
        
        # 解析条件
        condition = self.parse_condition()
        
        # 消费冒号
        if self.peek().type != TokenType.COLON:
            raise ParserError("IF语句后缺少冒号")
        self.advance()
        
        # 解析then分支
        then_body = []
        while not self.is_at_end() and self.peek().type not in [TokenType.ELSE, TokenType.ENDIF]:
            then_body.append(self.parse_statement(nesting_depth + 1))
        
        # 解析else分支（如果有）
        else_body = None
        if self.peek().type == TokenType.ELSE:
            self.advance()  # 消费ELSE
            if self.peek().type != TokenType.COLON:
                raise ParserError("ELSE后缺少冒号")
            self.advance()
            
            else_body = []
            while not self.is_at_end() and self.peek().type != TokenType.ENDIF:
                else_body.append(self.parse_statement(nesting_depth + 1))
        
        # 消费ENDIF
        if self.peek().type != TokenType.ENDIF:
            raise ParserError("IF语句缺少ENDIF")
        self.advance()
        
        return IfStatementNode(if_token, condition, then_body, else_body)
    
    def parse_loop_statement(self, nesting_depth: int) -> LoopStatementNode:
        """解析LOOP语句"""
        loop_token = self.advance()  # 消费LOOP
        
        # 解析循环次数
        if self.peek().type != TokenType.NUMBER:
            raise ParserError("LOOP语句后缺少数字")
        times_token = self.advance()
        times = int(times_token.value)
        
        # 检查循环上限
        if times > self.max_loop_iterations:
            raise LoopLimitExceededError(
                f"循环次数({times})超过上限({self.max_loop_iterations})"
            )
        
        # 消费冒号（简化语法，不需要TIMES关键字）
        if self.peek().type != TokenType.COLON:
            raise ParserError("LOOP语句后缺少冒号")
        self.advance()
        
        # 解析循环体
        body = []
        while not self.is_at_end() and self.peek().type != TokenType.ENDLOOP:
            body.append(self.parse_statement(nesting_depth + 1))
        
        # 消费ENDLOOP
        if self.peek().type != TokenType.ENDLOOP:
            raise ParserError("LOOP语句缺少ENDLOOP")
        self.advance()
        
        return LoopStatementNode(loop_token, times, body)
    
    def parse_condition(self) -> ConditionNode:
        """解析条件表达式"""
        token = self.peek()
        
        if token.type in [TokenType.FRONT_CLEAR, TokenType.ON_KEY, TokenType.AT_DOOR, TokenType.AT_EXIT, TokenType.HAVE_KEY]:
            self.advance()
            return ConditionNode(token)
        elif token.type == TokenType.NOT:
            self.advance()
            operand = self.parse_condition()
            return ConditionNode(token, "NOT", operand)
        elif token.type == TokenType.IDENTIFIER:
            # 检查是否为有效的传感器
            if token.value.upper() in ['FRONT_CLEAR', 'ON_KEY', 'AT_DOOR', 'AT_EXIT', 'HAVE_KEY']:
                self.advance()
                return ConditionNode(Token(token.type, token.value.upper(), token.line, token.column))
            else:
                raise ParserError(f"无效的传感器: {token.value}")
        else:
            raise ParserError(f"意外的条件token: {token}")
    
    def peek(self) -> Token:
        """查看当前token"""
        if self.current >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.current]
    
    def advance(self) -> Token:
        """前进到下一个token"""
        if not self.is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]
    
    def is_at_end(self) -> bool:
        """检查是否到达末尾"""
        return self.current >= len(self.tokens)


class Executor:
    """执行器"""
    
    def __init__(self, world: World, bot: Bot):
        self.world = world
        self.bot = bot
        self.execution_count = 0
        self.max_executions = 1000  # 防止无限执行
    
    def execute(self, ast_nodes: List[ASTNode]) -> bool:
        """
        执行AST节点列表
        
        Args:
            ast_nodes: AST节点列表
            
        Returns:
            bool: 执行是否成功
        """
        try:
            for node in ast_nodes:
                if self.execution_count >= self.max_executions:
                    raise RuntimeError("执行次数超过限制")
                
                self.execute_node(node)
                
                # 检查是否到达出口
                if self.bot.is_on_exit():
                    return True
                    
        except Exception as e:
            print(f"执行错误: {e}")
            return False
        
        return False
    
    def execute_node(self, node: ASTNode):
        """执行单个AST节点"""
        if isinstance(node, StatementNode):
            self.execute_statement(node)
        elif isinstance(node, IfStatementNode):
            self.execute_if_statement(node)
        elif isinstance(node, LoopStatementNode):
            self.execute_loop_statement(node)
        else:
            raise RuntimeError(f"未知的节点类型: {type(node)}")
    
    def execute_statement(self, node: StatementNode):
        """执行语句节点"""
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
            pass  # 程序结束
        
        self.execution_count += 1
    
    def execute_if_statement(self, node: IfStatementNode):
        """执行IF语句"""
        if self.evaluate_condition(node.condition):
            for stmt in node.then_body:
                self.execute_node(stmt)
        elif node.else_body:
            for stmt in node.else_body:
                self.execute_node(stmt)
    
    def execute_loop_statement(self, node: LoopStatementNode):
        """执行LOOP语句"""
        for _ in range(node.times):
            for stmt in node.body:
                self.execute_node(stmt)
                # 检查是否到达出口
                if self.bot.is_on_exit():
                    break
            if self.bot.is_on_exit():
                break
    
    def evaluate_condition(self, condition: ConditionNode) -> bool:
        """评估条件表达式"""
        if condition.operator == "NOT":
            return not self.evaluate_condition(condition.left)
        
        # 基本传感器条件
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
    """解释器主类"""
    
    def __init__(self, world: World, bot: Bot):
        self.world = world
        self.bot = bot
        self.tokenizer = Tokenizer()
        self.parser = Parser()
        self.executor = Executor(world, bot)
    
    def run(self, source: str) -> bool:
        """
        运行源代码
        
        Args:
            source: 源代码字符串
            
        Returns:
            bool: 执行是否成功
        """
        try:
            # 词法分析
            tokens = self.tokenizer.tokenize(source)
            
            # 语法分析
            ast = self.parser.parse(tokens)
            
            # 执行
            return self.executor.execute(ast)
            
        except Exception as e:
            print(f"解释器错误: {e}")
            return False
    
    def get_token_count(self, source: str) -> int:
        """获取源代码的token数量"""
        try:
            tokens = self.tokenizer.tokenize(source)
            # 过滤掉空白和EOF token
            meaningful_tokens = [t for t in tokens if t.type not in [TokenType.WHITESPACE, TokenType.EOF]]
            return len(meaningful_tokens)
        except:
            return 0 