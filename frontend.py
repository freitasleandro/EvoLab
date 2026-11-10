import json
import math
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from backend import simular, MODELOS, TEXTOS, ESTOCASTICOS
from apresentacao import APRESENTACAO, ORIENTACOES

st.set_page_config(page_title='EvoLab · Genética de populações',page_icon='🧬',layout='wide')
st.markdown('''<style>
.stApp {background:#f5f7fb} [data-testid="stSidebar"]{background:#fff;border-right:1px solid #e1e7ef}
h1,h2,h3{color:#17334b} .eyebrow{color:#13877d;font-weight:700;letter-spacing:2px;font-size:12px}
[data-testid="stMetric"]{background:white;border:1px solid #e1e7ef;padding:16px;border-radius:12px}
.stButton>button[kind="primary"]{background:#087e78;border:0}
</style>''',unsafe_allow_html=True)
if st.sidebar.radio('Representação', ['Frequências populacionais', 'Autômato celular espacial'], key='representacao') == 'Autômato celular espacial':
    from spatial_ui import render_espacial
    render_espacial()
    st.stop()

if 'historico' not in st.session_state: st.session_state.historico={}
with st.sidebar:
    st.markdown('### 🧬 EvoLab')
    st.caption('UFBA · Campus de Vitória da Conquista')
    st.caption('Curso de Ciências Biológicas · IMS')
    modelo=st.selectbox('Processo evolutivo',MODELOS)
    st.caption(ORIENTACOES[modelo]['resumo'])
    st.divider()
    st.markdown('**Condições iniciais**')
    def complementar(origem,destino): st.session_state[destino]=round(1-st.session_state[origem],6)
    if 'p' not in st.session_state: st.session_state.p=.5;st.session_state.q=.5
    c1,c2=st.columns(2)
    p=c1.number_input('Alelo A · p',0.,1.,step=.01,key='p',on_change=complementar,args=('p','q'),format='%.4f')
    c2.number_input('Alelo a · q',0.,1.,step=.01,key='q',on_change=complementar,args=('q','p'),format='%.4f')
    gens=st.number_input('Número de gerações',1,2000,100,step=10)
    cfg=dict(modelo=modelo,p0=p,geracoes=gens)
    st.divider()
    if modelo in ('Seleção natural','Seleção natural + deriva genética','Seleção natural + mutação'):
        cfg['favorecido']=st.selectbox('Alelo favorecido',['A','a'])
        cfg['s']=st.number_input('Força de seleção · s',0.,1.,.1,.01,help='Desvantagem do homozigoto desfavorecido.')
        cfg['h']=st.number_input('Dominância da desvantagem · h',0.,1.,.5,.05)
    if modelo in ESTOCASTICOS:
        cfg['ne']=st.number_input('Tamanho efetivo diploide · Ne',1,100000,100)
        cfg['replicas']=st.number_input('Populações independentes',1,100,20)
        cfg['seed']=st.number_input('Semente aleatória',0,2147483647,42)
    elif modelo=='Endogamia': cfg['autofecundacao']=st.number_input('Fração de autofecundação · σ',0.,1.,.2,.01)
    elif modelo=='Migração':
        cfg['migracao']=st.number_input('Taxa de migração · m',0.,1.,.05,.01)
        cfg['p_fonte']=st.number_input('Frequência de A na fonte',0.,1.,.8,.01)
    if modelo in ('Mutação','Seleção natural + mutação'):
        cfg['mu']=st.number_input('μ · A → a',0.,1.,.001,.0001,format='%.6f')
        cfg['nu']=st.number_input('ν · a → A',0.,1.,.0001,.0001,format='%.6f')
    rodar=st.button('Executar simulação',type='primary',width='stretch')
    st.caption('Cinco processos isolados e dois modelos combinados. A geração 0 representa a condição inicial.')

