# Vault Runner

A mini programming language project that includes a Python interpreter, enabling robots to navigate in a 2D grid world, collect keys, open doors, and reach the exit.

## Project Overview

Vault Runner implements a simple programming language that allows users to write programs to control robot behavior in a 2D grid world. The robot can only see one cell ahead and must use sensors and actions to complete tasks.

## Core Features

- **Mini Programming Language**: No more than 20 keywords, supports conditional statements and loops
- **2D Grid World**: Contains floors, walls, keys, doors, and exits
- **Sensor System**: Whether the front is clear, whether on a key, whether at a door, whether at exit
- **Action System**: Move, turn, pick up keys, open doors
- **Safety Limits**: Maximum nesting depth of 10 levels, loop limit of 50 iterations

## Project Structure

```
TheVaultRunner/
├── main.py              # Main program entry point
├── interpreter.py       # Interpreter (Tokenizer, Parser, Executor)
├── bot.py              # Robot implementation
├── world.py            # World model
├── examples/           # Example programs
│   ├── corridor.runner
│   └── collect_and_open.runner
├── tests/              # Test cases
│   └── test_world.py
└── README.md           # Project documentation
```

## Installation and Running

### Running Example Programs

```bash
# Run corridor example
python main.py examples/corridor.runner --verbose

# Run collect keys and open door example
python main.py examples/collect_and_open.runner --verbose
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ --verbose

# Run specific test file
python -m pytest tests/test_world.py --verbose
```

## Language Syntax

### Keywords (20 total)
- `MOVE`, `LEFT`, `RIGHT`, `PICK`, `OPEN` - 5 actions 
- `IF`, `ELSE`, `ENDIF` - 3 conditional statements
- `LOOP`, `ENDLOOP`, `TIMES` - 3 loop statements
- `FRONT_CLEAR`, `ON_KEY`, `AT_DOOR`, `AT_EXIT`, `HAVE_KEY` - 5 detection method
- `AND`, `OR`, `NOT` - 3 logical operators
- `END` - 1 ending action

### Syntax Example

```
LOOP 50:
  IF FRONT_CLEAR:
    MOVE
  ELSE:
    RIGHT
  ENDIF
ENDLOOP
```

## Constraints

- **Nesting Depth**: Maximum 3 levels (IF/LOOP nesting)
- **Loop Limit**: Maximum 50 iterations
- **Keyword Count**: No more than 20
- **Variable Limits**: Can only use sensor outputs, literals, and one accumulator flag

## Example Programs

### 1. Corridor Navigation (corridor.runner)
- **Token Count**: 15
- **Description**: Simple right-wall-following strategy, loop limit of 50 iterations

### 2. Collect Keys and Open Doors (collect_and_open.runner)
- **Token Count**: 25
- **Description**: Prioritize picking up keys, open doors when encountering them with keys, until reaching the exit

## Implemented Features

- ✅ Basic framework structure
- ✅ World model (2D grid)
- ✅ Robot implementation (movement, turning, sensors)
- ✅ Interpreter (Tokenizer, Parser, Executor)
- ✅ Example programs
- ✅ Automated test cases
- ✅ Constraint checking (nesting depth, loop limit)

## Planned Features

1. **Richer Conditional Expressions** - Support complex logical combinations
2. **Macro and Function Support** - Subroutine definition and calling
3. **Path Planning Algorithms** - A* and other intelligent navigation
4. **Visualization Output** - Step display and world state
5. **Multi-key Multi-door Support** - Extend world model complexity

## Extension Possibilities

### High Priority
- Support richer conditional expressions and variables
- Add macro or function/subroutine support

### Medium Priority
- Better path planning algorithms as built-in macros
- Visualized step output

### Low Priority
- Support for multiple keys or multiple doors
- Graphical interface support

## Technology Stack

- **Python 3.10+**
- **Type annotations**
- **pytest** (testing framework)

## Contributing Guidelines

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is for learning and research purposes only. 