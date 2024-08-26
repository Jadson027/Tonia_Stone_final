import pandas as pd
import os
from glob import glob

# Função para calcular o Lucro do Mês
def calcular_lucro(df):
    valor_coluna = 'Valor (R$)'  # A coluna que você está usando para os cálculos
    total_pagamentos = df[df['Tipo de Transação'] == 'pagamento'][valor_coluna].abs().sum()
    total_recebimentos = df[df['Tipo de Transação'] == 'recebimento'][valor_coluna].sum()
    lucro = total_recebimentos - total_pagamentos
    return total_pagamentos, total_recebimentos, lucro

# Função para calcular a Necessidade de Capital de Giro (NCG)
def calcular_ncg(df):
    valor_coluna = 'Valor (R$)'  # A coluna que você está usando para os cálculos
    # Contas a Pagar (CP): Todo pagamento na coluna 'Tipo de Transação'
    contas_a_pagar = df[df['Tipo de Transação'] == 'pagamento'][valor_coluna].abs().sum()

    # Contas a Receber (CR): Todos os recebimentos na coluna 'Tipo de Transação'
    contas_a_receber = df[df['Tipo de Transação'] == 'recebimento'][valor_coluna].sum()

    # Valor em Estoque (VE): 'Compra de insumos' na coluna 'Descrição'
    valor_estoque = df[df['Descrição'] == 'compra de insumos'][valor_coluna].sum()

    # Fórmula da NCG: CP – (CR + VE)
    ncg = contas_a_pagar - (contas_a_receber + valor_estoque)
    return ncg

# Função para prever o Capital de Giro necessário no próximo mês
def prever_capital_de_giro(lucros, vendas, gastos, capital_de_giro_atual):
    # Analisar as oscilações de vendas e gastos
    variacao_vendas = (max(vendas) - min(vendas)) / len(vendas) if len(vendas) > 1 else 0
    variacao_gastos = (max(gastos) - min(gastos)) / len(gastos) if len(gastos) > 1 else 0

    # Prever necessidade de capital de giro considerando oscilações e histórico
    previsao_gastos = sum(gastos) / len(gastos) + variacao_gastos
    previsao_vendas = sum(vendas) / len(vendas) - variacao_vendas

    # Previsão de capital de giro para o próximo mês
    previsao_capital_giro = capital_de_giro_atual + previsao_gastos - previsao_vendas
    return previsao_capital_giro

