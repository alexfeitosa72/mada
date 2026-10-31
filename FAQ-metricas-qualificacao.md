# FAQ para a qualificação — métricas e interpretação da fase empírica da MADA

Material de apoio à preparação da fala. Escopo: fase empírica, MQD-1222. Os resultados abaixo vêm das predições e métricas existentes; o suplemento não refez treinamentos. As interpretações devem ser apresentadas com seus limites, sem transformar concordância em evidência de verdade objetiva.

## 1. Existe acurácia ou F1 sem ground truth?

Sem qualquer rótulo de referência, não se calculam essas métricas de classificação. Entretanto, a referência não precisa representar uma verdade objetiva incontestável: pode ser uma anotação humana consolidada, cuja natureza e limitações precisam ser explicitadas.

Na MADA há duas referências operacionais: os rótulos majoritários do grupo masculino e os do grupo feminino. “Acerto” significa coincidência com a referência adotada naquela avaliação. Não significa demonstrar o sentimento verdadeiro da frase ou estabelecer qual grupo está correto.

**Sugestão de fala:** “A metodologia não pressupõe um ground truth único. Avaliamos a aderência das predições aos rótulos majoritários de cada grupo, tratados como referências operacionais distintas.”

## 2. Qual é a pergunta principal da MADA?

A MADA investiga se a concordância entre as predições de modelos treinados nas duas fontes é menor do que a concordância inicial entre essas fontes.

O indicador central é:

**Δκ = κ anotativo − média dos κ preditivos dos cinco folds.**

Um Δκ positivo indica redução da concordância no protocolo adotado. Acurácia e F1 respondem a uma pergunta complementar: quão bem cada modelo reproduz sua própria fonte anotativa?

**Sugestão de fala:** “Δκ caracteriza a mudança de concordância. Acurácia e F1 contextualizam a qualidade das predições que produziram essa mudança.”

## 3. O que a acurácia mede?

A proporção de frases cuja predição coincide com o rótulo de referência:

**Acurácia = número de acertos ÷ número de frases avaliadas.**

Acertar 40 de 100 frases corresponde a 40% de acurácia. Cada frase tem o mesmo peso. O número não revela, sozinho, em quais sentimentos os acertos e os erros se concentram.

## 4. O que são precisão, revocação e F1?

Para explicar o F1, podemos considerar uma classe de cada vez. Exemplo hipotético para a classe positiva:

- Existem 20 frases positivas na referência.
- O modelo prediz “positiva” para 10 frases.
- Dessas 10, oito são positivas na referência.

| Medida | Pergunta | Exemplo |
|---|---|---:|
| Precisão | Das frases chamadas de positivas, quantas são positivas na referência? | 8/10 = 80% |
| Revocação | Das frases positivas na referência, quantas foram identificadas? | 8/20 = 40% |
| F1 | Como se combinam precisão e revocação? | 53,3% |

O F1 é a média harmônica entre precisão e revocação:

**F1 = 2 × precisão × revocação ÷ (precisão + revocação).**

Também pode ser escrito como **2VP ÷ (2VP + FP + FN)**, em que VP são verdadeiros positivos, FP falsos positivos e FN falsos negativos para a classe considerada. A implementação trata os casos de divisão indefinida com `zero_division=0`.

No exemplo, o modelo foi relativamente preciso quando declarou “positiva”, mas deixou de encontrar muitas das positivas existentes. O F1 reflete essa combinação.

## 5. Acurácia e F1 não contam os mesmos acertos?

Ambos derivam das mesmas predições e referências, mas resumem os resultados de formas diferentes.

A acurácia conta acertos no conjunto inteiro. O F1 de cada classe considera os acertos daquela classe e dois tipos de erro: atribuir a classe indevidamente e deixar de identificá-la quando ela está presente.

Assim, **F1 de 0,53 não significa que 53% das frases foram classificadas corretamente**. Essa leitura pertence à acurácia. Dois modelos com a mesma acurácia podem apresentar F1 distintos se distribuírem seus erros de maneira diferente entre as classes.

**Sugestão de fala:** “A acurácia resume a proporção total de rótulos reproduzidos. O F1 considera também como os erros se distribuem na identificação de cada sentimento.”

## 6. O que diferencia F1 por classe, macro, ponderado e micro?

Não há uma única versão “normal” de F1 para um problema com três classes. É necessário declarar a forma de agregação.

