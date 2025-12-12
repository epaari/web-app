# Quick fix script to apply all equation rendering fixes
import re

file_path = r'c:\EzeeGenie\web-app\Tools\Migration\migration.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Add func handler after rad handler
func_handler = '''
        # Function (like lim, sin, cos, etc.)
        elif tag == 'func':
            # Get the function name
            fName = elem.find(f'{m_ns}fName')
            func_name = process_element(fName) if fName is not None else ''
            
            # Get the base expression (what comes after the function)
            e_elem = elem.find(f'{m_ns}e')
            base_latex = process_element(e_elem) if e_elem is not None else ''
            
            # Add backslash for LaTeX function names (lim, sin, cos, etc.)
            if func_name and not func_name.startswith('\\\\'):
                func_name = '\\\\' + func_name
            
            return f'{func_name}{base_latex}'
'''

# Find the rad handler and add func handler after it
content = re.sub(
    r"(return f'\\\\sqrt\{\{base_latex\}\}'\s+)",
    r"\1" + func_handler + "\n",
    content,
    count=1
)

# Fix 2: Update sSub handler to support multi-line subscripts
old_ssub = r'''        # Subscript
        elif tag == 'sSub':
            base = elem\.find\(f'\{m_ns\}e'\)
            sub = elem\.find\(f'\{m_ns\}sub'\)
            base_latex = process_element\(base\) if base is not None else ''
            sub_latex = process_element\(sub\) if sub is not None else ''
            return f'\{base_latex\}_\{\{\{sub_latex\}\}\}' '''

new_ssub = '''        # Subscript
        elif tag == 'sSub':
            base = elem.find(f'{m_ns}e')
            sub = elem.find(f'{m_ns}sub')
            base_latex = process_element(base) if base is not None else ''
            
            # Check if subscript contains an equation array (multi-line subscript)
            if sub is not None and sub.find(f'{m_ns}eqArr') is not None:
                # Multi-line subscript - use \\\\substack for vertical stacking
                eqArr = sub.find(f'{m_ns}eqArr')
                rows = []
                for e_elem in eqArr.findall(f'{m_ns}e'):
                    row_content = process_element(e_elem)
                    if row_content:
                        rows.append(row_content)
                
                if rows:
                    sub_latex = '\\\\substack{' + ' \\\\\\\\ '.join(rows) + '}'
                else:
                    sub_latex = process_element(sub) if sub is not None else ''
            else:
                sub_latex = process_element(sub) if sub is not None else ''
            
            return f'{base_latex}_{{{sub_latex}}}'
'''

content = re.sub(old_ssub, new_ssub, content, flags=re.DOTALL)

# Fix 3: Add integral detection heuristic in nary handler
# Find the nary handler and add the heuristic
old_nary_start = r"(# N-ary operators.*?operator = '\\\\sum'  # Default to summation)"
new_nary_start = r"\1\n            chr_val = '∑'  # Default character value"

content = re.sub(old_nary_start, new_nary_start, content, flags=re.DOTALL)

# Add heuristic after processing limits
old_nary_limits = r'''(# Get subscript \(lower limit\)
            sub_elem = elem\.find\(f'\{m_ns\}sub'\)
            sub_latex = process_element\(sub_elem\) if sub_elem is not None else ''
            
            # Get superscript \(upper limit\)
            sup_elem = elem\.find\(f'\{m_ns\}sup'\)
            sup_latex = process_element\(sup_elem\) if sup_elem is not None else '')'''

new_nary_limits = '''# Get subscript (lower limit) and superscript (upper limit)
            sub_elem = elem.find(f'{m_ns}sub')
            sup_elem = elem.find(f'{m_ns}sup')
            
            # Process limits once and cache the results
            sub_latex = process_element(sub_elem) if sub_elem is not None else ''
            sup_latex = process_element(sup_elem) if sup_elem is not None else ''
            
            # Check if we need to apply the integral heuristic
            if chr_val == '∑' and sub_elem is not None and sup_elem is not None:
                # Heuristic: Integrals typically have simple limits (a, b, 0, 1, etc.)
                # Summations typically have expressions like i=1, n, etc.
                has_empty_limits = (not sub_latex or not sup_latex)
                is_simple_lower = len(sub_latex) == 1 and sub_latex.isalnum()
                is_simple_upper = len(sup_latex) == 1 and sup_latex.isalnum()
                
                if has_empty_limits or (is_simple_lower and is_simple_upper):
                    operator = '\\\\int'
'''

content = re.sub(old_nary_limits, new_nary_limits, content, flags=re.DOTALL)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied all fixes successfully!")
