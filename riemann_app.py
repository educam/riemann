"""
Hipótese de Riemann — aplicativo didático
=========================================

Um "livro ilustrado" interativo em 6 lições. Use os botões
◀ Anterior / Próxima ▶ (ou as setas do teclado) para navegar.

Requisitos:  pip install matplotlib mpmath numpy
Executar:    python riemann_app.py
Salvar PNGs: python riemann_app.py --salvar pasta_saida
"""

import sys
import os
import textwrap

import numpy as np
import mpmath as mp
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# Sem a barra de ferramentas do matplotlib: as setas dela (◀ ▶) só desfazem
# zoom e confundem com os botões de navegação do app.
plt.rcParams["toolbar"] = "None"
# Libera ← → (e espaço) para o app em vez dos atalhos padrão do matplotlib.
for _k in ("keymap.back", "keymap.forward"):
    plt.rcParams[_k] = [k for k in plt.rcParams[_k] if k not in ("left", "right")]

try:  # evita erro de acentos/símbolos em terminais Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ----------------------------------------------------------------------------
# Dados compartilhados (calculados uma vez só)
# ----------------------------------------------------------------------------
N_ZEROS = 100  # quantos zeros não triviais vamos usar

print(f"Calculando os primeiros {N_ZEROS} zeros não triviais de ζ(s)...")
# mp.zetazero(n) devolve o n-ésimo zero: 1/2 + i·t_n
ZEROS_T = np.array([float(mp.zetazero(n).imag) for n in range(1, N_ZEROS + 1)])
print("Pronto! Primeiros zeros (parte imaginária):", np.round(ZEROS_T[:5], 4))

_cache = {}


def zeta_critica(t_max=50, n=3000):
    """ζ(1/2 + it) ao longo da linha crítica."""
    if "linha" not in _cache:
        t = np.linspace(0.01, t_max, n)
        z = np.array([complex(mp.zeta(mp.mpc(0.5, ti))) for ti in t])
        _cache["linha"] = (t, z)
    return _cache["linha"]


# ----------------------------------------------------------------------------
# Lições — cada uma desenha no eixo `ax` e devolve o texto explicativo
# ----------------------------------------------------------------------------
def licao_1(fig, ax):
    ax.set_title("1. O que é a função zeta de Riemann?")
    s = np.linspace(1.05, 6, 400)
    ax.plot(s, [float(mp.zeta(x)) for x in s], lw=2, color="C0",
            label=r"$\zeta(s)=\sum_{n\geq1} 1/n^s$")
    for n_termos, cor in [(1, "C3"), (2, "C1"), (5, "C2")]:
        parcial = sum(1 / np.arange(1, n_termos + 1)[:, None] ** s)
        ax.plot(s, parcial, "--", color=cor, alpha=.8,
                label=f"soma dos {n_termos} primeiros termos")
    ax.axhline(np.pi**2 / 6, color="gray", ls=":")
    ax.annotate(r"$\zeta(2)=\pi^2/6 \approx 1{,}645$", (2, np.pi**2 / 6),
                (2.6, 2.6), arrowprops=dict(arrowstyle="->"))
    ax.set_ylim(0, 5)
    ax.set_xlabel("s (número real > 1)")
    ax.set_ylabel(r"$\zeta(s)$")
    ax.legend()
    ax.grid(alpha=.3)
    return """
    A função zeta soma 1 + 1/2^s + 1/3^s + 1/4^s + ...

    Para s real maior que 1 essa soma converge. Ex.: ζ(2) = π²/6 (Euler).
    Em s = 1 ela explode (série harmônica).

    Euler descobriu a ponte com os PRIMOS:
      ζ(s) = Π_p 1 / (1 − p^(−s))
    (produto sobre todos os primos p). Por isso
    ζ "sabe" onde estão os primos.

    Riemann (1859) estendeu ζ para NÚMEROS
    COMPLEXOS s = σ + i·t, valendo em todo o plano,
    exceto s = 1. É lá que mora a hipótese.
    """