| Forma | Como é calculada | Interpretação |
|---|---|---|
| Por classe | Um F1 para negativa, um para neutra e um para positiva | Diagnóstico específico de cada sentimento |
| Macro | Média simples dos três F1 | Igual importância para as três classes |
| Ponderado | Média dos F1 ponderada pela quantidade de exemplos de cada classe na referência de teste | Importância proporcional à frequência observada |
| Micro | Reúne as contagens de acertos e erros das classes antes do cálculo | Neste problema de classe única por frase, considerando todas as classes, coincide com a acurácia |

O “suporte” de uma classe é a quantidade de exemplos dessa classe na referência avaliada. Se a classe representa 40% dos exemplos do teste, seu F1 recebe peso de 40% no F1 ponderado daquele fold.

O F1 ponderado não é calculado fazendo a média entre precisão ponderada e revocação ponderada: calcula-se primeiro o F1 de cada classe e depois se aplica a ponderação.

## 7. O F1 ponderado é melhor para este estudo?

Não é universalmente melhor. É uma escolha coerente para resumir o desempenho respeitando a frequência das classes observadas, mas pode esconder dificuldades nas classes menos frequentes.

Se a pergunta for se os três sentimentos são identificados com igual importância, o F1 macro é mais alinhado a essa finalidade. Os resultados por classe permitem localizar as dificuldades que um resumo único pode ocultar.

O código original da Fase 2 já calculava F1 ponderado. O suplemento preservou essa escolha para reproduzir o protocolo e acrescentou F1 macro e diagnóstico por classe. A escolha da métrica não deve se apoiar em qual resultado parece mais favorável.

**Sugestão de fala:** “Mantivemos o F1 ponderado adotado no protocolo original. Ele resume a identificação das classes segundo sua frequência; o F1 macro e as métricas por classe oferecem diagnósticos complementares.”

## 8. Quais bases e referências foram utilizadas?

A base textual é o arquivo `dados/02-logs-processados/mqd-1222-majoritarias.csv`, com 1.222 frases. Cada frase possui duas referências:

- `classificacao_majoritaria_masculino`;
- `classificacao_majoritaria_feminino`.

São as mesmas frases com duas fontes anotativas, não dois corpora de textos distintos. O mapeamento de classes é negativa = −1, neutra = 0 e positiva = 1.

O suplemento usa `dados/03-resultados-empiricos/predicoes-completas.csv`, que contém referências, predições, identificadores e folds. Confere o alinhamento com o corpus e reproduz os valores de `dados/03-resultados-empiricos/metricas-modelos-pareados.csv`.

As verificações incluem cobertura dos 1.222 itens por algoritmo, unicidade dos identificadores, pareamento dos folds, alinhamento de rótulos e textos e reprodução das médias certificadas com tolerância absoluta de 1e-12. Os hashes e as versões estão em `dados/06-suplemento-qualificacao/verificacao.json`.

## 9. As avaliações são sempre separadas por grupo?

Acurácia e F1 principais são calculados separadamente:

| Avaliação | Modelo | Referência de teste |
|---|---|---|
| Masculina | Treinado nos rótulos masculinos | Rótulos masculinos |
| Feminina | Treinado nos rótulos femininos | Rótulos femininos |

Já a concordância compara fontes ou modelos: κ anotativo compara os dois conjuntos de rótulos; κ preditivo compara as duas predições do par.

O suplemento também contém uma tabela exploratória cruzada, comparando cada modelo à referência do outro grupo. Essa tabela é identificada separadamente e não substitui a avaliação principal.

**Sugestão de fala:** “Cada modelo é avaliado contra sua respectiva fonte. A comparação entre os modelos ocorre na análise de concordância.”

## 10. Como funciona a validação cruzada utilizada?

O código usa cinco folds, com embaralhamento e semente 42, estratificados pelos rótulos masculinos. Os dois modelos de cada par recebem os mesmos índices de treino e teste. A estratificação não é ajustada independentemente para o grupo feminino.

Em cada fold, o TF-IDF é ajustado somente nos textos de treino e aplicado ao teste. O mesmo vetorizador do fold é utilizado pelos dois modelos do par. Cada frase é avaliada fora do treino uma vez por algoritmo, produzindo uma predição de cada modelo do par.

As métricas principais são calculadas no teste de cada fold e depois agregadas pela média simples dos cinco resultados. Métricas sobre as predições out-of-fold reunidas são apresentadas separadamente: sobretudo para F1, essa agregação pode produzir valores diferentes da média por fold.

