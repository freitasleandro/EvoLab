"""Modelos diploides de um locus e dois alelos; geração 0 incluída."""
import numpy as np
import pandas as pd

MODELOS = ['Seleção natural', 'Deriva genética', 'Endogamia', 'Migração', 'Mutação', 'Seleção natural + deriva genética', 'Seleção natural + mutação']
ESTOCASTICOS = {'Deriva genética', 'Seleção natural + deriva genética'}

def simular(modelo, p0=.5, geracoes=100, s=.1, h=.5, favorecido='A', ne=100,
            replicas=10, seed=42, autofecundacao=.2, migracao=.05, p_fonte=.8,
            mu=.001, nu=.0001):
    if modelo not in MODELOS:
        raise ValueError('Modelo desconhecido.')
    for nome, v in dict(p0=p0,s=s,h=h,autofecundacao=autofecundacao,
                        migracao=migracao,p_fonte=p_fonte,mu=mu,nu=nu).items():
        if not np.isfinite(v) or not 0 <= v <= 1:
            raise ValueError(f'{nome} deve estar entre 0 e 1.')
    for nome,v,lim in [('geracoes',geracoes,2000),('ne',ne,100000),('replicas',replicas,100)]:
        if not isinstance(v,(int,np.integer)) or not 1<=v<=lim:
            raise ValueError(f'{nome} deve ser inteiro entre 1 e {lim}.')
    if favorecido not in ('A','a'):
        raise ValueError('Alelo favorecido inválido.')
    rng=np.random.default_rng(seed)
    linhas=[]
    for r in range(replicas if modelo in ESTOCASTICOS else 1):
        # Wright–Fisher inicia com um número inteiro de cópias.
        p=round(2*ne*p0)/(2*ne) if modelo in ESTOCASTICOS else p0
        f=0.
        extinta=False
        for g in range(geracoes+1):
            q=1-p
            aa=p*p+f*p*q; het=2*p*q*(1-f); bb=q*q+f*p*q
            linhas.append((r+1,g,p,q,aa,het,bb,f if not extinta else np.nan,2*p*q,'Extinta' if extinta else 'Ativa'))
            if g==geracoes: break
            if extinta: continue
            if modelo in ('Seleção natural','Seleção natural + deriva genética','Seleção natural + mutação'):
                w=np.array([1,1-h*s,1-s] if favorecido=='A' else [1-s,1-h*s,1])
                media=aa*w[0]+het*w[1]+bb*w[2]
                if media<=0:
                    if modelo in ESTOCASTICOS:
                        extinta=True
                        p=float('nan')
                        continue
                    raise ValueError('Aptidão média zero: todos os genótipos presentes têm aptidão nula. Reduza s ou altere as frequências.')
                p=float(np.clip((aa*w[0]+.5*het*w[1])/media,0,1))
                if modelo in ESTOCASTICOS: p=rng.binomial(2*ne,p)/(2*ne)
                elif modelo=='Seleção natural + mutação': p=p*(1-mu)+(1-p)*nu
            elif modelo=='Deriva genética': p=rng.binomial(2*ne,p)/(2*ne)
            elif modelo=='Endogamia': f=autofecundacao*(1+f)/2
            elif modelo=='Migração': p=(1-migracao)*p+migracao*p_fonte
            elif modelo=='Mutação': p=p*(1-mu)+(1-p)*nu
            p=float(np.clip(p,0,1))
    return pd.DataFrame(linhas,columns=['replica','geracao','p_A','q_a','AA','Aa','aa','F','H_esperada','status'])

