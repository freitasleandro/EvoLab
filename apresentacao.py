"""Apresentação institucional e orientações introdutórias dos modelos."""
APRESENTACAO = '''
# EvoLab — Simulador de Genética de Populações

**EvoLab · Grupo Genética e Bioinformática · IMS / UFBA | Prof. Leandro Martins de Freitas**

O EvoLab é um aplicativo educacional desenvolvido para apoiar o ensino e o estudo de genética de populações e evolução no Curso de Ciências Biológicas da Universidade Federal da Bahia (UFBA), Campus de Vitória da Conquista, Instituto Multidisciplinar em Saúde (IMS).

O aplicativo permite simular, em uma população diploide com dois alelos, os efeitos isolados da seleção natural, deriva genética, endogamia, migração e mutação, além das combinações de seleção natural com deriva genética e de seleção natural com mutação. A partir das frequências alélicas iniciais, do número de gerações e dos parâmetros de cada modelo, o sistema apresenta gráficos e tabelas das frequências alélicas, proporções genotípicas e diversidade genética.

**Desenvolvido por:** Prof. Leandro Martins de Freitas — `leandromartins<at>ufba.br` — Grupo Genética e Bioinformática — Instituto Multidisciplinar em Saúde — Universidade Federal da Bahia.

**Objetivo:** oferecer uma ferramenta interativa para compreender os mecanismos de mudança genética nas populações, comparar cenários evolutivos e interpretar resultados de simulações reprodutíveis com base em modelos de genética de populações.

**Representações disponíveis:** Frequências populacionais reúne os modelos matemáticos originais. Autômato celular espacial permite observar indivíduos AA, Aa e aa em uma grade, com posições vazias em branco, reprodução local e animação ao longo das gerações. A versão espacial é estocástica e tem regras próprias, apresentadas antes dos resultados.

**Como começar:** selecione um modelo na barra lateral, leia a orientação abaixo, ajuste as frequências iniciais e os parâmetros e clique em **Executar simulação**. Ao modificar a frequência de um alelo, a do outro é ajustada para que a soma seja 1. As frequências variam de 0 a 1; por exemplo, 0,5 corresponde a 50%. A geração 0 representa a condição inicial. As simulações são didáticas e devem ser interpretadas de acordo com as hipóteses de cada modelo.
'''