## 11. O que significa baseline? Há mais de um aqui?

Baseline é uma referência explícita de comparação. Há dois usos distintos neste material:

| Baseline | Origem | Papel |
|---|---|---|
| Anotativo | Já presente na MADA | Concordância entre os grupos antes do treinamento; referência para Δκ |
| De classificação por classe majoritária | Acrescentado no suplemento | Competidor simples para contextualizar acurácia e F1 |

O baseline de classificação não foi exigido pelo código original nem é parte obrigatória da definição de Δκ. Foi acrescentado como diagnóstico convencional de desempenho, equivalente à estratégia `most_frequent` de um classificador simples.

Baseline não significa um mínimo garantido que qualquer modelo necessariamente alcança.

## 12. Como funciona o baseline de classe majoritária?

Em cada fold e grupo:

1. Identifica-se a classe mais frequente nos rótulos de treino.
2. Prediz-se essa classe para todas as frases do teste, sem analisar seus textos.
3. Calculam-se as métricas contra os rótulos de teste daquele grupo.

Em caso de empate entre classes no treino, o suplemento escolhe o menor código numérico. A escolha não utiliza os rótulos de teste.

Exemplo hipotético: se “negativa” for a classe mais frequente do treino, o baseline responde “negativa” para qualquer frase do teste. Se 39 de 100 frases do teste forem negativas na referência, ele obtém 39% de acurácia, sem usar informação textual.

**O baseline é escolhido no treino e avaliado no teste.** A comparação não coloca a acurácia de teste dos modelos contra uma acurácia de treino.

**Sugestão de fala:** “Incluímos uma estratégia que sempre prediz a classe majoritária do treino. Ela oferece um ponto de comparação sem informação textual, avaliado nos mesmos testes dos modelos.”

## 13. Quais resultados empíricos devem ser lembrados?

Médias simples dos cinco folds; acurácia em percentual e F1 na escala de 0 a 1. Valores arredondados apenas para apresentação.

| Modelo | Acurácia masculina | Acurácia feminina | F1 ponderado masculino | F1 ponderado feminino |
|---|---:|---:|---:|---:|
| SVM | 36,66% | 34,37% | 0,3390 | 0,3395 |
| Naive Bayes | 36,99% | 35,03% | 0,3275 | 0,3394 |
| Random Forest | 36,74% | 33,55% | 0,3423 | 0,3325 |
| Regressão Logística | 35,93% | 34,86% | 0,3350 | 0,3451 |
| Baseline de classe majoritária | 39,36% | 36,50% | 0,2223 | 0,1955 |

Todos os modelos apresentam acurácia média abaixo e F1 ponderado médio acima do baseline. Essas comparações são descritivas; o suplemento não realizou teste de significância das diferenças para o baseline.

O κ anotativo é aproximadamente 0,7664. Os Δκ empíricos e IC95% registrados são:

| Modelo | Δκ | IC95% bootstrap |
|---|---:|---|
| SVM | 0,2888 | [0,2510; 0,3279] |
| Naive Bayes | 0,2984 | [0,2625; 0,3352] |
| Random Forest | 0,2645 | [0,2266; 0,3036] |
| Regressão Logística | 0,2524 | [0,2160; 0,2897] |

Fonte dos intervalos: `dados/03-resultados-empiricos/significancia-delta-kappa.csv`. O procedimento revisado usa reamostragem pareada dentro dos folds e mantém κ anotativo fixo; portanto, o intervalo não incorpora toda a incerteza possível da referência anotativa ou de novos treinamentos.

## 14. Como o modelo pode perder em acurácia e ganhar em F1 ponderado?

O baseline concentra todas as respostas em uma única classe. Isso pode gerar muitos acertos totais, mas não identifica nenhum exemplo das outras duas classes, que recebem F1 zero.

Os modelos apresentam outra distribuição de acertos e erros entre as classes. No experimento, essa distribuição produz F1 ponderado maior, mesmo com menor proporção total de acertos. O ganho no resumo ponderado não demonstra que cada classe individualmente melhorou.

Não existe contradição: as métricas valorizam aspectos diferentes das mesmas predições. Também não se deve selecionar apenas a métrica com conclusão favorável.

**Sugestão de fala:** “A regra majoritária concentra os acertos em uma classe. Os modelos têm uma distribuição diferente de erros e obtêm F1 ponderado maior, embora acertem menos frases no total.”

