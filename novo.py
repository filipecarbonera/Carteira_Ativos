# Importando as bibliotecas necessárias.
import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Definição da função para realizar a análise.
def realizar_analise(start_date, end_date, carteira_df):

    # Isolando em listas as duas colunas da carteira definida.
    ativos = carteira_df['Ativo'].tolist()
    valores_investidos = carteira_df['Valor Investido'].tolist()

    # Criação de um DataFrame com os valores diários de fechamento de cada ação definida na carteira no período selecionado.
    precos = pd.DataFrame()
    for ativo in ativos:
        precos[ativo] = yf.download(ativo, start=start_date, end=end_date)['Adj Close']

    # Criação de um DataFrame com a posição diária de cada ativo e um consolidado considerando a quantidade de ações adquiridas com cada valor investido.
    primeiro_preco = precos.iloc[0]
    qtd_acoes = pd.Series(valores_investidos / primeiro_preco, index=primeiro_preco.index)
    posicao_diaria = precos * qtd_acoes
    posicao_diaria['Carteira Teórica'] = posicao_diaria.sum(axis=1)

    # Obtendo dados do índice Bovespa e unindo a informação com as demais posições de carteira.
    ibov = yf.download('^BVSP', start=start_date, end=end_date)
    ibov.rename(columns={'Adj Close': 'IBOV'}, inplace=True)
    ibov = ibov.drop(ibov.columns[[0,1,2,3,5]], axis=1)
    consolidado = pd.merge(posicao_diaria, ibov, how='inner', on='Date')

    # Normalizando os dados das posições.
    c_normalizado = consolidado / consolidado.iloc[0]
    
    # Retornando as posições consolidadas e normalizadas para plotar gráficos.
    return c_normalizado, consolidado

# Título do aplicativo.
st.title('Análise de Carteira de Ativos')

# Seleção da data de início e fim da análise.
start_date = st.date_input("Selecione a Data Inicial da análise:", key='start_date')
end_date = st.date_input("Selecione a Data Final da análise:", key='end_date')

# Subtítulo do aplicativo.
st.subheader('Informe os ativos e valores para compor a Carteira')
st.write("Para cada conjunto de ativo e valor selecionados precione ENTER para incorporá-los à Carteira.")

# Lista com os ativos disponíveis para análise.
ativos_disponiveis = ['PETR4.SA','VALE3.SA','WEGE3.SA','RADL3.SA','OIBR3.SA','KNRI11.SA','SMAL11.SA', 'IVVB11.SA']

# Listas para armazenar os ativos e valores de carteira.
ativos_selecionados = []
valores_investidos = []

# Definição de iteradores.
a = 0
b = 0

# Definindo as variáveis de ativo e valor para iterar.
ativo_selecionado = 0
valor_investido = 0

# Loop para seleção de diversos conjuntos de ativo e valor.
while True:
    ativo_selecionado = st.selectbox(f'Selecione o Ativo:', ativos_disponiveis, key=f"ativo_selecionado_{a}")
    a+=1
    if ativo_selecionado == '':
        break
    
    valor_investido = st.number_input(f"Valor a investir no ativo {ativo_selecionado}:", step=0.1, key=f'valor_investido{b}')
    b+=1
    if valor_investido == 0 or valor_investido is None:
        break
    
    ativos_selecionados.append(ativo_selecionado)
    valores_investidos.append(valor_investido)

# Exibindo a carteira de ativos e valores selecionados em uma tabela de controle.
if ativos_selecionados and valores_investidos:
    carteira_df = pd.DataFrame({'Ativo': ativos_selecionados, 'Valor Investido': valores_investidos})
    st.write('Carteira de Ativos (Confira as informações incluídas antes de iniciar a análise)')
    st.dataframe(carteira_df)

    # Botão para realizar a análise.
    if st.button('Realizar Análise'):
        data_valida = True
        for ativo in ativos_selecionados:
            dados = yf.download(ativo, start=start_date, end=end_date)
            if dados.empty:
                st.error(f"Não há dados de preço disponíveis para o ativo {ativo} em todo o período selecionado.")
                data_valida = False
                break
        
        if data_valida:
            # Aplica a função "realizar_analise" definida no início do código.
            n, c = realizar_analise(start_date, end_date, carteira_df)

            # Plota gráficos de análise.
            st.write('Compatativo de Carteira com Índice Bovespa (normalizado)')
            st.line_chart(n[['IBOV','Carteira Teórica']])
            st.write('Compatativo de Ativos em Carteira (normalizado)')
            st.line_chart(n.iloc[:, :-1])
            st.write('Compatativo de Ativos em Carteira (absoluto)')
            st.line_chart(c.iloc[:, :-2])

else:
    st.write('Nenhum ativo e valor selecionados.')