def licao_2(fig, ax):
    ax.set_title("2. O mapa dos zeros no plano complexo")
    ax.axvspan(0, 1, color="gold", alpha=.25, label="faixa crítica 0 < σ < 1")
    ax.axvline(0.5, color="C3", lw=1.5, label="linha crítica σ = 1/2")
    triv = [-2, -4, -6, -8, -10]
    ax.plot(triv, [0] * len(triv), "s", color="C2", ms=8, label="zeros triviais (−2, −4, ...)")
    zs = ZEROS_T[ZEROS_T < 60]
    ax.plot([0.5] * len(zs), zs, "o", color="C0", ms=6, label="zeros não triviais")
    ax.plot([0.5] * len(zs), -zs, "o", color="C0", ms=6, alpha=.4)
    ax.plot(1, 0, "x", color="k", ms=12, mew=3, label="polo em s = 1")
    for k in range(3):
        ax.annotate(f"½ + {ZEROS_T[k]:.3f}i", (0.5, ZEROS_T[k]), (1.6, ZEROS_T[k] + 1),
                    fontsize=8, arrowprops=dict(arrowstyle="-", alpha=.5))
    ax.set_xlim(-11, 4)
    ax.set_ylim(-20, 60)
    ax.set_xlabel("σ = Re(s)")
    ax.set_ylabel("t = Im(s)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(alpha=.3)
    return f"""
    ζ(s) = 0 acontece em dois tipos de lugar:

    • Zeros TRIVIAIS: −2, −4, −6, ... (fáceis
      de entender, vêm de um fator seno).

    • Zeros NÃO TRIVIAIS: todos dentro da
      faixa crítica 0 < σ < 1 (amarela).
      São simétricos em relação ao eixo real.

    ★ HIPÓTESE DE RIEMANN ★
    Todo zero não trivial está exatamente
    na linha crítica σ = 1/2 (vermelha).

    Já foram verificados mais de 10 trilhões
    de zeros — todos na linha. Mas ninguém
    provou que vale para TODOS. É um dos
    problemas do Milênio (prêmio de US$ 1 mi).

    Aqui mostramos os {len(zs)} primeiros.
    """


def licao_3(fig, ax):
    ax.set_title(r"3. $|\zeta(\frac{1}{2}+it)|$ — andando sobre a linha crítica")
    t, z = zeta_critica()
    ax.plot(t, np.abs(z), color="C0", lw=1.5)
    zs = ZEROS_T[ZEROS_T < t[-1]]
    ax.plot(zs, np.zeros_like(zs), "o", color="C3", ms=6, label="zeros")
    for k, tz in enumerate(zs[:6], 1):
        ax.annotate(f"{tz:.2f}", (tz, 0), (tz, -0.35), ha="center", fontsize=8, color="C3")
    ax.set_xlabel("t")
    ax.set_ylabel(r"$|\zeta(1/2+it)|$")
    ax.set_ylim(-0.6, None)
    ax.legend()
    ax.grid(alpha=.3)
    return f"""
    Fixamos σ = 1/2 e variamos t.

    O valor absoluto |ζ(1/2 + it)| toca o
    zero várias vezes. Cada toque é um zero
    não trivial (pontos vermelhos).

    Primeiros zeros:
      t₁ ≈ {ZEROS_T[0]:.4f}
      t₂ ≈ {ZEROS_T[1]:.4f}
      t₃ ≈ {ZEROS_T[2]:.4f}

    Repare: os zeros ficam mais próximos
    conforme t cresce. O número de zeros
    até altura T é ≈ (T/2π)·log(T/2πe).

    Este é o gráfico mais clássico
    associado à Hipótese de Riemann.
    """


def licao_4(fig, ax):
    ax.set_title("4. Função Z de Hardy — contando zeros por troca de sinal")
    if "hardy" not in _cache:
        tt = np.linspace(0, 50, 2500)
        _cache["hardy"] = (tt, np.array([float(mp.siegelz(x)) for x in tt]))
    t, Z = _cache["hardy"]
    ax.plot(t, Z, color="C4", lw=1.5, label="Z(t)")
    ax.fill_between(t, Z, 0, where=Z > 0, color="C2", alpha=.2)
    ax.fill_between(t, Z, 0, where=Z < 0, color="C3", alpha=.2)
    zs = ZEROS_T[ZEROS_T < 50]
    ax.plot(zs, np.zeros_like(zs), "o", color="k", ms=5, label="zeros")
    ax.axhline(0, color="k", lw=.8)
    ax.set_xlabel("t")
    ax.set_ylabel("Z(t)")
    ax.legend()
    ax.grid(alpha=.3)
    return """
    Problema: ζ(1/2+it) é complexo, difícil de
    ver o sinal. Hardy criou uma função REAL:

      Z(t) = e^{iθ(t)} · ζ(1/2 + it)

    com |Z(t)| = |ζ(1/2+it)|.

    Como Z é real, cada vez que o gráfico
    cruza o eixo, há um zero NA LINHA crítica.

    É assim que computadores verificam a
    hipótese: contam trocas de sinal de Z(t)
    e comparam com o total de zeros na faixa
    (fórmula de Riemann–von Mangoldt).
    Se os números batem, nenhum zero "fugiu"
    da linha naquela altura.
    """


def licao_5(fig, ax):
    ax.set_title(r"5. A espiral: $\zeta(\sigma+it)$ no plano complexo, $0<t<40$")
    t, z = zeta_critica()
    m = t <= 40
    ax.plot(z[m].real, z[m].imag, color="C0", lw=1.2, label="σ = 0,5 (linha crítica)")
    if "sigma075" not in _cache:
        tt = t[m][::2]
        _cache["sigma075"] = np.array([complex(mp.zeta(mp.mpc(0.75, ti))) for ti in tt])
    z2 = _cache["sigma075"]
    ax.plot(z2.real, z2.imag, "--", color="C1", lw=1, label="σ = 0,75 (fora da linha)")
    ax.plot(0, 0, "*", color="C3", ms=18, label="origem (ζ = 0)")
    ax.set_aspect("equal")
    ax.set_xlabel("Re ζ")
    ax.set_ylabel("Im ζ")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=.3)
    return """
    Agora desenhamos o VALOR de ζ, que é um
    número complexo, enquanto t cresce.

    Na linha crítica (azul) a curva faz laços
    e PASSA PELA ORIGEM várias vezes —
    cada passagem é um zero.

    Em σ = 0,75 (laranja) a curva gira em
    torno da origem mas nunca a atinge.

    A Hipótese de Riemann diz que isso
    sempre acontece: só a curva de σ = 1/2
    passa pelo zero.
    """