st.markdown(APRESENTACAO)
st.divider()
st.subheader(modelo)
orientacao = ORIENTACOES[modelo]
st.write(orientacao['resumo'])
st.markdown('**Como configurar**')
st.write(orientacao['uso'])
st.markdown('**O que observar nos resultados**')
st.write(orientacao['leitura'])
st.caption('As equações e as hipóteses completas estão na aba Modelo e interpretação. O manual em Word está disponível ao final da página.')
if rodar or modelo not in st.session_state.historico:
    try:
        st.session_state.historico[modelo]=(simular(**cfg),dict(cfg))
    except ValueError as e:
        st.error(str(e));st.stop()
df,usado=st.session_state.historico[modelo]
if usado!=cfg: st.warning('Parâmetros alterados. Clique em Executar simulação para atualizar os resultados.')
final=df[df.geracao==usado['geracoes']]
inicio=df[df.geracao==0]
a,b,c,d=st.columns(4)
def formatar(v): return f'{v:.4f}' if math.isfinite(v) else 'Indefinida'
a.metric('A · frequência final média',formatar(final.p_A.mean()),f'{final.p_A.mean()-inicio.p_A.mean():+.4f}' if math.isfinite(final.p_A.mean()) else None)
b.metric('a · frequência final média',formatar(final.q_a.mean()))
c.metric('Heterozigotos · Aa',formatar(final.Aa.mean()))
d.metric('Gerações simuladas',str(usado['geracoes']))
cores={'A':'#078b83','a':'#df9950','AA':'#176385','Aa':'#078b83','aa':'#df9950'}
t1,t2,t3,t4=st.tabs(['Trajetórias','Genótipos e diversidade','Modelo e interpretação','Dados e exportação'])
def mostrar(fig):
    fig.update_layout(template='plotly_white',height=440,margin=dict(l=20,r=20,t=30,b=20),legend_title_text='',paper_bgcolor='rgba(0,0,0,0)',font=dict(color='#254359'))
    fig.update_yaxes(range=[0,1],title='Frequência');fig.update_xaxes(title='Geração')
    st.plotly_chart(fig,width='stretch')
with t1:
    if modelo in ESTOCASTICOS:
        fig=go.Figure()
        for r,sub in df.groupby('replica'): fig.add_trace(go.Scatter(x=sub.geracao,y=sub.p_A,name=f'População {r}',mode='lines',line=dict(width=1.2),opacity=.5))
        media=df.groupby('geracao').p_A.mean()
        fig.add_trace(go.Scatter(x=media.index,y=media,name='Média de A',line=dict(color='#153d51',width=3)))
        if modelo=='Seleção natural + deriva genética':
            try:
                referencia=simular('Seleção natural',p0=float(inicio.p_A.iloc[0]),geracoes=usado['geracoes'],s=usado['s'],h=usado['h'],favorecido=usado['favorecido'])
                fig.add_trace(go.Scatter(x=referencia.geracao,y=referencia.p_A,name='Seleção sem deriva',line=dict(color='#d27822',width=3,dash='dash')))
            except ValueError:
                st.warning('Referência determinística indefinida: aptidão média inicial zero.')
        trajetoria=fig
        mostrar(fig)
        st.info(f"Ao final: {(final.p_A==1).sum()} populações com A fixado; {(final.p_A==0).sum()} com A perdido; {((final.p_A>0)&(final.p_A<1)).sum()} polimórficas. As proporções são observadas nestas réplicas, não probabilidades exatas.")
        if modelo=='Seleção natural + deriva genética':
            st.caption(f"Populações extintas até o final: {(final.status=='Extinta').sum()}. Médias excluem frequências indefinidas; genótipos viáveis ausentes com s = 1 impedem reprodução.")
        st.caption(f"p inicial efetivo = {inicio.p_A.iloc[0]:.6f}; solicitado = {usado['p0']:.6f}. O gráfico acompanha A; em cada população q = 1 − p.")
    else:
        longo=df.melt('geracao',value_vars=['p_A','q_a'],var_name='Alelo',value_name='Frequência')
        longo['Alelo']=longo.Alelo.map({'p_A':'A','q_a':'a'})
        trajetoria=px.line(longo,x='geracao',y='Frequência',color='Alelo',color_discrete_map=cores)
        if modelo=='Seleção natural + mutação':
            referencia=simular('Seleção natural',p0=usado['p0'],geracoes=usado['geracoes'],s=usado['s'],h=usado['h'],favorecido=usado['favorecido'])
            trajetoria.add_trace(go.Scatter(x=referencia.geracao,y=referencia.p_A,name='A · seleção sem mutação',line=dict(color='#153d51',width=2.5,dash='dash')))
        mostrar(trajetoria)
