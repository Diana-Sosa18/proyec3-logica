"""Exporta el arbol SLD de camino(X,d,Y) a DOT y PNG.

Alternativa reproducible a SldDraw; no produce una exportacion de SldDraw.
Requiere Python 3 y Pillow: python -m pip install Pillow.
Ejecutar: python ejercicio2/generar_arbol.py
El expansor se limita al grafo aciclico y las dos reglas de este ejercicio.
"""
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
source = (HERE / 'grafo.pl').read_text(encoding='utf-8')
code = re.sub(r'%[^\n]*', '', source)
clauses = [re.sub(r'\s+', '', c) for c in code.split('.') if c.strip()]
expected = ['camino(X,Y,[X,Y]):-arco(X,Y)',
            'camino(X,Y,[X|Resto]):-arco(X,Z),camino(Z,Y,Resto)']
assert [c for c in clauses if c.startswith('camino(')] == expected, \
    'Las reglas cambiaron: adapte el expansor antes de exportar.'
arcs = re.findall(r'arco\(([a-z]\w*),([a-z]\w*)\)',
                  '.'.join(c for c in clauses if ':-' not in c))
assert arcs == [('a', 'b'), ('a', 'c'), ('a', 'd'), ('c', 'd')], \
    'Este expansor corresponde exclusivamente al grafo de la tarea.'

nodes, edges, answers = [], [], []

def node(label, kind='goal'):
    i = len(nodes)
    nodes.append({'label': label, 'kind': kind, 'children': []})
    return i


def child(parent, label, edge='', kind='goal'):
    i = node(label, kind)
    nodes[parent]['children'].append(i)
    edges.append((parent, i, edge))
    return i


def finish(parent, x, path, binding):
    answer = f"X={x}, Y=[{','.join(path)}]"
    child(parent, 'EXITO: objetivo vacio\n' + answer, binding, 'success')
    answers.append((x, path))


def expand_call(parent, vertex, tail, prefix, x, depth):
    # En cada llamada se prueban primero la regla base y luego la recursiva.
    z, rest = f'Z{depth}', f'R{depth}'
    base = child(parent, f'arco({vertex},d)',
                 f'base: {tail}=[{vertex},d]')
    matches = [(a, b) for a, b in arcs if a == vertex and b == 'd']
    if matches:
        finish(base, x, prefix + [vertex, 'd'], 'hecho arco(' + vertex + ',d)')
    else:
        child(base, 'FALLO', 'sin hecho compatible', 'failure')
    rec = child(parent, f'arco({vertex},{z}),\ncamino({z},d,{rest})',
                f'rec.: {tail}=[{vertex}|{rest}]')
    outgoing = [(a, b) for a, b in arcs if a == vertex]
    if not outgoing:
        child(rec, 'FALLO', 'sin hecho compatible', 'failure')
    for _, dest in outgoing:
        call = child(rec, f'camino({dest},d,{rest})', f'{z}={dest}')
        expand_call(call, dest, rest, prefix + [vertex], x, depth + 1)


root = node('camino(X,d,Y)')
base = child(root, 'arco(X,d)', 'base: Y=[X,d]')
for a, b in arcs:
    if b == 'd':
        finish(base, a, [a, b], f'X={a}')
rec = child(root, 'arco(X,Z1),\ncamino(Z1,d,R1)', 'rec.: Y=[X|R1]')
for a, b in arcs:
    call = child(rec, f'camino({b},d,R1)', f'X={a}, Z1={b}')
    expand_call(call, b, 'R1', [a], a, 2)
assert answers == [('a', ['a', 'd']), ('c', ['c', 'd']),
                   ('a', ['a', 'c', 'd'])]
assert sum(n['kind'] == 'failure' for n in nodes) == 8

