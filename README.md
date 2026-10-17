# MADA. Metodologia de Amplificação de Divergências Anotativas

Projeto de pesquisa de mestrado dedicado a investigar se modelos de classificação supervisionada de sentimentos preservam ou ampliam divergências entre rótulos consolidados por grupos de anotadores definidos pelo gênero autodeclarado, no contexto do português brasileiro.

A MADA compara a concordância entre as fontes anotativas com a concordância entre as predições dos modelos. A medida central é **Δκ = κ_anotativo − κ_preditivo**. Valores positivos de Δκ indicam redução da concordância nas predições em relação à concordância anotativa inicial, segundo o protocolo adotado.

## Organização

Os quatro notebooks oficiais, na raiz do repositório, compõem o fluxo de processamento:

| Ordem | Notebook | Função |
| --- | --- | --- |
| 1 | `fase1-tratamento-logs.ipynb` | Tratamento dos registros e consolidação dos rótulos anotativos. |
| 2 | `fase2-dados-empiricos.ipynb` | Treinamento, avaliação e análise de divergências no corpus empírico. |
| 3 | `fase3-dados-sinteticos.ipynb` | Avaliação dos classificadores em 12 cenários sintéticos. |
| 4 | `fase4-resultados-gerais.ipynb` | Integração dos resultados das Fases 2 e 3, sem novos treinamentos. |

O diretório `dados/` contém entradas anonimizadas, dados intermediários e resultados científicos versionados. A organização inclui `01-logs-brutos/`, `02-logs-processados/`, `03-resultados-empiricos/` e `04-resultados-sinteticos/`. O arquivo `mqd-1465.csv` constitui a entrada original da Fase 1; os cenários sintéticos mantêm os nomes históricos `SynSA-XX.csv`. As saídas dos notebooks são regeneráveis pelo fluxo experimental, mas a regeneração **não** é requisito para consulta ou uso dos resultados certificados já versionados.

## Ambiente e instalação

Ambiente local de referência: **Python 3.13.15**. Os arquivos `requirements.txt` e `requirements-lock.txt` documentam, respectivamente, as dependências diretas e o conjunto completo de versões do ambiente certificado. Para reconstrução fiel do ambiente de dependências, priorizar o lockfile.

```bash
python -m venv .venv
```

Ative o ambiente virtual pelo mecanismo correspondente ao seu sistema operacional e execute:

```bash
python -m pip install -r requirements-lock.txt
python -m pip check
```

No VS Code, selecione o interpretador da `.venv` como kernel dos notebooks. Execute as fases na ordem indicada, somente quando houver intenção explícita de regenerar os artefatos. **Preserve os arquivos certificados antes de qualquer execução que possa regravá-los.**

## Resultados de referência

**Fase 1.** Corpus MQD-1222: 1.222 frases, 1.033 concordâncias e 189 divergências. Concordância anotativa κ = **0,766397**, IC95% bootstrap **[0,734826; 0,795834]**. A sequência histórica de blocos preservada é `[10, 1, 2, 3, 4, 5, 6, 7, 8, 9]`.

**Fase 2.** Resultados empíricos certificados:

| Modelo | κ preditivo | Δκ |
| --- | ---: | ---: |
| SVM | 0,477604 | 0,288793 |
| Naive Bayes | 0,467999 | 0,298398 |
| Random Forest | 0,501914 | 0,264483 |
| Regressão Logística | 0,513972 | 0,252425 |

Médias: κ preditivo **0,490372** e Δκ **0,276025**. Os quatro IC95% bootstrap de Δκ permanecem integralmente acima de zero. O TF-IDF é ajustado nos dados de treinamento de cada fold; usa-se `StratifiedKFold` com cinco partições, `shuffle=True`, `random_state=42` e estratificação pelos rótulos masculinos.

**Fase 3.** São 12 cenários `SynSA-XX` de 999 registros cada. Os 48 valores certificados de Δκ são positivos. Médias de Δκ: SVM **0,209214**, NB **0,200795**, RF **0,473822**, LR **0,193537**.

**Fase 4.** Integra os resultados empíricos e sintéticos, reproduzindo oito valores consolidados de Δκ com quatro casas decimais, sem novos treinamentos.

## Google Colab e limites de portabilidade

A portabilidade foi avaliada no Colab com **Python 3.13.16** e um ambiente virtual científico isolado, instalado a partir de `requirements-lock.txt`. As dependências foram importadas nas versões fixadas e `pip check` não encontrou conflitos. Os quatro notebooks passaram na análise sintática (86 células de código); suas inicializações foram aprovadas em subprocessos com a detecção do Colab simulada. A execução direta no kernel real do Colab confirmou acesso ao repositório e ao ambiente virtual; esse kernel também conseguiu acionar o Python isolado e importar as dependências certificadas.

**Escopo da validação:** não foram executados os pipelines ou treinamentos completos no Colab, nem se certificou que a interface interativa utiliza diretamente o kernel do ambiente virtual. Portanto, a portabilidade estrutural e operacional controlada foi aprovada **com ressalvas**. A diferença entre Python 3.13.15 (local) e 3.13.16 (Colab) não autoriza alegar equivalência científica estrita. Permanecem quatro avisos não bloqueantes de `SyntaxWarning` relativos a sequências de escape na Fase 4.

## Integridade e versionamento

Os resultados científicos apresentados foram previamente reconstruídos e auditados no ambiente local. Alterações em algoritmos, parâmetros experimentais, dados ou arquivos de resultados exigem nova avaliação específica e não fazem parte do encerramento da portabilidade. O repositório histórico `MIVA` é independente e deve permanecer inalterado. O projeto `mada` preserva seus dados anonimizados e artefatos científicos versionados, permitindo rastrear os resultados de referência sem exigir reexecuções desnecessárias.