# Função para analisar o comando do usuário e extrair palavras-chave
def interpretar_comando(comando):
    palavras_chave = {
        "tipo_transacao": None,
        "mes": None,
        "categoria": None,
        "descricao": None,
        "metodo_pagamento": None,
        "detalhamento": None,
        "cancelar": False
    }

    comando = comando.lower()

    # Variáveis para tipo de transação
    transacao_recebimento = [
        "recebimento", "recebimentos", "entradas", "ganhos", "recebi", 
        "receber", "faturamento", "faturei", "créditos", "creditos", 
        "depósitos", "deposito", "entrar dinheiro", "receita", 
        "receitas", "entrada de caixa", "dinheiro recebido", "vendas", 
        "faturamento bruto", "faturamento total", "renda", "rendimentos"
    ]
    
    transacao_pagamento = [
        "pagamento", "pagamentos", "saídas", "saída", "gastos", 
        "paguei", "pagar", "compras", "comprei", "debitos", 
        "débitos", "insumos", "compra", "comprando", "despesas", 
        "despesa", "contas pagas", "contas a pagar", "desembolso", 
        "dinheiro gasto", "saiu do caixa", "despesas operacionais", 
        "despesas fixas", "despesas variáveis", "custos", 
        "custos fixos", "custos variáveis", "pagamento de fornecedores",
        "compra de equipamentos", "equipamentos", "pagamento de impostos", 
        "imposto", "impostos", "compra de insumos", "luz", "venda", "vendas"
    ]
    
    transacao_completo = [
        "total", "geral", "completo", "tudo", "toda", 
        "consolidado", "consolidei", "balanço", "balanco", 
        "resumo", "resumo geral", "totalizador", "fechamento", 
        "fechamento mensal", "fechar mês", "resultado completo", 
        "resultado geral", "predial", "reparos", "produtos"
    ]

    # Variáveis para cancelar
    cancelar_opcoes = [
        "cancelar", "menu", "menu principal", "não quero", 
        "não é isso", "nao quero", "nao é isso", "abortar", 
        "sair", "desistir", "parar", "interromper", "voltar", 
        "resetar", "reiniciar", "desfazer", "cancela isso"
    ]

    # Verificar se o usuário deseja cancelar
    if any(palavra in comando for palavra in cancelar_opcoes):
        palavras_chave["cancelar"] = True
        return palavras_chave

    # Identificar tipo de transação
    if any(palavra in comando for palavra in transacao_recebimento):
        palavras_chave["tipo_transacao"] = "recebimento"
    elif any(palavra in comando for palavra in transacao_pagamento):
        palavras_chave["tipo_transacao"] = "pagamento"
    elif any(palavra in comando for palavra in transacao_completo):
        palavras_chave["tipo_transacao"] = "completo"

    # Variáveis para mês
    meses = {
        "janeiro": "2025-01", "fevereiro": "2025-02", "março": "2025-03", 
        "abril": "2025-04", "maio": "2025-05", "junho": "2025-06", 
        "julho": "2025-07", "agosto": "2025-08", "setembro": "2025-09", 
        "outubro": "2025-10", "novembro": "2025-11", "dezembro": "2025-12",
        "primeiro mês": "2025-01", "segundo mês": "2025-02", "terceiro mês": "2025-03",
        "quarto mês": "2025-04", "quinto mês": "2025-05", "sexto mês": "2025-06",
        "sétimo mês": "2025-07", "oitavo mês": "2025-08", "nono mês": "2025-09",
        "décimo mês": "2025-10", "undécimo mês": "2025-11", "décimo segundo mês": "2025-12"
    }

    for mes, valor in meses.items():
        if mes in comando:
            palavras_chave["mes"] = valor

    # Variáveis para método de pagamento
    metodos_pagamento = {
        "pix": "pix", "dinheiro": "dinheiro", "boleto": "boleto", 
        "cartão de crédito": "cartão de crédito", "cartão de débito": "cartão de débito", 
        "crédito": "cartão de crédito", "débito": "cartão de débito", 
        "no crédito": "cartão de crédito", "no débito": "cartão de débito", 
        "pagou no pix": "pix", "pagou em dinheiro": "dinheiro", 
        "transferência bancária": "pix", "pago com boleto": "boleto", 
        "boleto bancário": "boleto", "no cartão de crédito": "cartão de crédito", 
        "no cartão de débito": "cartão de débito", "cartão": "cartão de crédito"
    }

    for metodo, valor in metodos_pagamento.items():
        if metodo in comando:
            palavras_chave["metodo_pagamento"] = valor

    # Variáveis para categoria e descrição
    categorias_possiveis = [
        "alimentação", "serviços", "insumos", "suprimentos", 
        "fornecedores", "mercadorias", "combustível", "aluguel", 
        "manutenção", "limpeza", "transporte", "materiais", 
        "propaganda", "marketing", "publicidade", "impostos", 
        "compra de equipamentos", "equipamentos", "produtos", "predial", 
        "luz", "reparos"
    ]
    
    for categoria in categorias_possiveis:
        if categoria in comando:
            palavras_chave["categoria"] = categoria
            palavras_chave["detalhamento"] = "categoria"

    descricoes_possiveis = [
        "insumos", "material", "produtos", "estoque", 
        "ferramentas", "equipamentos", "papelaria", "informática", 
        "tecnologia", "software", "hardware", "peças", 
        "comida", "bebida", "suporte técnico", "consultoria", 
        "impostos", "predial", "luz", "reparos", "produtos"
    ]
    
    for descricao in descricoes_possiveis:
        if descricao in comando:
            palavras_chave["descricao"] = descricao
            palavras_chave["detalhamento"] = "descricao"

    # Se nenhum detalhamento específico for identificado, assumir relatório mensal total
    if palavras_chave["detalhamento"] is None:
        palavras_chave["detalhamento"] = "mensal_total"

    return palavras_chave

