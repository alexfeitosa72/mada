"""Preenche a reserva R10 com distribuições das predições out-of-fold."""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dados/06-suplemento-qualificacao'
SOURCE = ROOT / 'dados/03-resultados-empiricos/predicoes-completas.csv'
MODELOS = ['SVM', 'NB', 'RF', 'LR']
GRUPOS = ['masculino', 'feminino']
CLASSES = {-1: 'Negativa', 0: 'Neutra', 1: 'Positiva'}
CORES = {-1: '#C9564F', 0: '#9AA6B2', 1: '#397CA8'}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    dados = pd.read_csv(SOURCE)
    assert set(dados.modelo) == set(MODELOS)
    assert not dados.duplicated(['modelo', 'frase_id']).any()
    linhas = []
    for modelo in MODELOS:
        d = dados[dados.modelo == modelo]
        assert len(d) == 1222 and set(d.frase_id) == set(range(1222))
        assert set(d.fold) == {1, 2, 3, 4, 5}
        for grupo in GRUPOS:
            y = d[f'pred_{grupo}']
            assert not y.isna().any() and set(y) <= set(CLASSES)
            counts = y.value_counts().reindex(CLASSES, fill_value=0)
            assert counts.sum() == 1222
            for classe, sentimento in CLASSES.items():
                linhas.append(dict(modelo=modelo, grupo=grupo, classe=classe,
                                   sentimento=sentimento.lower(), n=int(counts[classe]),
                                   total=len(d), proporcao=counts[classe]/len(d)))
    tabela = pd.DataFrame(linhas)
    np.testing.assert_allclose(tabela.groupby(['modelo','grupo']).proporcao.sum(), 1)
    tabela.to_csv(OUT/'proporcoes-classes-predicoes.csv', index=False, encoding='utf-8-sig')

    plt.rcParams.update({'font.family':'sans-serif', 'font.size':12,
                         'svg.fonttype':'none'})
    fig = plt.figure(figsize=(15.8, 7), facecolor='white')
    fig.add_artist(Rectangle((0,.953),1,.047,transform=fig.transFigure,color='#707070',lw=0))
    fig.add_artist(Rectangle((0,.747),1,.206,transform=fig.transFigure,color='#17548A',lw=0))
    fig.text(.02,.977,'Reserva R10',va='center',color='white',fontsize=11)
    fig.text(.98,.977,'Fase empírica · MQD-1222',va='center',ha='right',color='white',fontsize=11,weight='bold')
    fig.text(.032,.852,'Proporções de cada classe nas predições, por classificador e\npor grupo',
             color='white',fontsize=26,weight='bold',va='center',linespacing=1.15)
    fig.text(.135,.695,'Predições out-of-fold reunidas · 1.222 frases por barra · cada barra soma 100%',
             color='#626D7D',fontsize=11)
    ax = fig.add_axes([.125,.215,.765,.455])
    centers = np.arange(4)*2.25
    pos = [center+offset for center in centers for offset in [-.4,.4]]
    bottoms = np.zeros(8)
    for classe, sentimento in CLASSES.items():
        valores = np.array([tabela.query('modelo == @modelo and grupo == @grupo and classe == @classe').proporcao.iloc[0]
                            for modelo in MODELOS for grupo in GRUPOS])
        bars = ax.bar(pos,valores,.62,bottom=bottoms,color=CORES[classe],
                      edgecolor='white',linewidth=1.5,zorder=3)
        for barra, valor, bottom in zip(bars,valores,bottoms):
            label = f'{100*valor:.1f}%'.replace('.',',')
            ax.text(barra.get_x()+barra.get_width()/2,bottom+valor/2,label,
                    ha='center',va='center',color='white',fontsize=8 if valor < .06 else 12,weight='bold')
        bottoms += valores
    ax.set(ylim=(0,1),xlim=(-1.1,centers[-1]+1.1),
           xticks=pos,xticklabels=['masc.','fem.']*4,yticks=np.linspace(0,1,5))
    ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
    ax.tick_params(axis='x',length=0,pad=8)
    ax.tick_params(axis='y',colors='#626D7D',labelsize=10)
    for tick,grupo in zip(ax.get_xticklabels(),GRUPOS*4):
        tick.set_color('#007C80' if grupo=='masculino' else '#A05B00')
        tick.set_weight('bold')
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_color('#34404B')
    ax.grid(axis='y',alpha=.18,zorder=0)
    ax.set_axisbelow(True)
    for center,modelo,marker,cor in zip(centers,MODELOS,['o','s','D','o'],['#34469B','#B34AA1','#DD4933','#77952B']):
        ax.scatter(center-.25,-.17,s=60,marker=marker,color=cor,clip_on=False,
                   facecolors='none' if modelo=='LR' else cor,linewidths=2,
                   transform=ax.get_xaxis_transform())
        ax.text(center-.13,-.17,modelo,transform=ax.get_xaxis_transform(),
                va='center',ha='left',fontsize=14,weight='bold',color='#26313B')
    fig.legend(handles=[Patch(facecolor=CORES[c],label=s) for c,s in CLASSES.items()],
               loc='lower center',bbox_to_anchor=(.5,.065),ncol=3,frameon=False,fontsize=11)
    fig.text(.125,.025,'Fonte: predicoes-completas.csv. Proporções das saídas dos modelos; não representam acurácia ou distribuição dos rótulos de referência.',
             fontsize=9,color='#626D7D')
    for formato in ['png','svg']:
        fig.savefig(OUT/f'proporcoes-classes-predicoes-r10.{formato}',dpi=200,facecolor='white')
    plt.close(fig)
    (OUT/'proporcoes-classes-predicoes-r10-origem.json').write_text(json.dumps({
        'fonte':str(SOURCE.relative_to(ROOT)),
        'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'agregacao':'Contagem nas 1222 predições out-of-fold reunidas por modelo e grupo; não é média de proporções por fold.',
        'classes':CLASSES,'validacoes':'IDs únicos; cobertura integral por modelo; cinco folds; soma 100% em cada barra.'
    },ensure_ascii=False,indent=2),encoding='utf8')
    print(tabela.to_string(index=False))


if __name__ == '__main__':
    main()
