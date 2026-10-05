import re

def fix_table_overlaps(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # The table block in Appendix A has \texttt{path\_with\_underscores.py}
    # We want to change them to \path{path_with_underscores.py}
    
    # Let's target the tabularx environment for tab:claim_map
    pattern = r'(\\begin\{tabularx\}\{\\textwidth\}\{.*?\\end\{tabularx\}\})'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        table_content = match.group(1)
        # Inside this table content, replace \texttt{...} with \path{...}
        # and unescape the underscores
        
        def replace_texttt(m):
            inner = m.group(1)
            # unescape underscores
            inner = inner.replace(r'\_', '_')
            return r'\path{' + inner + '}'
            
        fixed_table = re.sub(r'\\texttt\{([^}]+)\}', replace_texttt, table_content)
        
        content = content.replace(table_content, fixed_table)

    with open(filepath, 'w') as f:
        f.write(content)

fix_table_overlaps('paper/Machine_Markets_Final_Integrated_Paper.tex')