with t2:
    medio=df.groupby('geracao')[['AA','Aa','aa','H_esperada','F']].mean().reset_index()
    longo=medio.melt('geracao',value_vars=['AA','Aa','aa'],var_name='Genótipo',value_name='Frequência')
    mostrar(px.line(longo,x='geracao',y='Frequência',color='Genótipo',color_discrete_map=cores))
    fig=go.Figure()
    for col,nome in [('Aa','Heterozigotos Aa'),('H_esperada','Diversidade esperada 2pq')]: fig.add_trace(go.Scatter(x=medio.geracao,y=medio[col],name=nome))
    if modelo=='Endogamia': fig.add_trace(go.Scatter(x=medio.geracao,y=medio.F,name='Coeficiente F'))
    if modelo=='Deriva genética':
        fig.add_trace(go.Scatter(x=medio.geracao,y=inicio.H_esperada.mean()*(1-1/(2*usado['ne']))**medio.geracao,name='E[H] teórica',line=dict(dash='dash')))
    mostrar(fig)
    if modelo in ESTOCASTICOS: st.caption('Curvas de genótipos e diversidade: médias entre populações. A diversidade média é calculada dentro de cada população, antes de tirar a média.')
with t3:
    titulo,formula,hipoteses=TEXTOS[modelo]
    st.markdown('#### Equação de atualização');st.code(formula,language=None)
    st.markdown('#### Hipóteses e leitura dos gráficos');st.write(hipoteses)
    if modelo=='Endogamia': st.info('A linha alélica fica horizontal: a autofecundação aumenta a homozigose e reduz Aa, mantendo p e q. Não equivale a seleção nem a deriva.')
    if modelo=='Mutação' and usado['mu']+usado['nu']>0: st.write(f"Equilíbrio formal de A: {usado['nu']/(usado['mu']+usado['nu']):.6f}. A aproximação ao equilíbrio depende das taxas e pode exigir muitas gerações; μ = ν = 1 produz alternância, salvo no equilíbrio.")
    st.caption('Base conceitual: Hartl & Clark, Principles of Population Genetics, 4ª ed.; Charlesworth & Charlesworth, Elements of Evolutionary Genetics, 2010. Modelos didáticos de um locus autossômico diploide com dois alelos.')
with t4:
    if modelo in ('Seleção natural + deriva genética','Seleção natural + mutação') and 'referencia' in locals():
        st.download_button('Baixar referência de seleção isolada · CSV',referencia.to_csv(index=False).encode('utf-8-sig'),'evolab_referencia_selecao.csv','text/csv')
    st.dataframe(df,width='stretch',hide_index=True)
    x,y,z=st.columns(3)
    x.download_button('Baixar resultados · CSV',df.to_csv(index=False).encode('utf-8-sig'),'evolab_resultados.csv','text/csv')
    y.download_button('Baixar parâmetros · JSON',json.dumps(usado,ensure_ascii=False,indent=2),'evolab_parametros.json','application/json')
    # Gráfico vetorial interativo e portátil: sem dependência de CDN.
    z.download_button('Baixar gráfico · HTML',trajetoria.to_html(include_plotlyjs=True),'evolab_grafico.html','text/html')
st.divider()
st.caption('EvoLab · Universidade Federal da Bahia · Campus de Vitória da Conquista · IMS · Curso de Ciências Biológicas | Prof. Leandro Martins de Freitas · Grupo Genética e Bioinformática')

manual=Path(__file__).with_name('Manual_EvoLab.docx')
if manual.exists():
    st.download_button('Baixar manual de uso e interpretação · Word',manual.read_bytes(),'Manual_EvoLab.docx','application/vnd.openxmlformats-officedocument.wordprocessingml.document')
