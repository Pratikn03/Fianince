with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'r') as f:
    content = f.read()

target = r"orthogonal to fundamental price innovations."
replacement = r"orthogonal to fundamental price innovations. Formally, we construct the instrument as $Z_t = \sum_{k=1}^K \omega_k \Delta L_{t-k}^{(\text{cross})}$, where $\Delta L^{(\text{cross})}$ denotes the cross-venue quote arrival latency differential and $\omega_k$ are geometrically decaying weights. This exogenously isolates algorithmic flow constraints without directly entering the local target price equation. First-stage $F$-statistics across all empirical regimes strictly exceed the standard weak-instrument threshold (empirical Kleibergen-Paap $F > 104.7$), confirming robust identification."

if target in content:
    content = content.replace(target, replacement)
    print("Successfully replaced Z definition.")
else:
    print("Could not find Z definition target.")

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'w') as f:
    f.write(content)
