"""Autômato celular estocástico diploide com gerações não sobrepostas.
0 = vazio; 1 = AA; 2 = Aa; 3 = aa. Uma célula comporta um indivíduo.
"""
import numpy as np
import pandas as pd
from backend import MODELOS, ESTOCASTICOS

CORES = ['#FFFFFF', '#2166AC', '#7B3294', '#D95F02']
ROTULOS = ['Vazia', 'AA', 'Aa', 'aa']
SELECAO = {'Seleção natural', 'Seleção natural + deriva genética', 'Seleção natural + mutação'}
MUTACAO = {'Mutação', 'Seleção natural + mutação'}

def indices_vizinhos(lado, raio=1, vizinhanca='Moore', borda='Periódica'):
    yy,xx=np.indices((lado,lado)); offsets=[]
    for dy in range(-raio,raio+1):
        for dx in range(-raio,raio+1):
            if vizinhanca=='Moore' or abs(dy)+abs(dx)<=raio: offsets.append((dy,dx))
    cols=[]
    for dy,dx in offsets:
        y,x=yy+dy,xx+dx
        if borda=='Periódica': idx=(y%lado)*lado+x%lado
        else: idx=np.where((y>=0)&(y<lado)&(x>=0)&(x<lado),y*lado+x,-1)
        cols.append(idx.ravel())
    return np.stack(cols,axis=1)

def _resumo(grade,g,imigrantes=0,mutacoes=0):
    counts=np.bincount(grade.ravel(),minlength=4);n=int(counts[1:].sum())
    p=(2*counts[1]+counts[2])/(2*n) if n else np.nan
    freqs=counts[1:]/n if n else [np.nan]*3
    return dict(geracao=g,N=n,vazias=int(counts[0]),n_AA=int(counts[1]),n_Aa=int(counts[2]),n_aa=int(counts[3]),
                p_A=p,q_a=1-p,AA=freqs[0],Aa=freqs[1],aa=freqs[2],
                H_observada=freqs[1],H_esperada=2*p*(1-p),imigrantes=imigrantes,mutacoes=mutacoes)

def simular_espacial(modelo,p0=.5,geracoes=100,lado=20,ocupacao=.8,raio=1,
                     vizinhanca='Moore',borda='Periódica',colonizar=False,padrao='Misturado',seed=42,
                     s=.1,h=.5,favorecido='A',autofecundacao=.2,migracao=.05,p_fonte=.8,
                     mu=.001,nu=.0001,reprodutores=4,grade_inicial=None):
    if modelo not in MODELOS:raise ValueError('Modelo desconhecido.')
    for nome,v in dict(p0=p0,ocupacao=ocupacao,s=s,h=h,autofecundacao=autofecundacao,migracao=migracao,p_fonte=p_fonte,mu=mu,nu=nu).items():
        if not np.isfinite(v) or not 0<=v<=1:raise ValueError(f'{nome} deve estar entre 0 e 1.')
    for nome,v,lo,hi in [('lado',lado,8,60),('geracoes',geracoes,1,500),('raio',raio,1,3),('reprodutores',reprodutores,2,49)]:
        if not isinstance(v,(int,np.integer)) or not lo<=v<=hi:raise ValueError(f'{nome}: inteiro de {lo} a {hi}.')
    if vizinhanca not in ['Moore','Von Neumann'] or borda not in ['Periódica','Fechada'] or padrao not in ['Misturado','Agrupado'] or favorecido not in ['A','a']:
        raise ValueError('Configuração espacial inválida.')
    rng=np.random.default_rng(seed);area=lado*lado
    if grade_inicial is None:
        n=round(area*ocupacao);grade=np.zeros(area,dtype=np.uint8)
        pos=np.sort(rng.choice(area,n,replace=False))
        # Frequência alélica inicial exata até o arredondamento de uma cópia.
        alelos=np.zeros(2*n,dtype=np.uint8);alelos[:round(2*n*p0)]=1;rng.shuffle(alelos)
        tipos=(3-alelos.reshape(-1,2).sum(axis=1)).astype(np.uint8)
        if padrao=='Agrupado':tipos.sort()
        grade[pos]=tipos;grade=grade.reshape(lado,lado)
    else:
        raw=np.asarray(grade_inicial)
        if raw.shape!=(lado,lado) or not np.isin(raw,[0,1,2,3]).all():raise ValueError('Grade inicial inválida.')
        grade=raw.astype(np.uint8).copy()
    alvo=np.ones(area,dtype=bool) if colonizar else (grade.ravel()>0).copy()
    indices=indices_vizinhos(lado,raio,vizinhanca,borda)
    invalidos=indices<0;seguros=np.maximum(indices,0);rows=np.arange(area)
    aptidoes=np.array([0.,1.,1.,1.])
    if modelo in SELECAO:
        aptidoes[1:]=[1,1-h*s,1-s] if favorecido=='A' else [1-s,1-h*s,1]
    estados=np.empty((geracoes+1,lado,lado),dtype=np.uint8);estados[0]=grade
    registros=[_resumo(grade,0)]
    for g in range(1,geracoes+1):
        viz=grade.ravel()[seguros].copy();viz[invalidos]=0
        pesos=aptidoes[viz]
        if modelo in ESTOCASTICOS and reprodutores<viz.shape[1]:
            # Gargalo: subconjunto uniforme de indivíduos locais antes de ponderar por aptidão.
            chaves=rng.random(viz.shape);chaves[viz==0]=np.inf
            keep=np.argsort(chaves,axis=1)[:,:reprodutores]
            mask=np.zeros_like(pesos,dtype=bool);mask[rows[:,None],keep]=True;pesos*=mask
        def escolher(w):
            total=w.sum(axis=1)
            j=np.argmax(np.cumsum(w,axis=1)>rng.random(area)[:,None]*total[:,None],axis=1)
            return j,total
        j1,total=escolher(pesos)
        pesos2=pesos.copy();pesos2[rows,j1]=0
        j2,total2=escolher(pesos2)
        selfing=(rng.random(area)<autofecundacao) if modelo=='Endogamia' else np.zeros(area,dtype=bool)
        j2=np.where(selfing,j1,j2)
        pode=alvo&(total>0)&(selfing|(total2>0))
        # Genótipo dá a probabilidade de transmitir A: AA=1, Aa=1/2, aa=0.
        p1=(3-viz[rows,j1].astype(float))/2;p2=(3-viz[rows,j2].astype(float))/2
        gametas=np.stack([rng.random(area)<p1,rng.random(area)<p2],axis=1)
        nmut=0
        if modelo in MUTACAO:
            flip=rng.random((area,2))<np.where(gametas,mu,nu)
            nmut=int((flip&pode[:,None]).sum());gametas^=flip
        nova=np.zeros(area,dtype=np.uint8);nova[pode]=(3-gametas[pode].sum(axis=1)).astype(np.uint8)
        nim=0
        if modelo=='Migração':
            im=alvo&(rng.random(area)<migracao);nim=int(im.sum())
            nova[im]=(3-rng.binomial(2,p_fonte,size=nim)).astype(np.uint8)
        grade=nova.reshape(lado,lado);estados[g]=grade
        registros.append(_resumo(grade,g,nim,nmut))
    return estados,pd.DataFrame(registros)