## 15. É adequado apresentar desvio-padrão para acurácia e F1?

Sim. Como há cinco resultados por métrica, um em cada fold, pode-se apresentar sua média e seu desvio-padrão. O suplemento calcula DP amostral entre folds, com `ddof=1`.

Por exemplo, a acurácia masculina do SVM é média de 36,66%, com DP de 2,27 pontos percentuais. Isso descreve a dispersão dos cinco resultados observados. Não descreve a variação entre cinco execuções independentes com novas sementes.

Para evitar confusão na tabela ou no gráfico, escrever: **“Média ± DP entre cinco folds; DP não representa IC.”**

Em uma figura de síntese, pode-se mostrar apenas as médias e manter o DP na tabela suplementar. A legenda precisa informar a escolha. Rótulos numéricos são úteis quando as diferenças entre resultados são pequenas.

## 16. Qual é a diferença entre DP e intervalo de confiança?

| Medida | Papel |
|---|---|
| DP entre folds | Descreve a dispersão dos resultados entre as partições observadas |
| IC | Quantifica incerteza de uma estimativa segundo um procedimento inferencial definido |

“Média ± DP” não é um IC95%. Como os conjuntos de treino dos folds se sobrepõem, os resultados não devem ser tratados automaticamente como observações independentes para construir intervalos convencionais.

Os IC de Δκ e os DP de acurácia/F1 têm origens e interpretações distintas. Se forem apresentados juntos, é necessário identificar explicitamente cada um. Sobreposição ou ausência de sobreposição das barras de DP não constitui teste de significância.

## 17. Podemos afirmar que os modelos não generalizaram bem?

A formulação mais precisa é: **os modelos apresentaram desempenho preditivo limitado nos testes da validação cruzada, especialmente em acurácia**.

A avaliação é fora do treino, portanto informa sobre desempenho em itens não utilizados no ajuste de cada fold. Contudo, não estabelece desempenho em qualquer população ou corpus externo.

O fato de nenhum modelo superar o baseline em acurácia média é uma limitação relevante. O ganho em F1 ponderado precisa ser relatado junto, sem converter a comparação em um julgamento único de superioridade geral.

Esses resultados, isoladamente, não provam que os modelos “não aprenderam nada”, não diagnosticam sobreajuste e não demonstram equivalência ao acaso. A investigação de sobreajuste exigiria examinar também o desempenho no treino e sua diferença para o teste. Uma acurácia próxima de 1/3 tampouco basta para concluir equivalência ao acaso.

**Sugestão de fala:** “A validação cruzada revelou desempenho limitado: nenhum modelo superou a regra majoritária em acurácia média, embora todos a tenham superado em F1 ponderado. Não interpretamos isso como ausência total de aprendizado nem como diagnóstico de sobreajuste.”

## 18. Isso invalida a redução de concordância observada?

Não elimina o resultado numérico de Δκ. Os quatro valores são positivos e os intervalos registrados permanecem acima de zero, nas condições do procedimento adotado.

Entretanto, o desempenho limitado restringe a interpretação substantiva. Menor concordância entre predições não demonstra, por si só, reprodução ou amplificação de perspectivas sociais efetivamente aprendidas. Erros preditivos, instabilidade e distribuições marginais também podem influenciar κ.

Assim, a afirmação sustentada é a redução de concordância no protocolo. Atribuir causalmente essa redução à amplificação de perspectivas exige evidências adicionais que esta avaliação não fornece.

**Sugestão de fala:** “O resultado operacional é uma redução de concordância entre as predições. O desempenho preditivo recomenda cautela em atribuir essa redução exclusivamente a perspectivas aprendidas.”

## 19. O que veio do protocolo e o que foi acrescentado no suplemento?

| Elemento | Origem |
|---|---|
| Acurácia e F1 ponderado contra a própria fonte | Já calculados na Fase 2 |
| Concordância anotativa, preditiva e Δκ | Núcleo do protocolo original |
| Baseline de classificação por classe majoritária | Acrescentado no suplemento |
| F1 macro, DP de F1 e métricas por classe no suplemento | Diagnósticos adicionais reconstruídos das predições salvas |
| Referência cruzada entre grupos | Análise exploratória adicional, identificada separadamente |

Nenhuma dessas análises adicionais transforma um grupo em árbitro da verdade. O suplemento não refez os treinamentos e não substituiu os resultados certificados.

