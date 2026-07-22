import re

def clean_conflict_markers(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output_lines = []
    in_conflict = False
    in_head = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("<<<<<<<"):
            in_conflict = True
            in_head = True
            i += 1
            continue
        elif line.startswith("======="):
            in_head = False
            i += 1
            continue
        elif line.startswith(">>>>>>>"):
            in_conflict = False
            i += 1
            continue
            
        if in_conflict:
            # If inside conflict, keep only the HEAD side (which is what we wanted)
            if in_head:
                output_lines.append(line)
        else:
            output_lines.append(line)
        i += 1
            
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print("Conflict markers cleaned successfully.")

if __name__ == '__main__':
    clean_conflict_markers(r'C:\Users\dasha\Projects\pangea-substrate\public\nova_horizon_aurora.html')