# Função para gerar o relatório com base nos filtros aplicados
def gerar_relatorio(df, tipo_transacao=None, categoria=None, descricao=None, metodo_pagamento=None):
    # Aplicar filtros conforme solicitado
    if tipo_transacao and tipo_transacao != 'completo':
        df = df[df['Tipo de Transação'] == tipo_transacao]
    
    if categoria:
        df = df[df['Categoria'] == categoria]
    
    if descricao:
        df = df[df['Descrição'] == descricao]
    
    if metodo_pagamento:
        df = df[df['Método de Pagamento'] == metodo_pagamento]
    
    # Calcular total
    total = df['Valor (R$)'].sum()
    return total, df

# Definir o caminho da pasta onde estão as planilhas
caminho_pasta = r'C:\Users\jadso\Desktop\AssistenteIA'

# Criar a pasta 'reports' se ela não existir
caminho_reports = os.path.join(caminho_pasta, 'reports')
if not os.path.exists(caminho_reports):
    os.makedirs(caminho_reports)

# Obter a lista de todos os arquivos Excel na pasta que correspondem ao padrão
arquivos_excel = glob(os.path.join(caminho_pasta, 'Planilha seu francisco - FAST FOOD - *.xlsx'))

# Lista para armazenar os DataFrames de cada arquivo
dataframes = []

# Loop através de cada arquivo e ler o conteúdo
for arquivo in arquivos_excel:
    try:
        df = pd.read_excel(arquivo)
        
        # Remover linhas que não contenham datas válidas na coluna 'Data'
        df = df[pd.to_datetime(df['Data'], errors='coerce').notna()]
        
        # Converter a coluna 'Data' para datetime
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
        
        # Extrair o mês e o ano da coluna 'Data' e criar uma nova coluna 'Mês'
        df['Mês'] = df['Data'].dt.strftime('%Y-%m')

        # Padronizar colunas de texto para minúsculas
        df['Tipo de Transação'] = df['Tipo de Transação'].str.lower()
        df['Categoria'] = df['Categoria'].str.lower()
        df['Descrição'] = df['Descrição'].str.lower()
        df['Método de Pagamento'] = df['Método de Pagamento'].str.lower()
        
        dataframes.append(df)
        print(f"Arquivo {os.path.basename(arquivo)} carregado com sucesso.")
    except Exception as e:
        print(f"Erro ao carregar {os.path.basename(arquivo)}: {e}")

# Concatenar todos os DataFrames em um único
if dataframes:
    df_combined = pd.concat(dataframes, ignore_index=True)
    print("Todos os arquivos foram combinados com sucesso.")
else:
    print("Nenhum arquivo foi carregado. Verifique o caminho e os arquivos disponíveis.")
    exit()

# Menu de opções
def interface_inicial():
    print("\nBem-vindo ao Assistente Financeiro!")
    print("Relatórios Detalhados: Visão clara dos gastos dos últimos três meses, receitas e saldo de caixa.")
    print("Análises Financeiras: Insights precisos para melhorar suas decisões.")
    print("Dashboard: Gráfico visual para entender as finanças e informações sobre capital de giro.")
    
    print("\nEscolha uma das opções:")
    print("1: Relatórios")
    print("2: Gerenciamento Financeiro")
    print("3: Buscar por Texto")
    print("4: Outro")
    
    opcao = input("Digite o número da opção desejada: ")
    
    if opcao == "1":
        relatorios()
    elif opcao == "2":
        gerenciamento_financeiro()
    elif opcao == "3":
        fluxo_buscar_por_texto()
    elif opcao == "4":
        print("Sinto muito, você poderá encontrar o que está buscando em um de nossos canais de atendimento:")
        print("Telefone: 3004 9680 (capitais e regiões metropolitanas) ou 0800 326 0506 (demais regiões)")
        print("Ou envie um e-mail para: meajuda@stone.com.br")
    else:
        print("Opção inválida. Tente novamente.")
        interface_inicial()

