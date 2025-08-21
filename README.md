# Metodo Ardesi vs Wheel Factorization

Questo repository raccoglie il materiale teorico e sperimentale legato al **Metodo Ardesi** per la previsione dei numeri primi e al confronto con il metodo classico della **Wheel Factorization**.

## 📖 Introduzione
Il Metodo Ardesi nasce dall’osservazione dei **corridoi mod 30** (i residui coprimi {1,7,11,13,17,19,23,29}) e introduce un approccio **predittivo e probabilistico** basato su log binari ed entropia.  
A differenza della Wheel classica, che esplora tutti i residui coprimi di un modulo, Ardesi seleziona solo un **sottoinsieme ottimizzato (top-k)** dei candidati per ogni blocco, riducendo drasticamente i test di primalità.

## 🧩 Teoria
- **Wheel Factorization**: riduce i candidati escludendo multipli di primi fino a un modulo M. Cresce con complessità ≈ (φ(M)/M)·ln(n).
- **Metodo Ardesi**: parte dai corridoi mod 30, calcola uno score basato su probabilità locali (P_log) ed entropia normalizzata (E_norm), e sceglie solo i k candidati più promettenti.  
  → Costo ≈ O(k), quasi costante anche al crescere di n.

## 📊 Confronto
- **Wheel [2,3,5] (mod 30)**: esaustiva, trova tutti i primi ma più lenta.  
- **Wheel [2,3,5,7] (mod 210)**: più efficiente, meno candidati e tempi ridotti.  
- **Ardesi (k=1 o k=3)**: non esaustivo, ma intercetta una parte consistente dei primi testando pochissimi numeri.  
  - Esempio: con k=1 si testano ~333.000 numeri invece di milioni, trovando comunque decine di migliaia di primi.

## 🚀 Uso del codice
Il file `ardesi_predictor.py` (da mantenere a parte) implementa il predittore. Esempi di esecuzione:

```bash
# Intervallo definito esplicitamente
python ardesi_predictor.py --range 12345678912300 12345688912300 -k 1

# Intervallo in notazione esponenziale (10^X - 10^Y)
python ardesi_predictor.py --exp 10 11 -k 3 --alpha 1.0 --beta 1.0

# Wheel di confronto
python ardesi_prime_wheel.py --range 12345678912300 12345688912300 --only-primes --wheel 2,3,5
python ardesi_prime_wheel.py --range 12345678912300 12345688912300 --only-primes --wheel 2,3,5,7
```

## 📂 Contenuto
- `Visione_Unificata_dei_Corridoi_dei_Numeri_Primi_3.pdf` → documento teorico sul Metodo Ardesi.
- `Confronto_tra_Wheel_e_Griglia_Binaria__Pattern_Binario_Ardesi_.pdf` → confronto dettagliato tra approcci.
- `screenshot_test1.png`, `screenshot_test2.png`, `screenshot_test3.png` → risultati sperimentali.

## ✨ Conclusioni
Il Metodo Ardesi è **simile alla wheel** perché parte dagli stessi corridoi coprimi, ma si distingue per l’**esplorazione predittiva**: non tratta tutti i corridoi allo stesso modo, bensì sceglie quelli più promettenti.  
Questo lo rende più **adattivo, flessibile e scalabile** nel lungo termine.
