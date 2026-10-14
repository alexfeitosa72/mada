# Principais Insights Estatísticos — MADA Fase 2

**Data de geração:** 14/10/2026 16:51:03

## 1) Baseline entre anotadores
- **Cohen's Kappa inicial:** `0.7664`
- **IC 95% do Kappa (bootstrap):** `[0.7362, 0.7963]`
- **Concordância observada:** `0.8453` (84.53%)
- **Cramér's V:** `0.7679`

> Interpretação: há concordância inicial relativamente alta entre os grupos de anotadores.

## 2) Concordância entre modelos pareados
- **Média de κ_pred (4 classificadores):** `0.4854`
- **Melhor κ_pred:** `LR` com `0.5191`
- **Pior κ_pred:** `RF` com `0.4526`

## 3) Amplificação de viés (Δκ = κ_anot - κ_pred)
- **Δκ médio:** `+0.2810`
- **Maior amplificação:** `RF` com `Δκ=+0.3138`
- **Menor amplificação:** `LR` com `Δκ=+0.2473`
- **Modelos com amplificação detectada:** `4/4`

### Severidade (Landis & Koch, 1977)
- **Nulo:** 0 modelo(s)
- **Restrito:** 4 modelo(s)
- **Amplo:** 0 modelo(s)
- **Acentuado:** 0 modelo(s)

## 4) Significância estatística (bootstrap de Δκ)
- **Modelos com Δκ estatisticamente significativo:** `4/4`
  - SVM: Δκ observado `+0.2719`, IC95% `[+0.2358, +0.3102]`, direção: **AMPLIFICA**
  - NB: Δκ observado `+0.2909`, IC95% `[+0.2545, +0.3287]`, direção: **AMPLIFICA**
  - RF: Δκ observado `+0.3138`, IC95% `[+0.2748, +0.3537]`, direção: **AMPLIFICA**
  - LR: Δκ observado `+0.2473`, IC95% `[+0.2109, +0.2854]`, direção: **AMPLIFICA**

## 5) Conclusão executiva
- Os classificadores reproduzem padrões com **menor concordância inter-grupos** do que a observada entre anotadores humanos.
- Houve **amplificação de viés em todos os modelos testados** nesta configuração experimental.
- A queda de faixa de concordância foi predominantemente **Restrito** (1 faixa em Landis & Koch), mas consistente.

---
Arquivo gerado automaticamente em: `dados\03-resultados-empiricos\insights-estatisticos-fase2.md`