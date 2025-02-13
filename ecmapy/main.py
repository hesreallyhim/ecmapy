import ast
from astor import to_source # type: ignore

class OptionalChainingTransformer(ast.NodeTransformer):
    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        # First recursively transform any nested nodes
        self.generic_visit(node)
        
        # Check if this is an optional `chaining access (ends with ?)
        attr_name = node.attr
        if attr_name.endswith('?'):
            # Remove the ? from the attribute name
            clean_attr_name = attr_name[:-1]
            
            # Transform node.attr? into get_safe(node, 'attr')
            return ast.Call(
                func=ast.Name(id='get_safe', ctx=ast.Load()),
                args=[
                    node.value,
                    ast.Constant(value=clean_attr_name)
                ],
                keywords=[]
            )
        
        return node

def transform_source(source: str) -> str:
    """Transform source code containing optional chaining into valid Python."""
    # Parse the source into an AST
    tree = ast.parse(source)
    
    # Add import and helper function
    helper_code = """
    def get_safe(obj, attr):
        if obj is None:
            return None
        try:
            if isinstance(obj, dict):
                return obj.get(attr)
            return getattr(obj, attr)
        except (AttributeError, KeyError):
            return None
    """
    helper_tree = ast.parse(helper_code)
    
    # Add helper function at the start of the module
    tree.body = helper_tree.body + tree.body
    
    # Transform the AST
    transformer = OptionalChainingTransformer()
    transformed_tree = transformer.visit(tree)
    
    # Fix line numbers and parent pointers
    ast.fix_missing_locations(transformed_tree)
    
    # Convert back to source code
    return to_source(transformed_tree)

def process_file(input_path: str, output_path: str):
    """Process an .ecpy file and output valid Python."""
    with open(input_path, 'r') as f:
        source = f.read()
    
    transformed = transform_source(source)
    
    with open(output_path, 'w') as f:
        f.write(transformed)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python transformer.py input.ecpy output.py")
        sys.exit(1)
    
    process_file(sys.argv[1], sys.argv[2])

# Example usage:
"""
# Input (sample.ecpy):
my_dict = {"a": {"b": 2}}
x = my_dict.a?.c
print(x)

# Output (sample.py):
def get_safe(obj, attr):
    if obj is None:
        return None
    try:
        if isinstance(obj, dict):
            return obj.get(attr)
        return getattr(obj, attr)
    except (AttributeError, KeyError):
        return None

my_dict = {"a": {"b": 2}}
x = get_safe(my_dict.get('a'), 'c')
print(x)
"""
