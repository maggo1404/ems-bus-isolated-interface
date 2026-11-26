import sys
# generate a test board: args = board attrs string, trace attrs string (for the crossing nets)
battrs, tattrs, name = sys.argv[1], sys.argv[2], sys.argv[3]
extra = sys.argv[4] if len(sys.argv) > 4 else ''
res = []
# 3 horizontal pairs and 3 vertical pairs crossing in the middle -> must use vias on a 2-layer board
for i in range(3):
    y = -4 + i*4
    res.append(f'<resistor name="RH{i}a" resistance="1k" footprint="0603" pcbX={{-12}} pcbY={{{y}}} />')
    res.append(f'<resistor name="RH{i}b" resistance="1k" footprint="0603" pcbX={{12}} pcbY={{{y}}} />')
    x = -4 + i*4
    res.append(f'<resistor name="RV{i}a" resistance="1k" footprint="0603" pcbX={{{x}}} pcbY={{-12}} pcbRotation={{90}} />')
    res.append(f'<resistor name="RV{i}b" resistance="1k" footprint="0603" pcbX={{{x}}} pcbY={{12}} pcbRotation={{90}} />')
    res.append(f'<trace from=".RH{i}a > .pin2" to=".RH{i}b > .pin1" {tattrs} />')
    res.append(f'<trace from=".RV{i}a > .pin2" to=".RV{i}b > .pin1" {tattrs} />')
res.append(extra)
src = f'export default () => (\n<board width="34mm" height="34mm" layers={{2}} {battrs}>\n' + "\n".join(res) + '\n</board>\n)\n'
open(f"scratch/rt/{name}.circuit.tsx","w").write(src)
