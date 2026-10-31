"""Suplemento independente: somente leitura dos resultados certificados.

Execute com o Python do projeto. Não treina modelos nem altera as Fases 1–4.
"""
from pathlib import Path
import base64
import hashlib
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, f1_score

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dados/06-suplemento-qualificacao'
MODELOS = ['SVM', 'NB', 'RF', 'LR']
GRUPOS = ['masculino', 'feminino']
LABELS = [-1, 0, 1]


def analisar():
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [ROOT / 'dados/03-resultados-empiricos/predicoes-completas.csv',
             ROOT / 'dados/03-resultados-empiricos/metricas-modelos-pareados.csv',
             ROOT / 'dados/02-logs-processados/mqd-1222-majoritarias.csv',
             ROOT / 'fase2-dados-empiricos.ipynb', ROOT / 'fase3-dados-sinteticos.ipynb']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    pred = pd.read_csv(paths[0])
    certificado = pd.read_csv(paths[1]).set_index('modelo')
    corpus = pd.read_csv(paths[2], sep='\t')
    mapping = {'negativa': -1, 'neutra': 0, 'positiva': 1}
    assert len(corpus) == 1222
    assert set(pred.modelo) == set(MODELOS)
    assert not pred.duplicated(['modelo', 'frase_id']).any()
    folds = []
    classes = []
    pooled = []
    cruzadas = []
    fold_ref = pred[pred.modelo == 'SVM'].set_index('frase_id').fold.sort_index()
    for modelo in MODELOS:
        dados = pred[pred.modelo == modelo]
        assert set(dados.frase_id) == set(range(len(corpus)))
        assert set(dados.fold) == set(range(1, 6))
        pd.testing.assert_series_equal(dados.set_index('frase_id').fold.sort_index(), fold_ref)
        for grupo in GRUPOS:
            y = dados[f'real_{grupo}']
            yp = dados[f'pred_{grupo}']
            assert set(y) == set(LABELS) and set(yp) <= set(LABELS)
            esperado = corpus[f'classificacao_majoritaria_{grupo}'].map(mapping)
            np.testing.assert_array_equal(y, esperado.iloc[dados.frase_id])
            assert all(dados.frase.to_numpy() == corpus.frase.iloc[dados.frase_id].str[:100].to_numpy())
            pooled.append(dict(modelo=modelo, grupo=grupo, n=len(y),
                               acuracia=accuracy_score(y, yp),
                               f1_ponderado=f1_score(y, yp, average='weighted', zero_division=0),
                               f1_macro=f1_score(y, yp, average='macro', zero_division=0)))
            pr, re, f1, suporte = precision_recall_fscore_support(y, yp, labels=LABELS, zero_division=0)
            for j, label in enumerate(LABELS):
                classes.append(dict(modelo=modelo, grupo=grupo, classe=label,
                                    sentimento={-1:'negativa',0:'neutra',1:'positiva'}[label],
                                    precisao=pr[j], revocacao=re[j], f1=f1[j], suporte=int(suporte[j])))
            outro = GRUPOS[1 - GRUPOS.index(grupo)]
            cruzadas.append(dict(modelo=modelo, modelo_treinado_em=grupo, referencia=outro,
                                 acuracia=accuracy_score(dados[f'real_{outro}'], yp),
                                 f1_ponderado=f1_score(dados[f'real_{outro}'], yp, average='weighted', zero_division=0)))
            for fold, d in dados.groupby('fold'):
                teste = d[f'real_{grupo}']
                previsao = d[f'pred_{grupo}']
                treino = dados[dados.fold != fold][f'real_{grupo}']
                # Empates da moda: menor código, regra explícita e determinística.
                majoritaria = int(treino.mode().min())
                base = np.full(len(teste), majoritaria)
                folds.append(dict(modelo=modelo, grupo=grupo, fold=fold, n=len(d),
                                  acuracia=accuracy_score(teste, previsao),
                                  f1_ponderado=f1_score(teste, previsao, average='weighted', zero_division=0),
                                  f1_macro=f1_score(teste, previsao, labels=LABELS, average='macro', zero_division=0),
                                  baseline_classe=majoritaria,
                                  baseline_acuracia=accuracy_score(teste, base),
                                  baseline_f1_ponderado=f1_score(teste, base, average='weighted', zero_division=0)))
    folds = pd.DataFrame(folds)
    resumo = folds.groupby(['modelo','grupo'], sort=False).agg(
        acuracia_media=('acuracia','mean'), acuracia_dp=('acuracia','std'),
        f1_ponderado_medio=('f1_ponderado','mean'), f1_ponderado_dp=('f1_ponderado','std'),
        f1_macro_medio=('f1_macro','mean'), f1_macro_dp=('f1_macro','std'),
        baseline_acuracia=('baseline_acuracia','mean'),
        baseline_f1_ponderado=('baseline_f1_ponderado','mean')).reset_index()
    resumo['ganho_acuracia_pp'] = 100*(resumo.acuracia_media-resumo.baseline_acuracia)
    for r in resumo.itertuples():
        c = certificado.loc[r.modelo]
        for calculado, coluna in [(r.acuracia_media,f'acc_{r.grupo}_mean'),
                                  (r.acuracia_dp,f'acc_{r.grupo}_std'),
                                  (r.f1_ponderado_medio,f'f1_{r.grupo}_mean')]:
            np.testing.assert_allclose(calculado, c[coluna], rtol=0, atol=1e-12)
    tabelas = {'resumo-fidelidade-fonte':resumo, 'metricas-por-fold':folds,
               'metricas-oof-reunidas':pd.DataFrame(pooled),
               'metricas-por-classe':pd.DataFrame(classes),
               'referencia-cruzada-exploratoria':pd.DataFrame(cruzadas)}
    for nome, tabela in tabelas.items():
        tabela.to_csv(OUT / f'{nome}.csv', index=False, encoding='utf-8-sig')
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    figuras = []
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.5))
    x = np.arange(4)
    for ax, metrica, dp, titulo in zip(axes, ['acuracia_media','f1_ponderado_medio'],
            ['acuracia_dp','f1_ponderado_dp'], ['Acurácia','F1 ponderado']):
        for j, (grupo, cor) in enumerate(zip(GRUPOS,['#0c4a6e','#0284c7'])):
            r = resumo[resumo.grupo == grupo].set_index('modelo').loc[MODELOS]
            barras = ax.bar(x+(j-.5)*.36, r[metrica]*100, .36, yerr=r[dp]*100,
                           capsize=4, label=grupo.capitalize(), color=cor)
            ax.bar_label(barras, labels=[f'{v:.1f}' for v in r[metrica]*100], padding=17, fontsize=10)
        ax.set(xticks=x, xticklabels=MODELOS, ylim=(0,100), ylabel='Percentual (%)', title=titulo)
        ax.grid(axis='y',alpha=.18)
    axes[0].legend(loc='upper right')
    fig.suptitle('Aderência às referências de cada grupo — MQD-1222', fontsize=16)
    fig.text(.5,.015,'Média de 5 folds; barras de erro = desvio-padrão amostral, não IC. Referência: rótulos majoritários de cada grupo.', ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.06,1,.93))
    figuras.append(('acuracia-f1-fontes',fig))
    fig, axes = plt.subplots(1,2,figsize=(13.5,5.5),sharey=True)
    for ax, grupo in zip(axes,GRUPOS):
        r=resumo[resumo.grupo == grupo].set_index('modelo').loc[MODELOS]
        ax.bar(x-.18,r.acuracia_media*100,.36,label='Modelo',color='#0c4a6e')
        ax.bar(x+.18,r.baseline_acuracia*100,.36,label='Classe majoritária do treino',color='#94a3b8')
        ax.set(xticks=x,xticklabels=MODELOS,ylim=(0,100),title=f'Referência: grupo {grupo}',ylabel='Acurácia (%)')
        ax.legend(fontsize=9)
        ax.grid(axis='y',alpha=.18)
    fig.suptitle('Contexto de desempenho: baseline sem informação textual',fontsize=16)
    fig.text(.5,.015,'Mesmos folds; baseline definido somente pelos rótulos do treino. Comparação descritiva, sem teste de superioridade.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.06,1,.93))
    figuras.append(('baseline-acuracia',fig))
    for nome, fig in figuras:
        fig.savefig(OUT / f'{nome}.png',dpi=200)
        fig.savefig(OUT / f'{nome}.svg')
        plt.close(fig)
    import sklearn
    manifest = {'python':sys.version,'pandas':pd.__version__,'numpy':np.__version__,
                'sklearn':sklearn.__version__,'matplotlib':matplotlib.__version__,
                'entradas_sha256':hashes,
                'validacoes':'Cobertura 1222/modelo; IDs únicos; folds pareados; rótulos e texto alinhados ao corpus; médias e DP certificados reproduzidos a 1e-12.',
                'sintetico':'Acurácia/F1 não recuperáveis dos resumos salvos; nenhum treinamento executado.'}
    (OUT/'verificacao.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
    return tabelas


def notebook(tabelas):
    cells=[]
    def md(s):
        cells.append(dict(cell_type='markdown',metadata={},source=s.splitlines(keepends=True)))
    def code(s, outputs=None):
        cells.append(dict(cell_type='code',metadata={},source=s.splitlines(keepends=True),
                          execution_count=sum(c['cell_type']=='code' for c in cells)+1,outputs=outputs or []))
    def table(nome):
        d=tabelas[nome]
        code(f"display(tabelas[{nome!r}])",[dict(output_type='display_data',metadata={},
             data={'text/html':[d.to_html(index=False,float_format=lambda x:f'{x:.6f}')],
                   'text/plain':[d.to_string(index=False)]})])
    def pic(nome):
        code(f"display(Image(filename=str(mod.OUT / '{nome}.png')))",
             [dict(output_type='display_data',metadata={},data={'image/png':base64.b64encode((OUT/f'{nome}.png').read_bytes()).decode()})])
    md('''# Suplemento para qualificação: acurácia e F1 na MADA

**Conclusão:** acurácia e F1 exigem rótulos de referência. Não exigem que esses rótulos sejam uma verdade objetiva incontestável. Aqui, os consensos majoritários de cada grupo são **referências operacionais distintas**. As métricas abaixo medem aderência à fonte anotativa correspondente; não validam o sentimento verdadeiro nem demonstram qual grupo está correto.

Suplemento independente, produzido a partir das predições out-of-fold já salvas, sem novos treinamentos ou alteração dos resultados certificados. As tabelas e figuras estão incorporadas neste notebook e podem ser consultadas sem executar as células.
''')
    md('''## O que a metodologia propõe

1. A Fase 1 consolida anotações por grupo e obtém o MQD-1222.
2. A Fase 2 treina dois modelos de cada algoritmo, cada um com os rótulos de um grupo, nos mesmos cinco folds (estratificação masculina, shuffle e seed 42). O TF-IDF é ajustado apenas no treino.
3. A medida principal compara a concordância anotativa à preditiva: **Δκ = κ_anotativo − média dos κ_preditivos dos folds**. Δκ positivo indica redução da concordância segundo esse protocolo, sem estabelecer uma verdade externa.
4. Acurácia e F1 ponderado já são calculados na célula 19 (índice começando em zero) da Fase 2, em relação à própria fonte, e exportados em `metricas-modelos-pareados.csv`.

**Distinção para a banca:** concordância entre os dois modelos não é acurácia de classificação. As matrizes entre predições da Fase 2 são tabelas de contingência; as métricas de classificação comparam cada predição ao respectivo rótulo anotativo de teste.
''')
    code("from pathlib import Path\nimport importlib.util\nfrom IPython.display import display, Image\nraiz = Path.cwd()\nif not (raiz / 'suplemento-metricas-qualificacao.py').exists():\n    raise FileNotFoundError('Execute este notebook na raiz do repositório mada.')\nspec = importlib.util.spec_from_file_location('suplemento', raiz / 'suplemento-metricas-qualificacao.py')\nmod = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(mod)\ntabelas = mod.analisar()\nprint('Métricas reconstruídas e verificadas; nenhum treinamento executado.')",
         [dict(output_type='stream',name='stdout',text=['Métricas reconstruídas e verificadas; nenhum treinamento executado.\n'])])
    md('''## Tabela principal — média dos cinco folds

Valores entre 0 e 1. **F1 ponderado** é a média dos F1 por classe ponderada pelo suporte no teste, conforme a implementação original; F1 macro atribui o mesmo peso às três classes. DP é desvio-padrão amostral entre folds (ddof=1), não intervalo de confiança. `ganho_acuracia_pp` é a diferença descritiva para o baseline em pontos percentuais.

As médias de acurácia e F1 ponderado e os DP de acurácia foram reconstruídos e comparados aos arquivos certificados com tolerância absoluta de 1e-12. O DP de F1 e F1 macro são acréscimos deste suplemento.
''')
    table('resumo-fidelidade-fonte')
    pic('acuracia-f1-fontes')
    md('''## Baseline e limites da interpretação

O baseline sempre prediz a classe majoritária **do treino de cada fold e grupo**, sem acessar os rótulos de teste. Empates são resolvidos pelo menor código de classe. **Todos os modelos ficam abaixo desse baseline em acurácia:** o baseline obtém 39,36% na referência masculina e 36,50% na feminina. As diferenças dos modelos ficam entre −3,44 e −1,47 pontos percentuais. Em contrapartida, todos superam o F1 ponderado do baseline (0,2223 e 0,1955, respectivamente). A diferença entre as conclusões decorre de as métricas avaliarem aspectos distintos da distribuição dos erros. São comparações descritivas; não há teste de superioridade neste suplemento.

Uma acurácia próxima de 1/3, isoladamente, não permite concluir desempenho equivalente ao acaso: a distribuição de classes e a regra do baseline precisam ser consideradas. Tampouco a redução de κ prova que os modelos aprenderam diferenças substantivas de perspectiva; erros, instabilidade e distribuições marginais também podem afetar a concordância. As métricas de aderência complementam Δκ e recomendam cautela na interpretação substantiva.
''')
    pic('baseline-acuracia')
    md('''## Diagnóstico por classe e por fold

Mapeamento confirmado no código: −1 = negativa; 0 = neutra; 1 = positiva. As métricas por classe abaixo usam as 1.222 predições out-of-fold reunidas por modelo. São um estimador diferente da média de métricas por fold, sobretudo para F1. Não substituir uma agregação pela outra nos slides sem identificar a mudança.
''')
    table('metricas-por-classe')
    table('metricas-por-fold')
    table('metricas-oof-reunidas')
    md('''## Referência cruzada — análise exploratória

Modelo treinado no grupo masculino avaliado contra a referência feminina e vice-versa, sobre os mesmos itens out-of-fold. Esta tabela mede aderência à outra fonte, não corrige o resultado oficial e não transforma nenhum grupo em árbitro. Valores agregados nas predições reunidas; não são médias dos folds.
''')
    table('referencia-cruzada-exploratoria')
    md('''## Fase sintética: o que é e o que não é recuperável

Existem referências sintéticas geradas (`rotulo_masculino` e `rotulo_feminino`), portanto seria possível calcular acurácia/F1 **contra essas referências** durante a avaliação. Entretanto, a função `treinar_e_comparar` da Fase 3 usa as predições transitoriamente e não exporta acurácia/F1 nem predições individuais. Os CSV consolidados de κ, χ² e V de Cramér não determinam essas métricas. **Não disponível não significa zero.**

Este suplemento não inventa valores sintéticos nem refaz os treinamentos. Para obtê-los, seria necessário executar avaliação adicional isolada, preservando parâmetros e verificando κ contra os resultados certificados. Os textos sintéticos são tokens aleatórios gerados sem vínculo semântico com os rótulos: acurácia/F1 nesse experimento seriam um diagnóstico do controle sintético, não evidência de competência em sentimento.

## Conteúdo sugerido para os slides de reserva

**Slide 1 — O que conta como referência?** “A MADA não pressupõe um ground truth único. Acurácia e F1 são reportados relativamente aos consensos majoritários de cada grupo; Δκ mede a mudança de concordância entre fontes e modelos.”

**Slide 2 — Aderência às fontes.** Usar a tabela principal e `acuracia-f1-fontes.png`; identificar média de cinco folds, F1 ponderado e DP. Não chamar a concordância entre predições de acurácia.

**Slide 3 — Contexto e limites.** Usar `baseline-acuracia.png`. “Todos os modelos ficam abaixo da classe majoritária em acurácia, mas acima dela em F1 ponderado. Os valores modestos limitam a interpretação da amplificação como reprodução de perspectivas aprendidas.”

**Slide 4 — Controle sintético.** “Há rótulos sintéticos de referência; acurácia/F1 não foram exportados no experimento certificado e não são recuperáveis de κ. O controle não representa compreensão semântica.”

## Rastreabilidade e definições

Entradas: `predicoes-completas.csv`, `metricas-modelos-pareados.csv` e corpus `mqd-1222-majoritarias.csv`. Verificadas cobertura, unicidade, pareamento dos folds, alinhamento de rótulos/textos e reprodução dos valores certificados. Hashes SHA-256 e versões estão em `dados/06-suplemento-qualificacao/verificacao.json`.

Definições: [acurácia — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html) e [F1 — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html). Ambos exigem `y_true`; a interpretação da referência depende do desenho do estudo.
''')
    doc=dict(nbformat=4,nbformat_minor=5,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':sys.version.split()[0]}},cells=cells)
    for i,c in enumerate(cells):
        c['id']=f'suplemento-{i:02d}'
    (ROOT/'suplemento-metricas-qualificacao.ipynb').write_text(json.dumps(doc,ensure_ascii=False,indent=1),encoding='utf8')


if __name__ == '__main__':
    tabelas = analisar()
    notebook(tabelas)
    print(tabelas['resumo-fidelidade-fonte'].to_string(index=False))
    print('Suplemento gerado; resultados certificados preservados.')
