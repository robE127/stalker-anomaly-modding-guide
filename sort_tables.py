import re

with open('docs/api-reference/index.md', 'r', encoding='utf-8') as f:
    content = f.read()

def sort_key(row):
    cells = row.split('|')
    if len(cells) < 2:
        return ''
    cell = cells[1].strip().strip('`')
    # Remove namespace prefix: db.actor:, level., game., alife():, xr_logic., etc.
    cell = re.sub(r'^[a-zA-Z_.()]+[:.]+', '', cell)
    # Remove parameters
    cell = re.sub(r'\(.*', '', cell)
    return cell.lower().strip('`').strip()

def sort_table(table_text):
    lines = table_text.rstrip('\n').split('\n')
    header = lines[0]
    sep = lines[1]
    rows = [l for l in lines[2:] if l.strip()]
    sorted_rows = sorted(rows, key=sort_key)
    return '\n'.join([header, sep] + sorted_rows)

table_re = re.compile(r'(\| .+\|\n\|[-| :]+\|\n(?:\| .+\|\n?)+)')

def replace(m):
    t = m.group(0)
    first_line = t.split('\n')[0]
    # Skip tables with a Freq column — those stay sorted by freq desc
    if '| Freq |' in first_line or '| Freq' in first_line:
        return t
    return sort_table(t) + '\n'

new_content = table_re.sub(replace, content)

with open('docs/api-reference/index.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Done')