def licao_6(fig, ax):
    ax.set_title("6. Mapa de |ζ(σ+it)| na faixa crítica (escuro = perto de zero)")
    if "mapa" not in _cache:
        sig = np.linspace(-0.5, 1.5, 120)
        tt = np.linspace(0.5, 50, 400)
        S, T = np.meshgrid(sig, tt)
        val = np.vectorize(lambda a, b: abs(mp.fp.zeta(complex(a, b))))(S, T)
        _cache["mapa"] = (sig, tt, np.log10(val + 1e-6))
    sig, tt, L = _cache["mapa"]
    im = ax.imshow(L, origin="lower", aspect="auto", cmap="magma",
                   extent=[sig[0], sig[-1], tt[0], tt[-1]], vmin=-1.5, vmax=1)
    fig.colorbar(im, ax=ax, label=r"$\log_{10}|\zeta|$", fraction=.04)
    ax.axvline(0.5, color="cyan", ls="--", lw=1)
    ax.axvline(0, color="w", lw=.6, alpha=.6)
    ax.axvline(1, color="w", lw=.6, alpha=.6)
    zs = ZEROS_T[ZEROS_T < 50]
    ax.plot([0.5] * len(zs), zs, "o", mfc="none", mec="cyan", ms=8)
    ax.set_xlabel("σ")
    ax.set_ylabel("t")
    return """
    Calculamos |ζ| em cada ponto de um
    retângulo do plano complexo.

    Os "buracos" escuros são os zeros. Todos
    caem exatamente na linha tracejada
    σ = 1/2 (círculos ciano).

    Linhas brancas: bordas da faixa crítica.

    Se a hipótese fosse FALSA, apareceria um
    buraco fora da linha — e, pela simetria
    ζ(s) ↔ ζ(1−s), sempre em par (σ e 1−σ).
    """


def licao_7(fig, ax):
    ax.set_title("7. Por que importa: os zeros reconstroem os primos")
    x = np.linspace(2, 60, 2500)
    # ψ(x) de Chebyshev = soma de log p sobre potências de primos p^k ≤ x
    pk = []
    for p in range(2, 61):
        if all(p % d for d in range(2, int(p**.5) + 1)):
            q = p
            while q <= 60:
                pk.append((q, np.log(p)))
                q *= p
    pk.sort()
    pos, pesos = np.array([a for a, _ in pk]), np.array([b for _, b in pk])
    psi = np.array([pesos[pos <= xi].sum() for xi in x])
    ax.step(x, psi, where="post", color="k", lw=2, label="ψ(x) real (degraus nos primos)")

    lx = np.log(x)
    base = x - np.log(2 * np.pi) - 0.5 * np.log(1 - x**-2.0)
    ax.plot(x, base, ":", color="gray", label="sem zeros: só x")
    for n, cor in [(3, "C1"), (20, "C2"), (100, "C0")]:
        rho = 0.5 + 1j * ZEROS_T[:n]
        soma = (2 * np.exp(np.outer(lx, rho)) / rho).real.sum(axis=1)
        ax.plot(x, base - soma, color=cor, lw=1.2, alpha=.85, label=f"usando {n} zeros")
    ax.set_xlabel("x")
    ax.set_ylabel("ψ(x)")
    ax.legend(fontsize=8)
    ax.grid(alpha=.3)
    return """
    A "fórmula explícita" de Riemann/von Mangoldt:

      ψ(x) = x − Σ_ρ x^ρ/ρ − log(2π) − ...

    ψ(x) conta primos (com peso log p). Cada
    zero ρ = 1/2 + it adiciona uma ONDA de
    amplitude ≈ √x. Somando ondas, os degraus
    dos primos aparecem! (3 → 20 → 100 zeros)

    Os zeros são as "notas musicais" dos primos.

    Se TODOS têm parte real 1/2, o erro na
    contagem de primos é o menor possível:
      π(x) = Li(x) + O(√x · log x).
    Um zero fora da linha causaria ondas
    maiores e primos mais "bagunçados".
    """


