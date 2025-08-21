# ardesi_predictor.py
import argparse, math, random, time
from collections import deque, Counter

# ---------- primalità (Miller–Rabin) ----------
def is_probable_prime(n: int, rounds: int = 8) -> bool:
    if n < 2: return False
    small = [2,3,5,7,11,13,17,19,23,29]
    for p in small:
        if n == p: return True
        if n % p == 0: return False
    d, r = n-1, 0
    while d % 2 == 0:
        d //= 2; r += 1
    for _ in range(rounds):
        a = random.randrange(2, n-1)
        x = pow(a, d, n)
        if x in (1, n-1): continue
        for _ in range(r-1):
            x = (x*x) % n
            if x == n-1: break
        else:
            return False
    return True

# ---------- corridoi mod 30 ----------
RES = [1,7,11,13,17,19,23,29]   # 8 residui coprimi (mod 30)

def block_candidates(base: int):
    """Restituisce i candidati del blocco [base, base+29] nei corridoi."""
    return [base + r for r in RES]

# ---------- entropia percettiva (baseline teorica) ----------
# E(n) = ln(C(30,8)) + ln(n / ln n);  E_norm = E / max(E, 1)
LN_C_30_8 = math.log(5852925)  # C(30,8) = 5_852_925
def entropy_norm(n: int) -> float:
    if n < 3: return 0.0
    En = LN_C_30_8 + math.log(n / math.log(n))
    return En / max(En, 1.0)

# ---------- P_log locale (stima online) ----------
class LocalCorridorModel:
    """
    Stima semplice: frequenze dei residui osservati in una finestra scorrevole
    di ultimi W blocchi (in pratica 8*W posizioni). In assenza di dati -> uniforme.
    """
    def __init__(self, W: int = 128):
        self.W = W
        self.window = deque(maxlen=W)   # store counters per blocco
        self.global_counts = Counter()

    def update_with_block_result(self, base: int, primes_in_block: list[int]):
        """
        Aggiorna il modello sapendo quali posizioni del blocco risultano prime.
        Nota: per una stima 'pura', potresti aggiornare SOLO con i k testati
        e confermati; qui aggiorniamo con tutte le prime trovate nel blocco.
        """
        cnt = Counter()
        for p in primes_in_block:
            r = (p - base) % 30
            if r in RES:
                cnt[r] += 1
        # rimuovi il blocco più vecchio dall’aggregato
        if len(self.window) == self.window.maxlen:
            old = self.window[0]
            for r,v in old.items(): self.global_counts[r] -= v
        self.window.append(cnt)
        for r,v in cnt.items(): self.global_counts[r] += v

    def plog(self, candidate: int) -> float:
        r = candidate % 30
        tot = sum(self.global_counts.values())
        if tot <= 0:
            return 1.0 / len(RES)  # uniforme all'inizio
        # smoothing di Laplace per evitare zeri
        return (self.global_counts[r] + 1.0) / (tot + len(RES))

# ---------- main: predittore k-candidati per blocco ----------
def parse_args():
    ap = argparse.ArgumentParser(description="Metodo Ardesi: predittore k-candidati (corridoi + entropia).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--range", nargs=2, type=int, metavar=("START","STOP"))
    g.add_argument("--exp", nargs=2, type=int, metavar=("X","Y"),
                   help="Intervallo [10^min(X,Y), 10^max(X,Y)]")
    ap.add_argument("-k", type=int, default=3, help="k candidati per blocco (default: 3)")
    ap.add_argument("--alpha", type=float, default=1.0, help="peso per P_log")
    ap.add_argument("--beta", type=float, default=1.0, help="peso per E_norm")
    ap.add_argument("--rounds", type=int, default=8, help="round Miller–Rabin")
    ap.add_argument("--win", type=int, default=128, help="finestra blocchi per modello locale")
    return ap.parse_args()

def main():
    args = parse_args()
    if args.exp:
        X,Y = args.exp; start = 10**min(X,Y); stop = 10**max(X,Y)
    else:
        s,t = args.range; start,stop = (s,t) if s<=t else (t,s)

    start = max(2, start)
    # allinea all’inizio di un blocco mod 30
    base = start - (start % 30)
    model = LocalCorridorModel(W=args.win)

    tested = 0
    found  = []
    first4 = []
    t0 = time.perf_counter()

    while base <= stop:
        cand = [c for c in block_candidates(base) if start <= c <= stop]
        if not cand:
            base += 30
            continue

        En = entropy_norm(base if base>0 else 2)
        # ranking dei candidati
        scored = []
        for c in cand:
            S = args.alpha * model.plog(c) + args.beta * En
            scored.append((S, c))
        scored.sort(reverse=True)
        topk = [c for _,c in scored[:args.k]]

        # testa solo i top-k nel blocco corrente
        primes_in_block = []
        for c in topk:
            tested += 1
            if is_probable_prime(c, rounds=args.rounds):
                primes_in_block.append(c)
                found.append(c)
                if len(first4) < 4: first4.append(c)

        # aggiorna il modello locale con le prime del blocco
        model.update_with_block_result(base, primes_in_block)

        base += 30

    t1 = time.perf_counter()

    print(f"k per blocco: {args.k}  |  alpha={args.alpha}  beta={args.beta}  |  finestra={args.win}")
    print(f"Numeri testati (top-k): {tested}")
    print(f"Probabili primi trovati: {len(found)}")
    if first4:
        print("Primi 4 trovati:")
        for x in first4: print(f"  {x}  (Prob. ≈ 1 - 4^-{args.rounds})")
    else:
        print("Primi 4 trovati: (nessuno)")
    print(f"Tempo di calcolo: {t1 - t0:.3f} s")

if __name__ == "__main__":
    main()
