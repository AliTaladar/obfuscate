# transformers.py
import ast
from utils import generate_obscure_name, encode
from llm_integration import llm_generate_junk_function
from encryption import generate_key, encrypt_code

class NameCollector(ast.NodeVisitor):
    """Collects all user-defined names in the code for renaming."""
    def __init__(self):
        self.names = set()

    def collect_names_from(self, node):
        """Recursively collect names from assignment targets (handles tuples, lists, etc.)."""
        if isinstance(node, ast.Name):
            self.names.add(node.id)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for elt in node.elts:
                self.collect_names_from(elt)

    def visit_FunctionDef(self, node):
        """Collect function name and its parameters."""
        self.names.add(node.name)
        for arg in node.args.args:
            self.names.add(arg.arg)
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Collect names from assignment targets."""
        for target in node.targets:
            self.collect_names_from(target)
        self.generic_visit(node)

    def visit_For(self, node):
        """Collect names from for-loop targets."""
        self.collect_names_from(node.target)
        self.generic_visit(node)

    def visit_With(self, node):
        """Collect names from with-statement variables."""
        for item in node.items:
            if item.optional_vars:
                self.collect_names_from(item.optional_vars)
        self.generic_visit(node)

class BaseObfuscator(ast.NodeTransformer):
    """Base class for obfuscation transformers."""
    def __init__(self, name_mapping):
        self.name_mapping = name_mapping

    def visit_Name(self, node):
        """Replace user-defined names with obscure ones from the mapping."""
        if node.id in self.name_mapping:
            node.id = self.name_mapping[node.id]
        return node

    def visit_FunctionDef(self, node):
        """Rename the function name and its parameters."""
        if node.name in self.name_mapping:
            node.name = self.name_mapping[node.name]
        for arg in node.args.args:
            if arg.arg in self.name_mapping:
                arg.arg = self.name_mapping[arg.arg]
        return self.generic_visit(node)

class StringEncoder(BaseObfuscator):
    """Transforms string literals into decode function calls."""
    def visit_Str(self, node):
        """Replace string literals with a decode function call using the encoded value."""
        encoded = encode(node.s)
        return ast.Call(
            func=ast.Name(id='decode', ctx=ast.Load()),
            args=[ast.Str(s=encoded)],
            keywords=[]
        )

class JunkCodeInserter(BaseObfuscator):
    """Inserts junk code (e.g., dummy functions) into the AST."""
    def visit_Module(self, node):
        """Insert a dummy function at the beginning of the module."""
        junk_func_code = llm_generate_junk_function()
        junk_func_ast = ast.parse(junk_func_code).body[0]
        node.body.insert(0, junk_func_ast)
        return self.generic_visit(node)

class ControlFlowAlterer(BaseObfuscator):
    """Alters control flow by replacing if statements with nested function calls."""
    def visit_If(self, node):
        """Replace if statement with a nested function call structure."""
        # Create a function that wraps the if body
        if_func_name = generate_obscure_name()
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
        # Create a function that wraps the else body
        else_func_name = generate_obscure_name()
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
        # Create a call to select between the two functions
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
        # Return a list of the new functions and the select call
        return [if_func, else_func, select_call]

class CodeEncryptor(BaseObfuscator):
    """Encrypts function bodies and replaces them with decryption calls."""
    def __init__(self, name_mapping):
        super().__init__(name_mapping)
        self.key = generate_key()
        self.decrypt_func_name = generate_obscure_name()

    def visit_FunctionDef(self, node):
        """Encrypt the function body and replace it with a decryption call."""
        # Create a Module node with the function body and fix missing locations
        subtree = ast.Module(body=node.body, type_ignores=[])
        ast.fix_missing_locations(subtree)
        # Unparse the subtree to get the code string
        func_code = ast.unparse(subtree)
        # Encrypt the code
        encrypted_code = encrypt_code(func_code, self.key)
        
        # Create a new function body that decrypts and executes the code
        decrypt_call = ast.parse(f"""
exec({self.decrypt_func_name}('{encrypted_code}', {self.key!r}))
""").body[0]
        
        # Replace the original function body with the decryption call
        node.body = [decrypt_call]
        return self.generic_visit(node)

    def get_decrypt_func(self):
        """Return the decryption function to be inserted into the code."""
        decrypt_func_code = f"""
def {self.decrypt_func_name}(encrypted_code, key):
    from cryptography.fernet import Fernet
    import base64
    fernet = Fernet(key)
    decrypted = fernet.decrypt(base64.b64decode(encrypted_code.encode()))
    return decrypted.decode()
"""
        return ast.parse(decrypt_func_code).body[0]