LICOES = [licao_1, licao_2, licao_3, licao_4, licao_5, licao_6, licao_7]


# ----------------------------------------------------------------------------
# Interface
# ----------------------------------------------------------------------------
class App:
    def __init__(self, interativo=True):
        self.fig = plt.figure(figsize=(14, 7.8))
        self.fig.canvas.manager.set_window_title("Hipótese de Riemann — aula interativa")
        self.idx = 0
        self.ax = None
        self.txt = None
        if interativo:
            b1 = self.fig.add_axes([0.63, 0.04, 0.15, 0.08])
            b2 = self.fig.add_axes([0.80, 0.04, 0.15, 0.08])
            self.btn_ant = Button(b1, "◀  Anterior", color="#dde6f5", hovercolor="#b9cdee")
            self.btn_prox = Button(b2, "Próxima  ▶", color="#cfe8d4", hovercolor="#a6d8b0")
            for b in (self.btn_ant, self.btn_prox):
                b.label.set_fontsize(13)
                b.label.set_fontweight("bold")
            # Tratamos o clique diretamente (mais confiável no Windows/Tk do que
            # o on_clicked do widget Button, que às vezes não dispara).
            self.fig.canvas.mpl_connect("button_press_event", self.clique)
            self.fig.canvas.mpl_connect("key_press_event", self.tecla)
            self._focar()
        self._fixos = list(self.fig.axes)  # eixos dos botões ficam sempre
        self.desenhar()

    def _focar(self):
        """Dá foco de teclado à área do gráfico (necessário para ← → no Tk)."""
        try:
            self.fig.canvas.get_tk_widget().focus_force()
        except Exception:
            pass

    def clique(self, ev):
        self._focar()
        if ev.inaxes is self.btn_prox.ax:
            self.ir(+1)
        elif ev.inaxes is self.btn_ant.ax:
            self.ir(-1)

    def tecla(self, ev):
        if ev.key in ("right", "pagedown", " "):
            self.ir(+1)
        elif ev.key in ("left", "pageup"):
            self.ir(-1)

    def ir(self, passo):
        self.idx = (self.idx + passo) % len(LICOES)
        self.desenhar()

    def desenhar(self):
        # remove os eixos da lição anterior (mantém os botões)
        for a in list(self.fig.axes):
            if a not in self._fixos:
                a.remove()
        if self.txt:
            self.txt.remove()
        self.ax = self.fig.add_axes([0.06, 0.1, 0.52, 0.82])
        texto = LICOES[self.idx](self.fig, self.ax)
        texto = textwrap.dedent(texto).strip()
        self.txt = self.fig.text(
            0.63, 0.93, texto, va="top", ha="left", fontsize=10.5, family="DejaVu Sans",
            bbox=dict(boxstyle="round,pad=0.8", fc="#f7f4ea", ec="#c9bf9f"))
        self.fig.suptitle(f"Hipótese de Riemann   ·   lição {self.idx + 1} de {len(LICOES)}",
                          x=0.06, ha="left", fontsize=9, color="gray")
        self.fig.canvas.draw_idle()


def main():
    if "--salvar" in sys.argv:
        pasta = sys.argv[sys.argv.index("--salvar") + 1] if len(sys.argv) > 2 else "graficos"
        os.makedirs(pasta, exist_ok=True)
        plt.switch_backend("Agg")
        app = App(interativo=False)
        for i in range(len(LICOES)):
            app.idx = i
            app.desenhar()
            caminho = os.path.join(pasta, f"licao_{i + 1}.png")
            app.fig.savefig(caminho, dpi=90)
            print("salvo:", caminho)
        return
    app = App()
    t = app.fig.canvas.new_timer(interval=500)  # foco depois que a janela abrir
    t.single_shot = True
    t.add_callback(app._focar)
    t.start()
    plt.show()


if __name__ == "__main__":
    main()
