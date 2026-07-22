import re

def resolve_remaining(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Matches any git conflict markers
    pattern = re.compile(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]+', re.DOTALL)
    
    resolved = pattern.sub(r'\1', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(resolved)
    
    print("Resolved remaining conflicts.")

if __name__ == '__main__':
    resolve_remaining(r'C:\Users\dasha\Projects\pangea-substrate\public\nova_horizon_3d.html')
