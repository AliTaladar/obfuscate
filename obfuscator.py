import ast
from transformers import NameCollector, StringEncoder, JunkCodeInserter, ControlFlowAlterer
from llm_integration import llm_generate_names, llm_generate_junk_function

class Obfuscator:
    """Main obfuscator class that applies multiple transformations."""
    def __init__(self, transformations):
        self.transformations = transformations

    def obfuscate(self, code):
        """Obfuscate the input code using LLM-generated names and functions."""
        tree = ast.parse(code)
        collector = NameCollector()
        collector.visit(tree)
        names_to_obfuscate = list(collector.names)
        num_names_needed = len(names_to_obfuscate) + 10  # Extra names for junk functions
        llm_names = llm_generate_names(num_names_needed)
        
        # Map original names to LLM-generated names
        name_mapping = {}
        for i, original in enumerate(names_to_obfuscate):
            name_mapping[original] = llm_names[i]
        available_names = llm_names[len(names_to_obfuscate):]  # Remaining names for other uses

        # Apply transformations
        for transform in self.transformations:
            transformer = transform(name_mapping, available_names)
            tree = transformer.visit(tree)

        # Insert decode function if string encoding is used
        if any(isinstance(t, type(StringEncoder)) for t in self.transformations):
            decode_func_code = """
def decode(s):
    return ''.join(chr(ord(c) - 1) for c in s)
"""
            decode_func_ast = ast.parse(decode_func_code, mode='exec').body[0]
            tree.body.insert(0, decode_func_ast)

        ast.fix_missing_locations(tree)
        return ast.unparse(tree)