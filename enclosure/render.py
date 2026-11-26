"""Vorschau-Bilder (matplotlib, ohne GPU)."""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))


def _poly(ax, tm, color, alpha=1.0, clip=None, shift=(0, 0, 0)):
    v = tm.vertices + np.array(shift)
    f = tm.faces
    cen = v[f].mean(axis=1)
    if clip is not None:
        f = f[clip(cen)]
    tri = v[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
    light = np.array([0.4, -0.5, 0.75]); light /= np.linalg.norm(light)
    sh = 0.45 + 0.55 * np.clip(n @ light, 0, 1)
    base = np.array(matplotlib.colors.to_rgb(color))
    cols = np.c_[base[None, :] * sh[:, None], np.full(len(f), alpha)]
    pc = Poly3DCollection(tri, facecolors=cols, edgecolors='none', linewidths=0)
    ax.add_collection3d(pc)


def _scene(items, elev, azim, fn, title, size=(13, 8), zmax=30):
    fig = plt.figure(figsize=size, dpi=110)
    ax = fig.add_subplot(111, projection='3d')
    for it in items:
        _poly(ax, **it)
    ax.set_box_aspect((126, 65, zmax))
    ax.set_xlim(-70, 57); ax.set_ylim(-35, 35); ax.set_zlim(0, zmax)
    ax.view_init(elev, azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=11)
    fig.savefig(os.path.join(HERE, 'img', fn), bbox_inches='tight')
    plt.close(fig)


def render_all(d, to_tm, g):
    os.makedirs(os.path.join(HERE, 'img'), exist_ok=True)
    tb, tl, tp, tpl = to_tm(d['bottom']), to_tm(d['lid']), to_tm(d['pcb']), to_tm(d['plug'])
    rods = [to_tm(r) for r in d['rods']]
    sc = [to_tm(s) for s in d['scr']]
    items = [dict(tm=tb, color='#8a9bb0'), dict(tm=tp, color='#2e7d32', shift=(0, 0, 14)), dict(tm=tpl, color='#d9a400', shift=(0, 0, 14)),
             dict(tm=tl, color='#b0bcc8', shift=(0, 0, 40))] + \
            [dict(tm=r, color='#e53935', shift=(0, 0, 40)) for r in rods] + \
            [dict(tm=s, color='#444444', shift=(0, 0, 40)) for s in sc]
    _scene(items, 28, -62, 'assembly_exploded.png', 'Explosion: Unterteil, Platine (gruen, Bauteile als Boxen), P1-Stecker (gelb), Deckel, Lichtleiter, Schrauben', zmax=66)
    items = [dict(tm=tb, color='#8a9bb0'), dict(tm=tp, color='#2e7d32'), dict(tm=tpl, color='#d9a400'),
             dict(tm=tl, color='#b0bcc8', alpha=0.35)] + [dict(tm=r, color='#e53935') for r in rods] + [dict(tm=s, color='#444444') for s in sc]
    _scene(items, 38, -58, 'assembly_fit.png', 'Zusammengebaut (Deckel halbtransparent) - Platine mit Bauteilen passt kollisionsfrei')
    cut = d['cut']
    c = lambda mf: to_tm(mf ^ cut)
    items = [dict(tm=c(d['bottom']), color='#8a9bb0'), dict(tm=c(d['pcb']), color='#2e7d32'), dict(tm=c(d['plug']), color='#d9a400'),
             dict(tm=c(d['lid']), color='#b0bcc8')] + [dict(tm=to_tm(x ^ cut), color='#444444') for x in d['scr']] + \
            [dict(tm=to_tm(x ^ cut), color='#e53935') for x in d['rodsm']]
    _scene(items, 22, -68, 'assembly_cutaway.png', 'Schnitt bei y = +6 mm: Posten, Schrauben, Rippe x=0, Deckelhuelsen, Lichtleiter', size=(15, 7), zmax=34)
    def plan(fn, title, layers, extra=None):
        fig, ax = plt.subplots(figsize=(15, 8.3), dpi=110)
        for tm, z, col, lw in layers:
            sec = tm.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
            if sec is None:
                continue
            for pts in sec.discrete:
                ax.plot(pts[:, 0], pts[:, 1], color=col, lw=lw)
        if extra:
            extra(ax)
        ax.set_aspect('equal'); ax.set_title(title, fontsize=11); ax.grid(alpha=.25)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, 'img', fn)); plt.close(fig)
    ZT, ZB, ZLT = g['Z_PCB_T'], g['Z_PCB_B'], g['Z_LID_T']
    def lab(ax):
        for n, (x, y) in g['LEDS'].items():
            ax.annotate(n, (x, y), color='#e53935', fontsize=8, ha='center', va='bottom', xytext=(0, 9), textcoords='offset points')
        for n, v in g['BTN'].items():
            ax.annotate(n, (v[0], v[1]), color='#e53935', fontsize=8, ha='center', va='top', xytext=(0, -8), textcoords='offset points')
    plan('plan_lid.png', 'Deckel von oben (Schnitt knapp unter der Oberflaeche: Loecher, Gravuren, Fenster); grau = Bauteile der Platine',
         [(tl, ZLT - 0.2, '#263238', 1.0), (tp, ZT + 0.6, '#9e9e9e', 0.6)], lab)
    plan('plan_bottom.png', 'Unterteil von oben (Schnitt unter der Platine: Posten, Rippe x=0 mit Zungen, Wandmontage); gruen = Platinenumriss',
         [(tb, ZB - 1.0, '#263238', 1.2), (tp, ZB + 0.8, '#2e7d32', 1.0)])
    fig, axs = plt.subplots(2, 1, figsize=(14, 9), dpi=110)
    for ax, (axis, val, ttl) in zip(axs, ((1, 0.0, 'Schnitt y = 0 (XZ): P1-Stecker links, Rippe x=0, Antennenende rechts'),
                                          (0, 33.0, 'Schnitt x = 33 (YZ): USB-C-Buchse J2 oben (+y), Ausschnitt 12 x 7'))):
        for tm, col in ((tb, '#37474f'), (tl, '#607d8b'), (tp, '#2e7d32'), (tpl, '#d9a400')):
            n = np.zeros(3); n[axis] = 1; o = np.zeros(3); o[axis] = val
            sec = tm.section(plane_origin=o, plane_normal=n)
            if sec is None:
                continue
            for ent in sec.entities:
                pts = sec.vertices[ent.points]
                ax.plot(pts[:, 0 if axis == 1 else 1], pts[:, 2], color=col, lw=1.4)
        ax.set_aspect('equal'); ax.set_title(ttl, fontsize=10); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, 'img', 'sections.png')); plt.close(fig)
