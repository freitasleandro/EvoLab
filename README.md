# EvoLab 2.1 — Simulações evolutivas

Universidade Federal da Bahia · Campus de Vitória da Conquista · Instituto Multidisciplinar em Saúde · Curso de Ciências Biológicas.

Aplicativo didático em Python/Streamlit. Os arquivos originais do analisador de conservação não são necessários nem foram substituídos.

## Executar

Requer Python 3.10 ou superior. No terminal, dentro desta pasta:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell), em vez do comando acima:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run frontend.py
```

Abra o endereço local informado pelo Streamlit. A conexão com a internet é necessária para instalar as dependências; as simulações são calculadas localmente.

## Uso

Selecione um dos sete modelos na barra lateral. Altere p ou q; o outro campo se ajusta para completar 1. Configure as gerações e os parâmetros específicos; use as setas dos campos numéricos ou digite os valores. Clique em Executar simulação após alterações. As abas mostram trajetórias alélicas, proporções genotípicas, diversidade, hipóteses e dados. Os resultados de cada modelo permanecem na sessão ao trocar de modelo.

A deriva usa Wright–Fisher com 2Ne cópias e permite até 100 populações independentes, com semente reprodutível. Seleção + deriva combina seleção de viabilidade com Wright–Fisher, exibe a referência de seleção sem deriva e trata ausência total de genótipos viáveis como extinção. Os outros modelos usam populações infinitas determinísticas. A endogamia foi implementada como autofecundação parcial; não altera frequências alélicas. Cada aba explica o modelo e o momento do ciclo de vida representado. A combinação de forças está restrita à sexta e à sétima opções.

Downloads: tabela CSV com todas as réplicas e gerações; JSON com os parâmetros executados; gráfico de trajetórias em HTML autossuficiente. A geração 0 está incluída. Na deriva, as frequências genotípicas são expectativas de acasalamento aleatório, não genótipos amostrados.

## Verificação

```bash
python -m unittest test_modelos.py -v
```

Os testes verificam normalização, ausência de efeito com taxas nulas, recorrências analíticas, endogamia, reprodutibilidade, discretização e estados absorventes da deriva, e seleção com aptidão média nula.

## Estrutura

- backend.py: modelos matemáticos e textos explicativos.
- frontend.py: interface Streamlit e gráficos Plotly.
- requirements.txt: dependências com faixas de versão.
- test_modelos.py: 14 testes dos modelos.
- test_interface.py: testes funcionais Streamlit.
- Manual_EvoLab.docx: manual completo, também disponível para download no aplicativo.

Desenvolvido para atividades de genética de populações do Prof. Leandro Martins de Freitas, Grupo Genética e Bioinformática, IMS/UFBA.

## Testes de interface

```bash
python -m unittest test_interface.py -v
```

## Apresentação institucional e orientações

A abertura identifica o Grupo Genética e Bioinformática, o IMS/UFBA, o Campus de Vitória da Conquista, o Curso de Ciências Biológicas e o Prof. Leandro Martins de Freitas, com contato e objetivo educacional. Cada um dos sete modelos apresenta uma introdução, orientações de configuração e interpretação dos resultados, visíveis antes dos indicadores e gráficos. Os textos estão em apresentacao.py.

## Seleção natural e mutação

O sétimo modelo aplica seleção de viabilidade seguida de mutação bidirecional no pool gênico e acasalamento aleatório. A população é infinita, sem deriva ou migração. O gráfico mostra A e a no combinado e uma referência de A com seleção sem mutação, também exportável em CSV. μ = ν = 0 recupera seleção isolada; s = 0 recupera mutação isolada. Aptidão média zero interrompe o cálculo, pois a mutação atua após a seleção.
