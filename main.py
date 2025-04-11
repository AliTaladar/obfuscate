# main.py
import argparse
from obfuscator import Obfuscator
from transformers import StringEncoder, JunkCodeInserter, ControlFlowAlterer, CodeEncryptor

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Obfuscate Python code')
    parser.add_argument('input', help='Input file path (e.g., keylogger.py)')
    parser.add_argument('output', help='Output file path (e.g., obfuscated.py)')
    parser.add_argument('--junk', action='store_true', help='Insert junk code')
    parser.add_argument('--control-flow', action='store_true', help='Alter control flow')
    parser.add_argument('--encrypt', action='store_true', help='Encrypt function bodies')
    args = parser.parse_args()

    # Read the input code
    with open(args.input, 'r') as f:
        code = f.read()

    # Define transformations based on CLI arguments
    transformations = [StringEncoder]  # Always include string encoding
    if args.junk:
        transformations.append(JunkCodeInserter)
    if args.control_flow:
        transformations.append(ControlFlowAlterer)
    if args.encrypt:
        transformations.append(CodeEncryptor)

    # Obfuscate the code
    obfuscator = Obfuscator(transformations)
    obfuscated_code = obfuscator.obfuscate(code)

    # Write the obfuscated code to the output file
    with open(args.output, 'w') as f:
        f.write(obfuscated_code)