def relatorios():
    # Solicitar ao usuário que insira o mês que deseja filtrar
    meses_disponiveis = df_combined['Mês'].unique()
    print("\nMeses disponíveis:")
    for idx, mes in enumerate(meses_disponiveis, start=1):
        print(f"{idx}. {mes}")
    
    try:
        mes_opcao = int(input("Selecione o número do mês que deseja filtrar: "))
        if mes_opcao < 1 or mes_opcao > len(meses_disponiveis):
            raise ValueError("Opção inválida.")
        
        mes_especifico = meses_disponiveis[mes_opcao - 1]
    except ValueError as e:
        print(f"Erro: {e}. Tente novamente.")
        relatorios()
        return
    
    # Filtrar o DataFrame combinado pelo mês especificado
    df_filtrado = df_combined[df_combined['Mês'] == mes_especifico].copy()
    
    if df_filtrado.empty:
        print(f"Não há dados disponíveis para o mês {mes_especifico}.")
        interface_inicial()
    else:
        # Menu para escolha entre recebimentos, pagamentos ou ambos
        print("\nEscolha o tipo de transação:")
        print("1. Relatório de Recebimentos")
        print("2. Relatório de Pagamentos")
        print("3. Relatório Total Mensal Completo (Recebimentos + Pagamentos)")
        try:
            tipo_opcao = int(input("Digite o número da opção desejada: "))
            if tipo_opcao < 1 or tipo_opcao > 3:
                raise ValueError("Opção inválida.")
            
            if tipo_opcao == 1:
                tipo_transacao = 'recebimento'
                df_filtrado = df_filtrado[df_filtrado['Tipo de Transação'] == tipo_transacao]
            elif tipo_opcao == 2:
                tipo_transacao = 'pagamento'
                df_filtrado = df_filtrado[df_filtrado['Tipo de Transação'] == tipo_transacao]
            elif tipo_opcao == 3:
                tipo_transacao = 'completo'
        except ValueError as e:
            print(f"Erro: {e}. Tente novamente.")
            relatorios()
            return
        
        # Menu para escolha de detalhamento do relatório
        print("\nEscolha o detalhamento do relatório:")
        print("1. Relatório Mensal Total")
        print("2. Registros por Método de Pagamento (PIX, Boleto, etc.)")
        print("3. Registros por Categoria")
        print("4. Registros por Descrição")
        
        try:
            detalhamento_opcao = int(input("Digite o número da opção desejada: "))
            if detalhamento_opcao < 1 or detalhamento_opcao > 4:
                raise ValueError("Opção inválida.")
            
            if detalhamento_opcao == 1:
                # Relatório Mensal Total
                total, df_detalhado = gerar_relatorio(df_filtrado)
                print(f"Total {tipo_transacao} no mês {mes_especifico}: R${total:.2f}")
            
            elif detalhamento_opcao == 2:
                # Menu de Métodos de Pagamento disponíveis
                metodos_disponiveis = df_filtrado['Método de Pagamento'].unique()
                print("\nMétodos de pagamento disponíveis:")
                for idx, metodo in enumerate(metodos_disponiveis, start=1):
                    print(f"{idx}. {metodo}")
                
                metodo_opcao = int(input("Selecione o número do método de pagamento: "))
                metodo_pagamento = metodos_disponiveis[metodo_opcao - 1]
                
                total, df_detalhado = gerar_relatorio(df_filtrado, metodo_pagamento=metodo_pagamento)
                print(f"Total {tipo_transacao} no mês {mes_especifico} via {metodo_pagamento}: R${total:.2f}")
            
            elif detalhamento_opcao == 3:
                # Menu de Categorias disponíveis
                categorias_disponiveis = df_filtrado['Categoria'].unique()
                print("\nCategorias disponíveis:")
                for idx, categoria in enumerate(categorias_disponiveis, start=1):
                    print(f"{idx}. {categoria}")
                
                categoria_opcao = int(input("Selecione o número da categoria: "))
                categoria = categorias_disponiveis[categoria_opcao - 1]
                
                total, df_detalhado = gerar_relatorio(df_filtrado, categoria=categoria)
                print(f"Total {tipo_transacao} na categoria {categoria} no mês {mes_especifico}: R${total:.2f}")
            
            elif detalhamento_opcao == 4:
                # Menu de Descrições disponíveis
                descricoes_disponiveis = df_filtrado['Descrição'].unique()
                print("\nDescrições disponíveis:")
                for idx, descricao in enumerate(descricoes_disponiveis, start=1):
                    print(f"{idx}. {descricao}")
                
                descricao_opcao = int(input("Selecione o número da descrição: "))
                descricao = descricoes_disponiveis[descricao_opcao - 1]
                
                total, df_detalhado = gerar_relatorio(df_filtrado, descricao=descricao)
                print(f"Total {tipo_transacao} na descrição {descricao} no mês {mes_especifico}: R${total:.2f}")
            
        except ValueError as e:
            print(f"Erro: {e}. Tente novamente.")
            relatorios()
            return
        
        # Exibir os detalhes do DataFrame na conversa
        print("\nResumo do Relatório:")
        print(df_detalhado)
        
        # Salvar os resultados em um arquivo Excel
        df_detalhado.to_excel(os.path.join(caminho_reports, f'relatorio_personalizado_{tipo_transacao}_{mes_especifico}.xlsx'), index=False)
        print(f"\nRelatório para {tipo_transacao} no mês {mes_especifico} foi salvo na pasta 'reports'.")

        # Perguntar se deseja tentar novamente
        nova_tentativa = input("Deseja gerar outro relatório? (s/n): ").strip().lower()
        if nova_tentativa == 's':
            relatorios()
        else:
            interface_inicial()

