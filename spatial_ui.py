import base64
import io
import json
from pathlib import Path
import numpy as np
import plotly.express as px
import streamlit as st
from backend import MODELOS, ESTOCASTICOS
from apresentacao import APRESENTACAO, ORIENTACOES
from spatial_backend import simular_espacial, REGRAS, CORES, SELECAO, MUTACAO

def html_animacao(estados,df):
    """Animação offline em canvas; dados inteiros compactos e sem CDN."""
    dados=base64.b64encode(estados.tobytes()).decode('ascii')
    resumo=json.loads(df.to_json(orient='records'))
    template='''<!DOCTYPE html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>EvoLab população espacial</title>
<style>body{font:15px system-ui,sans-serif;color:#254359;margin:12px;background:#fff}button{padding:8px 12px;border:1px solid #b6c7d0;border-radius:6px;background:#f3f7fa;cursor:pointer}button:focus,input:focus{outline:3px solid #1b807a}.controls{display:flex;gap:9px;align-items:center;flex-wrap:wrap}canvas{display:block;border:1px solid #9eb4c5;max-width:100%;margin:12px auto;image-rendering:pixelated}#g{width:min(100%,550px)}.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:13px}.box{display:inline-block;width:13px;height:13px;border:1px solid #9eacb8;vertical-align:middle}#stats{margin:10px 0}input[type=range]{flex:1;min-width:120px}#tip{min-height:22px;font-size:13px}</style>
<h3>Distribuição espacial dos genótipos</h3><div class="legend"><span><i class="box" style="background:#2166AC"></i> AA · homozigoto dominante*</span><span><i class="box" style="background:#7B3294"></i> Aa · heterozigoto</span><span><i class="box" style="background:#D95F02"></i> aa · homozigoto recessivo*</span><span><i class="box" style="background:white"></i> Sem indivíduo</span></div>
<canvas id="c" aria-label="Grade espacial de genótipos"></canvas><div id="tip">Passe o cursor sobre a grade para consultar posição e genótipo.</div>
<div class="controls"><button id="prev" aria-label="Geração anterior">◀</button><button id="play">Reproduzir</button><button id="next" aria-label="Próxima geração">▶</button><label for="g">Geração</label><input id="g" type="range" min="0" max="__LAST__" value="0"><output id="time"></output></div>
<div id="stats"></div><label for="speed">Intervalo entre gerações</label> <select id="speed"><option value="80">80 ms</option><option value="200" selected>200 ms</option><option value="500">500 ms</option><option value="1000">1 segundo</option></select>
<p style="font-size:12px">* Dominante e recessivo são rótulos didáticos para AA e aa. A dominância da aptidão é definida por h; as cores não representam fenótipos. Em todos os cenários espaciais há amostragem finita.</p>
<script>const size=__SIZE__,last=__LAST__,raw=Uint8Array.from(atob('__DATA__'),c=>c.charCodeAt(0)),stats=__STATS__;
const colors=[[255,255,255],[33,102,172],[123,50,148],[217,95,2]],names=['Sem indivíduo','AA','Aa','aa'];
const c=document.getElementById('c'),ctx=c.getContext('2d'),slider=document.getElementById('g'),play=document.getElementById('play');let timer=null;const cell=Math.max(6,Math.floor(500/size));c.width=c.height=size*cell;
function stop(){if(timer)clearInterval(timer);timer=null;play.textContent='Reproduzir'}
function draw(){let g=+slider.value;for(let y=0;y<size;y++)for(let x=0;x<size;x++){let v=raw[g*size*size+y*size+x];ctx.fillStyle='rgb('+colors[v].join(',')+')';ctx.fillRect(x*cell,y*cell,cell,cell);ctx.strokeStyle='#d4dde5';ctx.lineWidth=.4;ctx.strokeRect(x*cell,y*cell,cell,cell)}document.getElementById('time').textContent=g+' / '+last;let d=stats[g];const f=v=>v===null?'indefinida':v.toFixed(4);document.getElementById('stats').textContent='Geração '+g+' · N = '+d.N+' · Vazias = '+d.vazias+' · AA = '+d.n_AA+' · Aa = '+d.n_Aa+' · aa = '+d.n_aa+' · p = '+f(d.p_A)+' · q = '+f(d.q_a)}
slider.oninput=()=>{stop();draw()};document.getElementById('prev').onclick=()=>{stop();slider.value=Math.max(0,+slider.value-1);draw()};document.getElementById('next').onclick=()=>{stop();slider.value=Math.min(last,+slider.value+1);draw()};play.onclick=()=>{if(timer){stop();return}if(+slider.value===last)slider.value=0;draw();play.textContent='Pausar';timer=setInterval(()=>{slider.value=+slider.value+1;draw();if(+slider.value>=last)stop()},+document.getElementById('speed').value)};
document.getElementById('speed').onchange=()=>stop();c.onmousemove=e=>{let r=c.getBoundingClientRect(),x=Math.min(size-1,Math.floor((e.clientX-r.left)/r.width*size)),y=Math.min(size-1,Math.floor((e.clientY-r.top)/r.height*size));document.getElementById('tip').textContent='Linha '+(y+1)+' · Coluna '+(x+1)+' · '+names[raw[(+slider.value)*size*size+y*size+x]]};draw();</script></html>'''
    return template.replace('__SIZE__',str(estados.shape[1])).replace('__LAST__',str(len(estados)-1)).replace('__DATA__',dados).replace('__STATS__',json.dumps(resumo,ensure_ascii=False,allow_nan=False))

