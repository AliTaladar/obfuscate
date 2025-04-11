import ast
from llm_integration import llm_generate_junk_function

class BaseObfuscator(ast.NodeTransformer):
    """Base class for obfuscation transformers."""
    def __init__(self, name_mapping, available_names):
        self.name_mapping = name_mapping
        self.available_names = available_names

class NameCollector(ast.NodeVisitor):
    """Collect all variable and function names in the code."""
    def __init__(self):
        self.names = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Load)):
            self.names.add(node.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.names.add(node.name)
        self.generic_visit(node)

class StringEncoder(BaseObfuscator):
    """Encode string literals and replace them with decode calls."""
    def visit_Str(self, node):
        encoded = ''.join(chr(ord(c) + 1) for c in node.s)
        return ast.Call(
            func=ast.Name(id='decode', ctx=ast.Load()),
            args=[ast.Str(s=encoded)],
            keywords=[]
        )

class JunkCodeInserter(BaseObfuscator):
    """Insert LLM-generated junk functions into the module."""
    def visit_Module(self, node):
        junk_func = self.create_junk_function()
        node.body.insert(0, junk_func)
        return self.generic_visit(node)

    def create_junk_function(self):
        """Create a junk function with an LLM-generated name and body."""
        junk_code = llm_generate_junk_function()
        junk_ast = ast.parse(junk_code)
        junk_func = junk_ast.body[0]
        if self.available_names:  # Rename the function with an available LLM name
            junk_func.name = self.available_names.pop(0)
        return junk_func

class ControlFlowAlterer(BaseObfuscator):
    """Replace if statements with nested function calls using LLM names."""
    def visit_If(self, node):
        # Create function for if body
        if_func_name = self.available_names.pop(0) if self.available_names else "if_func_" + str(id(node))
        if_func = ast.FunctionDef(
            name=if_func_name,
            args=ast.arguments(
                posonlyargs=[],
                args=[],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[]
            ),
            body=node.body,
            decorator_list=[],
            returns=None
        )
        # Create function for else body
        else_func_name = self.available_names.pop(0) if self.available_names else "else_func_" + str(id(node))
        else_func = ast.FunctionDef(
            name=else_func_name,
            args=ast.arguments(
                posonlyargs=[],
                args=[],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[]
            ),
            body=node.orelse if node.orelse else [ast.Pass()],
            decorator_list=[],
            returns=None
        )
        # Create a lambda to select between the two functions
        select_call = ast.Expr(
            value=ast.Call(
                func=ast.Lambda(
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[ast.arg(arg='x'), ast.arg(arg='y')],
                        vararg=None,
                        kwonlyargs=[],
                        kw_defaults=[],
                        kwarg=None,
                        defaults=[]
                    ),
                    body=ast.IfExp(
                        test=node.test,
                        body=ast.Call(func=ast.Name(id='x', ctx=ast.Load()), args=[], keywords=[]),
                        orelse=ast.Call(func=ast.Name(id='y', ctx=ast.Load()), args=[], keywords=[])
                    )
                ),
                args=[ast.Name(id=if_func_name, ctx=ast.Load()), ast.Name(id=else_func_name, ctx=ast.Load())],
                keywords=[]
            )
        )
        return [if_func, else_func, select_call]