TEXTOS={
'Seleção natural': ('Seleção de viabilidade', 'w do homozigoto favorecido = 1; w do heterozigoto = 1 − h·s; w do outro homozigoto = 1 − s. p′ = (p²wAA + pqwAa) / w̄.', 'População infinita, acasalamento aleatório, sem mutação, migração ou deriva. As frequências genotípicas exibidas são as dos zigotos antes da seleção, após o acasalamento aleatório. h = 0 protege o heterozigoto; h = 1 atribui a ele a mesma desvantagem do homozigoto desfavorecido.'),
'Deriva genética': ('Amostragem Wright–Fisher', 'K ~ Binomial(2Ne, p); p′ = K / (2Ne). E[Hₜ] = H₀(1 − 1/2Ne)ᵗ.', 'Ne é o tamanho efetivo diploide constante. Cada réplica é uma população independente. AA, Aa e aa são proporções esperadas sob acasalamento aleatório, não contagens de genótipos amostrados. A frequência inicial é arredondada à cópia alélica mais próxima. Fixação e perda são estados absorventes.'),
'Endogamia': ('Autofecundação parcial', 'Fₜ₊₁ = σ(1 + Fₜ)/2; AA = p² + Fpq; Aa = 2pq(1 − F); aa = q² + Fpq.', 'F₀ = 0. Uma fração σ da descendência resulta de autofecundação e o restante de acasalamento aleatório em população infinita. p e q permanecem constantes. Este é um modelo de endogamia por autofecundação, aplicável especialmente a organismos autofecundantes; não representa diretamente casamentos consanguíneos humanos.'),
'Migração': ('Modelo continente–ilha', 'p′ = (1 − m)p + m·p_fonte.', 'Uma fração m do pool gênico é substituída em cada geração por migrantes de uma fonte com frequência constante. População receptora infinita e acasalamento aleatório; não há deriva, seleção ou mutação.'),
'Mutação': ('Mutação bidirecional', 'p′ = p(1 − μ) + (1 − p)ν; p* = ν/(μ + ν), se μ + ν > 0.', 'μ é a probabilidade por geração de A → a; ν é a probabilidade de a → A. População infinita e acasalamento aleatório. Taxas altas podem gerar oscilações; são úteis didaticamente, mas em geral não são realistas para mutações pontuais.')}

TEXTOS['Seleção natural + deriva genética'] = (
    'Seleção de viabilidade e amostragem Wright–Fisher',
    'p_sel = (p²wAA + pqwAa) / w̄; K ~ Binomial(2Ne, p_sel); p′ = K / (2Ne).',
    'Em cada geração, a seleção determina as contribuições relativas ao pool gênico; depois, 2Ne cópias são amostradas para a geração seguinte. Ne é constante e os acasalamentos são aleatórios. Não há migração nem mutação. As proporções genotípicas exibidas são expectativas antes da seleção, não contagens amostradas. A curva tracejada representa seleção sem deriva, iniciada na mesma frequência efetiva das réplicas. Um alelo favorecido pode ser perdido ao acaso. Com s = 1, uma população sem genótipos viáveis não se reproduz: as gerações seguintes ficam sem frequências definidas e recebem status Extinta. Médias excluem essas populações; extinção não é sinônimo de perda do alelo A.'
)

TEXTOS['Seleção natural + mutação'] = (
    'Seleção de viabilidade e mutação bidirecional',
    'p_sel = (p²wAA + pqwAa) / w̄; p′ = p_sel(1 − μ) + (1 − p_sel)ν.',
    'População infinita e acasalamento aleatório, sem deriva ou migração. Em cada geração, a seleção atua primeiro; depois, os alelos do pool gênico sofrem mutação (μ: A → a; ν: a → A), antes da formação dos zigotos da próxima geração. As proporções AA, Aa e aa são as esperadas antes da seleção em cada geração. As aptidões são as do modelo de seleção isolada. A curva tracejada mostra seleção sem mutação. Com mutação recorrente, um alelo desfavorecido pode persistir ou ser reintroduzido. O equilíbrio depende de s, h e das duas taxas; a fórmula ν/(μ + ν) do modelo de mutação isolada não se aplica em geral. Se a aptidão média for zero, o ciclo não está definido: a mutação posterior não resgata a ausência de reprodução. Taxas altas são didáticas e podem produzir oscilações.'
)