## 20. Qual interpretação integrada apresentar à banca?

A interpretação proposta tem três partes:

1. **Resultado observado:** os pares de modelos apresentam menor concordância que as fontes anotativas, com Δκ positivo nos quatro algoritmos.
2. **Contexto preditivo:** as acurácias ficam abaixo da regra majoritária; o F1 ponderado fica acima. O desempenho depende da métrica e é limitado em termos absolutos.
3. **Limite explicativo:** a mudança de concordância não pode ser atribuída exclusivamente à amplificação de perspectivas aprendidas, pois a qualidade das predições e a estrutura dos erros também precisam ser consideradas.

Evitar “os modelos são melhores que o baseline” sem especificar a métrica; “não generalizaram” sem delimitar o protocolo; “o F1 é melhor que a acurácia”; e “Δκ prova amplificação de viés de gênero”.

## 21. Sugestão de fala integrada, em aproximadamente um minuto

> “Na fase empírica, utilizamos as mesmas 1.222 frases com duas referências anotativas, correspondentes aos rótulos majoritários de cada grupo. Cada modelo é avaliado contra sua respectiva referência, sem pressupor um ground truth único.
>
> A acurácia mostra a proporção total de rótulos reproduzidos. O F1 ponderado complementa essa leitura ao combinar precisão e revocação por classe, com pesos proporcionais à frequência das classes.
>
> Os modelos ficaram abaixo da estratégia de classe majoritária em acurácia média, mas acima dela em F1 ponderado. Esse contexto revela desempenho preditivo limitado e diferenças na distribuição dos erros.
>
> Paralelamente, observamos Δκ positivo nos quatro algoritmos, com os intervalos calculados acima de zero. Portanto, há redução de concordância nas condições do experimento. A interpretação dessa redução como amplificação de perspectivas aprendidas exige cautela, porque erros de classificação também podem contribuir para o resultado.”

## 22. Respostas breves para perguntas prováveis

**“Sem ground truth, por que apresentar acurácia?”**

> “Há referências anotativas por grupo. A métrica mede aderência a essas referências, sem estabelecê-las como uma verdade objetiva única.”

**“Por que usar F1 ponderado?”**

> “Ele já fazia parte do protocolo e resume o F1 das classes segundo sua frequência. Não o tratamos como universalmente superior; o macro e os resultados por classe complementam o diagnóstico.”

**“Vocês venceram o baseline?”**

> “Em F1 ponderado médio, sim; em acurácia média, não. Essa comparação é descritiva e deve ser apresentada com a métrica explícita.”

**“Por que acrescentar uma regra que ignora o texto?”**

> “Para verificar o desempenho em relação a uma estratégia simples que explora apenas a frequência das classes. Ela contextualiza o ganho associado ao classificador.”

**“Isso prova que os modelos sofreram sobreajuste?”**

> “Não. Para diagnosticar sobreajuste, precisaríamos examinar a diferença entre treino e teste. Aqui identificamos desempenho limitado nos testes da validação cruzada.”

**“As barras de erro são IC95%?”**

> “Nos gráficos de acurácia e F1 do suplemento, são DP entre os cinco folds. Os intervalos de Δκ são bootstrap e têm outro significado.”

**“Com esse desempenho, o que permanece da conclusão?”**

> “Permanece a redução de concordância medida por Δκ no protocolo. A limitação recai sobre atribuir essa redução exclusivamente à amplificação de perspectivas aprendidas.”

## Fontes e arquivos de apoio

- [Código da fase empírica](fase2-dados-empiricos.ipynb).
- [Notebook suplementar](suplemento-metricas-qualificacao.ipynb).
- [Script que reconstrói o suplemento](suplemento-metricas-qualificacao.py).
- [Tabela de desempenho e baseline](dados/06-suplemento-qualificacao/resumo-fidelidade-fonte.csv).
- [Resultados de Δκ e IC95%](dados/03-resultados-empiricos/significancia-delta-kappa.csv).
- [Definição de acurácia — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html).
- [Definição de F1 e formas de agregação — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html).
- [Baseline de classificação — DummyClassifier](https://scikit-learn.org/1.5/modules/generated/sklearn.dummy.DummyClassifier.html).
- [Validação cruzada e apresentação de média/DP — scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html).
- [Bates, Hastie e Tibshirani: incerteza na validação cruzada](https://arxiv.org/abs/2104.00673).