def render_espacial():
    with st.sidebar:
        modelo=st.selectbox('Processo evolutivo espacial',MODELOS,key='esp_modelo')
        st.caption('UFBA · IMS · Campus de Vitória da Conquista · Ciências Biológicas')
        st.markdown('**Condições iniciais**')
        def complementar(origem,destino):st.session_state[destino]=round(1-st.session_state[origem],6)
        if 'esp_p' not in st.session_state:st.session_state.esp_p=.5;st.session_state.esp_q=.5
        a,b=st.columns(2)
        p=a.number_input('Alelo A · p',0.,1.,step=.01,key='esp_p',on_change=complementar,args=('esp_p','esp_q'),format='%.4f')
        b.number_input('Alelo a · q',0.,1.,step=.01,key='esp_q',on_change=complementar,args=('esp_q','esp_p'),format='%.4f')
        cfg=dict(modelo=modelo,p0=p)
        cfg['geracoes']=st.number_input('Gerações espaciais',1,500,100,key='esp_g')
        cfg['lado']=st.number_input('Lado da grade',8,60,20,key='esp_lado',help='Uma grade 20 × 20 tem 400 posições.')
        cfg['ocupacao']=st.number_input('Fração inicialmente ocupada',0.,1.,.8,.05,key='esp_ocup')
        cfg['padrao']=st.selectbox('Distribuição inicial',['Misturado','Agrupado'],key='esp_padrao')
        cfg['seed']=st.number_input('Semente espacial',0,2147483647,42,key='esp_seed')
        st.markdown('**Reprodução e espaço**')
        cfg['vizinhanca']=st.selectbox('Vizinhança',['Moore','Von Neumann'],key='esp_viz')
        cfg['raio']=st.number_input('Raio da vizinhança',1,3,1,key='esp_raio')
        cfg['borda']=st.selectbox('Bordas',['Periódica','Fechada'],key='esp_borda')
        cfg['colonizar']=st.checkbox('Permitir colonização das posições inicialmente vazias',key='esp_col')
        if modelo in SELECAO:
            cfg['favorecido']=st.selectbox('Alelo favorecido',['A','a'],key='esp_fav')
            cfg['s']=st.number_input('Força de seleção · s',0.,1.,.1,.01,key='esp_s')
            cfg['h']=st.number_input('Dominância da desvantagem · h',0.,1.,.5,.05,key='esp_h')
        if modelo in ESTOCASTICOS:
            cfg['reprodutores']=st.number_input('Máximo de reprodutores locais · B',2,49,4,key='esp_B',help='Gargalo adicional por posição; o máximo efetivo é o número de indivíduos na vizinhança. Não é Ne.')
        if modelo=='Endogamia':cfg['autofecundacao']=st.number_input('Fração de autofecundação · σ',0.,1.,.2,.01,key='esp_sigma')
        if modelo=='Migração':
            cfg['migracao']=st.number_input('Probabilidade de imigração por posição · m',0.,1.,.05,.01,key='esp_m')
            cfg['p_fonte']=st.number_input('Frequência de A na fonte',0.,1.,.8,.01,key='esp_fonte')
        if modelo in MUTACAO:
            cfg['mu']=st.number_input('μ · A → a',0.,1.,.001,.0001,format='%.6f',key='esp_mu')
            cfg['nu']=st.number_input('ν · a → A',0.,1.,.0001,.0001,format='%.6f',key='esp_nu')
        rodar=st.button('Executar simulação espacial',type='primary',key='esp_run',width='stretch')
    st.markdown(APRESENTACAO)
    st.subheader('Autômato celular espacial · '+modelo)
    st.write(ORIENTACOES[modelo]['resumo'])
    dicas={
        'Seleção natural':'Ajuste s e h e observe a contribuição reprodutiva dos genótipos na vizinhança; a aptidão é um peso de escolha dos pais. A amostragem local também produz deriva.',
        'Deriva genética':'Compare sementes, raios e o limite B de reprodutores locais. B menor acrescenta um gargalo; aglomerados e perda de alelos também dependem da estrutura espacial.',
        'Endogamia':'Ajuste σ para definir a probabilidade de autofecundação por tentativa. Observe Aa e os homozigotos; frequências alélicas também podem mudar por deriva na grade.',
        'Migração':'Ajuste m e p da fonte. Após a reprodução, cada posição permitida pode receber um imigrante, substituindo um descendente ou preenchendo uma vaga.',
        'Mutação':'Ajuste μ e ν para as conversões nos gametas. Acompanhe o surgimento de genótipos e a contagem de mutações; sem pais suficientes, a mutação não gera novos indivíduos.',
        'Seleção natural + deriva genética':'Combine s e h com o limite B. A seleção pondera a contribuição dos pais e B impõe um gargalo local adicional à amostragem que já existe na grade.',
        'Seleção natural + mutação':'A seleção pondera a escolha dos pais; em seguida, μ e ν modificam os gametas. Observe a persistência ou reintrodução de alelos desfavorecidos junto aos efeitos de deriva local.'
    }
    st.write(dicas[modelo])
    st.info('Extensão espacial: todos os cenários incluem amostragem finita, reprodução local e deriva. As regras abaixo substituem as hipóteses de população infinita do modo de frequências. Nos cenários de deriva, B permite impor um gargalo adicional de reprodutores locais.')
    st.markdown('**Como usar:** escolha o cenário, a grade, a ocupação inicial e a vizinhança na barra lateral. Clique em Executar simulação espacial. Na animação, use Reproduzir, Pausar, as setas ou o seletor de geração para inspecionar a população. Passe o cursor nas células para identificar genótipos. A grade mostra a população de uma realização; os gráficos abaixo mostram o histórico completo.')
    with st.expander('Regras espaciais e interpretação',expanded=False):st.markdown(REGRAS)
    if rodar or 'esp_resultado' not in st.session_state:
        with st.spinner('Calculando reprodução local e genótipos...'):
            try:estados,df=simular_espacial(**cfg)
            except ValueError as e:st.error(str(e));return
        st.session_state.esp_resultado=(estados,df,dict(cfg))
    estados,df,usado=st.session_state.esp_resultado
    if cfg!=usado:st.warning('Os parâmetros ou o cenário foram alterados. Execute novamente para atualizar a grade e os gráficos. Resultados exibidos: '+usado['modelo'])
    st.caption(f"Condição inicial executada: {estados.shape[1]} × {estados.shape[2]}, N = {df.N.iloc[0]}, p solicitado = {usado['p0']:.4f}, p realizado = {df.p_A.iloc[0]:.4f}. As cópias iniciais são arredondadas para 2N; os pares são distribuídos aleatoriamente.")
    html=html_animacao(estados,df)
    if hasattr(st,'iframe'):
        st.iframe(html,height=850,alt='Autômato celular do EvoLab com genótipos e controles de animação')
    else:
        import streamlit.components.v1 as components
        components.html(html,height=850,scrolling=True)
    st.markdown('**Resumo da última geração**')
    a,b,c,d=st.columns(4);last=df.iloc[-1]
    a.metric('Indivíduos · N',int(last.N));b.metric('Posições vazias',int(last.vazias));c.metric('Frequência final de A',f'{last.p_A:.4f}' if last.N else 'Indefinida');d.metric('Heterozigotos · contagem',int(last.n_Aa))
    t1,t2,t3=st.tabs(['Frequências e diversidade','Dados e exportação','Comparação entre representações'])
    with t1:
        for cols,titulo in [(['p_A','q_a'],'Frequências alélicas'),(['AA','Aa','aa'],'Proporções genotípicas observadas'),(['H_observada','H_esperada'],'Heterozigose observada e diversidade 2pq')]:
            fig=px.line(df,x='geracao',y=cols,title=titulo,labels={'geracao':'Geração','value':'Frequência','variable':'Medida'},template='plotly_white')
            fig.update_yaxes(range=[0,1]);st.plotly_chart(fig,width='stretch')
        st.plotly_chart(px.line(df,x='geracao',y=['N','vazias'],labels={'geracao':'Geração','value':'Posições','variable':'Medida'},template='plotly_white'),width='stretch')
        st.caption('p = (2 × nAA + nAa)/(2N). Proporções genotípicas usam somente indivíduos presentes. 2pq usa a frequência global da grade: diferenças para Aa podem refletir estrutura espacial, endogamia e amostragem; não são, sozinhas, prova de seleção. Posições brancas não são um quarto genótipo.')
    with t2:
        st.dataframe(df,hide_index=True,width='stretch')
        st.download_button('Baixar histórico espacial · CSV',df.to_csv(index=False).encode('utf-8-sig'),'evolab_espacial.csv','text/csv')
        st.download_button('Baixar parâmetros espaciais · JSON',json.dumps(usado,ensure_ascii=False,indent=2),'evolab_espacial_parametros.json','application/json')
        st.download_button('Baixar animação interativa · HTML',html,'evolab_espacial.html','text/html')
        buf=io.BytesIO();np.savez_compressed(buf,estados=estados,codigos=np.array(['Vazia','AA','Aa','aa']),parametros=json.dumps(usado,ensure_ascii=False))
        st.download_button('Baixar todas as grades · NPZ',buf.getvalue(),'evolab_grades.npz','application/octet-stream')
    with t3:
        st.write('O modo Frequências populacionais preserva os sete modelos originais. O modo espacial simula indivíduos e inclui estrutura de vizinhança, amostragem mendeliana e possíveis falhas de reprodução. Não há correspondência automática entre N da grade e Ne do modelo Wright–Fisher. A referência determinística não é sobreposta à grade porque as regras e a estrutura de acasalamento diferem.')
        st.write('O mesmo modelo e os mesmos parâmetros, inclusive semente e padrão inicial, reproduzem os resultados na mesma implementação. Misturado e Agrupado preservam as contagens iniciais de cada genótipo; muda sua distribuição no espaço. Em Agrupado, os tipos são ordenados ao longo das linhas entre as posições ocupadas.')
    st.divider();st.caption('EvoLab · Grupo Genética e Bioinformática · IMS / UFBA | Prof. Leandro Martins de Freitas · Campus de Vitória da Conquista · Curso de Ciências Biológicas')
    manual=Path(__file__).with_name('Manual_EvoLab.docx')
    if manual.exists():st.download_button('Baixar manual de uso e interpretação · Word',manual.read_bytes(),'Manual_EvoLab.docx','application/vnd.openxmlformats-officedocument.wordprocessingml.document',key='esp_manual')
