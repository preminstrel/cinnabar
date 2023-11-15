import re

def cuda_out_of_memory(filename):
    with open(filename, 'r') as file:
        content = file.read()
        match = re.search(r'RuntimeError: CUDA out of memory.', content)
        if match:
            return True
        else:
            return False