ORIENTACOES = {
    'Seleção natural': {
        'resumo': 'Estuda mudanças nas frequências alélicas causadas por diferenças de aptidão entre genótipos.',
        'uso': 'Defina as frequências iniciais e as gerações, escolha o alelo favorecido e ajuste a força de seleção s e a dominância da desvantagem h. s = 0 significa ausência de seleção. h = 0 preserva a aptidão do heterozigoto; h = 0,5 produz uma desvantagem intermediária; h = 1 atribui ao heterozigoto a mesma desvantagem do homozigoto desfavorecido.',
        'leitura': 'Observe a trajetória do alelo favorecido e as mudanças nas proporções AA, Aa e aa. O modelo é determinístico, com população infinita e acasalamento aleatório, sem deriva, migração ou mutação. Um alelo ausente não reaparece por seleção. As proporções genotípicas mostradas são as esperadas antes da seleção em cada geração.'
    },
    'Deriva genética': {
        'resumo': 'Simula mudanças aleatórias das frequências alélicas decorrentes da amostragem de cópias de alelos entre gerações em populações finitas.',
        'uso': 'Informe as frequências iniciais, o tamanho efetivo diploide Ne, as gerações, o número de populações independentes e a semente aleatória. Cada população representa uma réplica com as mesmas condições iniciais. Repita com diferentes valores de Ne; a mesma configuração e semente reproduzem os sorteios na mesma implementação.',
        'leitura': 'Compare a dispersão das trajetórias e a perda de diversidade. Populações menores tendem a apresentar flutuações maiores. p = 1 indica fixação de A; p = 0 indica perda de A e fixação de a. A média pode esconder populações fixadas em extremos diferentes. Não há seleção, mutação ou migração. Confira a frequência inicial efetiva, arredondada para um número inteiro de cópias entre 2Ne.'
    },
    'Endogamia': {
        'resumo': 'Representa a endogamia por autofecundação parcial e seu efeito sobre as proporções de homozigotos e heterozigotos.',
        'uso': 'Defina as frequências iniciais, o número de gerações e a fração de autofecundação σ. σ = 0 representa acasalamento aleatório; σ = 1 representa autofecundação em toda a descendência. A população começa com coeficiente de endogamia F = 0.',
        'leitura': 'Observe a redução de Aa e o aumento de AA, aa e F quando há autofecundação. As frequências alélicas p e q e a diversidade esperada 2pq permanecem constantes: a mudança ocorre na distribuição dos genótipos. O modelo não inclui deriva ou seleção e não representa diretamente casamentos consanguíneos humanos.'
    },
    'Migração': {
        'resumo': 'Simula o fluxo gênico de uma população fonte com frequência alélica constante para uma população receptora.',
        'uso': 'Defina a frequência inicial na população receptora, as gerações, a taxa migratória m e a frequência de A na fonte. m é a fração do pool gênico receptor substituída em cada geração; m = 0 desativa a migração e m = 1 substitui integralmente esse pool pela contribuição da fonte.',
        'leitura': 'Observe a aproximação da frequência local à da fonte. A frequência de A aumenta ou diminui conforme a diferença entre as duas populações; taxas maiores aceleram a mudança. A fonte permanece constante, a população receptora é infinita e há acasalamento aleatório, sem seleção, deriva ou mutação.'
    },
    'Mutação': {
        'resumo': 'Estuda a alteração das frequências alélicas por conversão bidirecional entre os alelos A e a.',
        'uso': 'Informe as frequências iniciais, as gerações e as probabilidades de mutação por geração: μ para A → a e ν para a → A. Com ambas iguais a zero, as frequências permanecem constantes. Taxas pequenas podem exigir muitas gerações para produzir uma alteração visível.',
        'leitura': 'Compare a trajetória com o equilíbrio formal p = ν/(μ + ν), quando a soma das taxas é positiva. Taxas altas podem produzir oscilações; μ = ν = 1 gera alternância, salvo no equilíbrio. Valores altos ajudam na demonstração didática, mas não devem ser tomados como taxas típicas de mutações pontuais. Não há seleção, deriva ou migração.'
    },
    'Seleção natural + deriva genética': {
        'resumo': 'Combina diferenças de aptidão entre genótipos com a amostragem aleatória de alelos em populações finitas.',
        'uso': 'Escolha o alelo favorecido, a força de seleção s e a dominância h, além das frequências iniciais, gerações, Ne, número de populações independentes e semente. A cada geração, o sistema aplica a seleção e depois sorteia as 2Ne cópias da geração seguinte. Compare populações pequenas e grandes mantendo os demais parâmetros.',
        'leitura': 'Compare cada população e a média com a curva tracejada de seleção sem deriva, iniciada na mesma frequência efetiva. Um alelo favorecido pode ser perdido ao acaso, especialmente quando começa com poucas cópias. Com s = 0, o modelo corresponde à deriva isolada. Com s = 1, a ausência de genótipos viáveis pode impedir a reprodução; as gerações seguintes são marcadas como Extinta e excluídas das médias. Não há migração ou mutação.'
    }
}

ORIENTACOES['Seleção natural + mutação'] = {
    'resumo': 'Simula a ação conjunta da seleção natural e da mutação bidirecional sobre as frequências alélicas, permitindo estudar a manutenção de alelos desfavorecidos por mutação recorrente.',
    'uso': 'Defina as frequências iniciais, as gerações, o alelo favorecido, a força de seleção s e a dominância da desvantagem h. Ajuste μ para A → a e ν para a → A. Em cada geração, a seleção atua primeiro; a mutação modifica os alelos do pool gênico antes da formação da geração seguinte. Não há sorteios nem parâmetro Ne: a população é infinita.',
    'leitura': 'Compare as frequências de A e a com a curva tracejada de A sob seleção sem mutação. A mutação pode reintroduzir um alelo ausente e manter o alelo desfavorecido em frequência diferente de zero. Com s = 0, o resultado corresponde à mutação isolada; com μ = ν = 0, corresponde à seleção isolada. O equilíbrio depende da seleção e das duas taxas, e não apenas de ν/(μ + ν). Taxas altas são úteis didaticamente, mas podem causar oscilações e não devem ser tratadas como taxas típicas de mutações pontuais.'
}
