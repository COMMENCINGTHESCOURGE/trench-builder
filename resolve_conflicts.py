import re

def resolve_merge_conflicts(filepath, output_path):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple regex to find merge conflicts and keep HEAD side (which has the local changes and Rim Light)
    # or keep a blend. Let's inspect the matches and resolve them.
    pattern = re.compile(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [a-f0-9]+', re.DOTALL)
    
    def replacement(match):
        head = match.group(1)
        incoming = match.group(2)
        
        # Smart merge: if HEAD contains hyperrealism or custom code, prefer HEAD.
        # If incoming contains new features like saveGame, let's include it.
        if "Rim Light" in head or "rimLight" in head:
            return head
        if "logo-icon" in head:
            return head
        if "inventory-content" in head:
            # combine both
            return head + "\n" + incoming
        if "pause-menu" in incoming:
            return head + "\n" + incoming
        
        # Default: Keep HEAD
        return head

    resolved = pattern.sub(replacement, content)
    
    # Verify no remaining conflict markers
    if "<<<<<<<" in resolved:
        print("Warning: Some conflicts could not be resolved automatically.")
    else:
        print("All conflicts resolved successfully.")
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(resolved)

if __name__ == '__main__':
    resolve_merge_conflicts(
        r'C:\Users\dasha\Projects\trench_builder\NOVA_HORIZON_3D.html',
        r'C:\Users\dasha\Projects\pangea-substrate\public\nova_horizon_3d.html'
    )