REGRAS = '''Uma célula comporta um indivíduo diploide: AA, Aa ou aa; branco indica ausência de indivíduo. A atualização é síncrona, com gerações não sobrepostas. A vizinhança inclui a própria célula e define de onde vêm os pais, não um movimento físico de adultos.

A cada geração, duas fontes parentais distintas são sorteadas na vizinhança, com contribuição mendeliana de um alelo de cada uma. Nos cenários de seleção, a aptidão relativa é o peso para escolher os pais (seleção na contribuição reprodutiva). Pais com aptidão zero não contribuem. Fora da autofecundação deliberada, são necessários dois pais viáveis. Se não houver pais suficientes, a posição fica vazia. As cores representam genótipos reais amostrados, e não frequências esperadas de Hardy–Weinberg.

Em Endogamia, uma fração σ das tentativas usa o mesmo pai para os dois gametas; o restante exige dois pais distintos. Portanto, o resultado espacial não segue necessariamente a recorrência de F do modelo de população infinita. Em Mutação, cada gameta sofre conversão A → a com probabilidade μ ou a → A com probabilidade ν. Em Seleção + mutação, essa conversão ocorre após a escolha dos pais por aptidão.

Em Migração, depois da reprodução local, cada posição permitida é substituída por um imigrante com probabilidade m, inclusive se estiver vazia. O genótipo imigrante é sorteado sob Hardy–Weinberg com p da fonte. A fonte permanece constante; m é uma probabilidade por posição, não uma fração exata de migrantes realizados. Migração pode recolonizar uma grade extinta quando há posições permitidas.

Todos os cenários espaciais têm população finita e amostragem, com deriva e efeitos de estrutura espacial. Seleção espacial e Seleção + deriva não são versões isoladas comparáveis à seleção determinística. Os cenários Deriva e Seleção + deriva acrescentam um gargalo: no máximo B reprodutores locais são sorteados uniformemente por posição antes da escolha por aptidão. Se B cobrir toda a vizinhança, o gargalo não é aplicado; os dois cenários de seleção passam a ter as mesmas regras.

Com colonização desativada, somente as posições ocupadas na geração 0 podem receber descendentes ou imigrantes; vagas produzidas depois podem ser reocupadas. Com colonização ativada, toda a grade pode receber indivíduos. Em ambos os casos, N é observado, não imposto. N não é uma estimativa de Ne. Borda periódica conecta lados opostos; borda fechada limita os vizinhos. A ordem é reprodução com seleção quando ativa, mutação nos gametas quando ativa e imigração quando ativa.'''