def gerenciamento_financeiro():
    # Solicitar ao usuário qual opção ele deseja analisar
    meses_disponiveis = df_combined['Mês'].unique()
    print("Opções disponíveis:")
    for i, mes in enumerate(meses_disponiveis, start=1):
        print(f"{i}. {mes}")
    print(f"{len(meses_disponiveis)+1}. Gerenciamento Total")
    print(f"{len(meses_disponiveis)+2}. Previsibilidade Financeira")
    
    try:
        opcao_escolhida = int(input("Digite o número da opção desejada: ").strip())
        if opcao_escolhida < 1 or opcao_escolhida > len(meses_disponiveis) + 2:
            raise ValueError("Opção inválida.")
        
        if opcao_escolhida <= len(meses_disponiveis):
            mes_escolhido = meses_disponiveis[opcao_escolhida-1]
            df_mes = df_combined[df_combined['Mês'] == mes_escolhido]

            # Calcular valores para o mês escolhido
            total_pagamentos, total_recebimentos, lucro = calcular_lucro(df_mes)
            ncg = calcular_ncg(df_mes)

            # Exibir os resultados para o mês escolhido
            print(f"\n--- Resultados para {mes_escolhido} ---")
            print(f"Total de Pagamentos: R$ {total_pagamentos:.2f}")
            print(f"Total de Recebimentos: R$ {total_recebimentos:.2f}")
            print(f"Lucro do Mês: R$ {lucro:.2f}")
            print(f"Necessidade de Capital de Giro (NCG): R$ {ncg:.2f}")
        
        elif opcao_escolhida == len(meses_disponiveis) + 1:
            # Gerenciamento Total
            total_pagamentos_geral = 0
            total_recebimentos_geral = 0
            lucro_acumulado = 0
            capital_de_giro_acumulado = 0

            for mes in meses_disponiveis:
                df_mes = df_combined[df_combined['Mês'] == mes]
                total_pagamentos, total_recebimentos, lucro = calcular_lucro(df_mes)
                ncg = calcular_ncg(df_mes)

                total_pagamentos_geral += total_pagamentos
                total_recebimentos_geral += total_recebimentos
                lucro_acumulado += lucro
                capital_de_giro_acumulado += lucro

            # Exibir os resultados para o gerenciamento total
            print("\n--- Resultados Gerenciamento Total ---")
            print(f"Total de Pagamentos: R$ {total_pagamentos_geral:.2f}")
            print(f"Total de Recebimentos: R$ {total_recebimentos_geral:.2f}")
            print(f"Lucro Total Acumulado: R$ {lucro_acumulado:.2f}")
            print(f"Capital de Giro Acumulado (Saldo): R$ {capital_de_giro_acumulado:.2f}")
            print(f"Necessidade de Capital de Giro (NCG): R$ {ncg:.2f}")

        elif opcao_escolhida == len(meses_disponiveis) + 2:
            # Previsibilidade Financeira
            lucros = []
            vendas = []
            gastos = []
            capital_de_giro_atual = 0

            for mes in meses_disponiveis:
                df_mes = df_combined[df_combined['Mês'] == mes]
                total_pagamentos, total_recebimentos, lucro = calcular_lucro(df_mes)
                lucros.append(lucro)
                vendas.append(total_recebimentos)
                gastos.append(total_pagamentos)
                capital_de_giro_atual += lucro

            previsao_capital_giro = prever_capital_de_giro(lucros, vendas, gastos, capital_de_giro_atual)

            # Exibir os resultados da previsão financeira
            print("\n--- Previsibilidade Financeira ---")
            print(f"Previsão de Capital de Giro necessário para o próximo mês: R$ {previsao_capital_giro:.2f}")

    except ValueError as e:
        print(f"Erro: {e}. Tente novamente.")
        gerenciamento_financeiro()
        return
    
    # Perguntar se deseja tentar novamente
    nova_tentativa = input("Deseja realizar outra análise financeira? (s/n): ").strip().lower()
    if nova_tentativa == 's':
        gerenciamento_financeiro()
    else:
        interface_inicial()

