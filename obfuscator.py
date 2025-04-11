# obfuscator.py
import ast
from transformers import NameCollector, StringEncoder, JunkCodeInserter, ControlFlowAlterer, CodeEncryptor
from llm_integration import llm_generate_names

class Obfuscator:
    """Main obfuscator class that applies multiple transformations."""
    def __init__(self, transformations):
        self.transformations = transformations

    def obfuscate(self, code):
        """Obfuscate the input code using the specified transformations."""
        tree = ast.parse(code)
        collector = NameCollector()
        collector.visit(tree)
        llm_names = llm_generate_names(len(collector.names))
        name_mapping = {name: llm_names[i] for i, name in enumerate(collector.names)}

        for transform in self.transformations:
            transformer = transform(name_mapping)
            tree = transformer.visit(tree)
            if isinstance(transformer, CodeEncryptor):
                # Insert the decrypt function
                decrypt_func = transformer.get_decrypt_func()
                tree.body.insert(0, decrypt_func)

        # Insert the decode function if string encoding is used
        if any(isinstance(t, type(StringEncoder)) for t in self.transformations):
            decode_func_code = """
def decode(s):
    return ''.join(chr(ord(c) - 1) for c in s)
"""
            decode_func_ast = ast.parse(decode_func_code, mode='exec').body[0]
            tree.body.insert(0, decode_func_ast)

        ast.fix_missing_locations(tree)
        return ast.unparse(tree)