


argparse是python标准库，基于optparse，语法分析程序

# 1.一个比较完整的例子

写一个最简单的例子，prog.py

```python
import argparse
parser = argparse.ArgumentParser(description="prog help...",   # 描述
                                 prog="prog",                  # 这个命令的名称
                                 usage="hhhh...a..."           # 用法
                                 )
# 增加必选参数
# parser.add_argument("echo",                                    # 必选参数名称
#                     help="echo the string you use here."       # 帮助信息
#                     )
# 增加可选参数
parser.add_argument("-s",                                      # 可选参数
                    "--square",                                # 可选参数，完整
                    help="echo the square of your given number.",
                    type=int                                   # 参数的类型
                    )
parser.add_argument("-v","--verb", help="increase output verbosity.",
                    action="store_true"                        # 后面不再跟参数值
                    )

arg = parser.parse_args()

# 开始处理输入的参数：
if arg.square:
    print(arg.square**2)

if arg.verb:
    print("verb turned on.")


```

可以发现很方便的类似bash命令的帮助信息。
```python
localhost:scripts$ python prog.py -h
usage: hhhh...a...

prog help...

optional arguments:
  -h, --help            show this help message and exit
  -s SQUARE, --square SQUARE
                        echo the square of your given number.
  -v, --verb            increase output verbosity.
```

# 2.ArgumentParser

```python
class argparse.ArgumentParser(prog=None, usage=None, description=None, epilog=None, parents=[], formatter_class=argparse.HelpFormatter, prefix_chars='-', fromfile_prefix_chars=None, argument_default=None, conflict_handler='error', add_help=True, allow_abbrev=True)

# 其中：
prog - The name of the program (default: sys.argv[0])
usage - The string describing the program usage (default: generated from arguments added to parser)
description - Text to display before the argument help (default: none)
epilog - Text to display after the argument help (default: none)
parents - A list of ArgumentParser objects whose arguments should also be included
formatter_class - A class for customizing the help output
prefix_chars - The set of characters that prefix optional arguments (default: ‘-‘)
fromfile_prefix_chars - The set of characters that prefix files from which additional arguments should be read (default: None)
argument_default - The global default value for arguments (default: None)
conflict_handler - The strategy for resolving conflicting optionals (usually unnecessary)
add_help - Add a -h/--help option to the parser (default: True)
allow_abbrev - Allows long options to be abbreviated if the abbreviation is unambiguous. (default: True)


```












# 参考

- https://docs.python.org/3/howto/argparse.html
- https://docs.python.org/3/library/argparse.html