def fluxo_buscar_por_texto():
    # Solicitar ao usuário que insira um comando
    while True:
        comando_usuario = input("Digite o comando para gerar um relatório personalizado: ")
        filtros = interpretar_comando(comando_usuario)

        if filtros["cancelar"]:
            print("Operação cancelada. Retornando ao menu principal.")
            interface_inicial()
            return

        if not filtros["tipo_transacao"]:
            print("Não foi possível identificar o tipo de transação (recebimento, pagamento ou completo). Tente novamente.")
            continue

        if not filtros["mes"]:
            print("Não foi possível identificar o mês desejado. Tente novamente.")
            continue

        # Filtrar os dados combinados para o mês específico
        df_filtrado = df_combined[df_combined['Mês'] == filtros['mes']]

        total, df_detalhado = gerar_relatorio(
            df_filtrado,
            tipo_transacao=filtros["tipo_transacao"],
            categoria=filtros["categoria"],
            descricao=filtros["descricao"],
            metodo_pagamento=filtros["metodo_pagamento"]
        )

        if df_detalhado.empty:
            print("Nenhum registro encontrado com os filtros especificados.")
        else:
            print(f"Total {filtros['tipo_transacao']} no mês {filtros['mes']}: R${total:.2f}")
            print(df_detalhado)

            # Salvar os resultados em um arquivo Excel
            detalhes = f'_{filtros["detalhamento"]}' if filtros["detalhamento"] != "mensal_total" else ""
            relatorio_nome = f'relatorio_{filtros["tipo_transacao"]}_{filtros["mes"]}{detalhes}.xlsx'
            df_detalhado.to_excel(os.path.join(caminho_reports, relatorio_nome), index=False)
            print(f"Relatório salvo como {relatorio_nome} na pasta 'reports'.")
        
        # Perguntar se deseja tentar novamente
        nova_tentativa = input("Deseja realizar outra busca por texto? (s/n): ").strip().lower()
        if nova_tentativa == 's':
            continue
        else:
            interface_inicial()
            break

# Iniciar a interface
interface_inicial()