# Fuente editable para Graphviz; conserva todos los objetivos y sustituciones.
def quote(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'

colors = {'goal': '#edf3ff', 'success': '#daf5e7', 'failure': '#ffe4e6'}
dot = ['digraph busqueda {', '  graph [rankdir=TB, ordering=out];',
       '  node [shape=box, style="rounded,filled", fontname="DejaVu Sans"];',
       '  edge [fontname="DejaVu Sans", fontsize=10];']
for i, n in enumerate(nodes):
    dot.append(f'  n{i} [label={quote(n["label"])}, fillcolor="{colors[n["kind"]]}"];')
for a, b, label in edges:
    dot.append(f'  n{a} -> n{b} [label={quote(label)}];')
dot.append('}')
(HERE / 'arbol_busqueda.dot').write_text('\n'.join(dot) + '\n', encoding='utf-8')

# Distribucion por hojas para que ninguna rama se oculte ni se superponga.
leaf = 0
positions = {}
def layout(i, depth=0):
    global leaf
    children = nodes[i]['children']
    xs = [layout(c, depth + 1) for c in children]
    x = (xs[0] + xs[-1]) / 2 if xs else leaf
    if not xs:
        leaf += 1
    positions[i] = (x, depth)
    return x

layout(root)
step_x, step_y, box_w, box_h = 430, 245, 395, 108
margin, top = 85, 240
width = margin * 2 + (leaf - 1) * step_x + box_w
height = top + max(d for _, d in positions.values()) * step_y + 230
im = Image.new('RGB', (width, height), '#ffffff')
draw = ImageDraw.Draw(im)
font_dir = Path('/usr/share/fonts/truetype/dejavu')
def font(size, bold=False):
    name = 'DejaVuSans' + ('-Bold' if bold else '') + '.ttf'
    try:
        return ImageFont.truetype(str(font_dir / name), size)
    except OSError:
        return ImageFont.load_default()

normal, small, title = font(20), font(17), font(36, True)
def xy(i):
    x, d = positions[i]
    return margin + box_w / 2 + x * step_x, top + d * step_y

draw.text((margin, 35), 'Arbol SLD completo: camino(X,d,Y)', fill='#12243a', font=title)
draw.text((margin, 92), 'Seleccion del objetivo izquierdo; clausulas y hechos en el orden de grafo.pl.', fill='#364152', font=normal)
draw.text((margin, 130), 'Verde = exito | Rojo = fallo | Z1, R1, Z2, R2... = variables frescas por llamada.', fill='#364152', font=normal)
draw.text((margin, 168), 'Generado con Python/Pillow. No es una exportacion de SldDraw.', fill='#364152', font=normal)
for a, b, label in edges:
    x1, y1 = xy(a)
    x2, y2 = xy(b)
    start, end = (x1, y1 + box_h / 2), (x2, y2 - box_h / 2)
    draw.line([start, end], fill='#6a7c91', width=3)
    draw.polygon([(x2, end[1]), (x2 - 6, end[1] - 12), (x2 + 6, end[1] - 12)], fill='#6a7c91')
    # Etiqueta cerca del hijo: cada hoja dispone de su propia columna.
    tx, ty = x2, end[1] - 36
    bbox = draw.textbbox((0, 0), label, font=small)
    tw = bbox[2] - bbox[0]
    draw.rectangle((tx-tw/2-5, ty-2, tx+tw/2+5, ty+24), fill='white')
    draw.text((tx-tw/2, ty), label, fill='#27364a', font=small)
for i, n in enumerate(nodes):
    x, y = xy(i)
    draw.rounded_rectangle((x-box_w/2, y-box_h/2, x+box_w/2, y+box_h/2),
                           radius=16, fill=colors[n['kind']], outline='#667890', width=2)
    bbox = draw.multiline_textbbox((0, 0), n['label'], font=normal, spacing=8, align='center')
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.multiline_text((x-tw/2, y-th/2-4), n['label'], font=normal,
                       fill='#102337', spacing=8, align='center')
im.save(HERE / 'arbol_busqueda.png')
print(f'{len(nodes)} nodos; 3 exitos; 8 fallos. Exportados DOT y PNG.')
for x, path in answers:
    print(f"X={x}, Y=[{','.join(path)}]")
