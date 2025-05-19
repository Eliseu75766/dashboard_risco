# Análise de Risco em Ambientes Logísticos

![Dashboard Preview](https://dashboardrisco.streamlit.app/)

## Sobre o Projeto

Este projeto implementa um sistema de análise de risco para ambientes logísticos, utilizando dados simulados para demonstrar como a inteligência analítica pode ser aplicada na prevenção de perdas e gestão de riscos em centros de distribuição.

O sistema consiste em:
1. Um conjunto de dados fictícios que simulam incidentes, riscos, métricas de desempenho e componentes do sistema
2. Uma planilha no Google Sheets para armazenamento e análise básica dos dados
3. Um dashboard interativo em Streamlit para visualização avançada e análise dinâmica

## Estrutura do Projeto

```
analise_risco_logistica/
├── dados/                      # Dados fictícios em formato CSV
│   ├── registro_incidentes.csv # Registro de incidentes de segurança
│   ├── analise_riscos.csv      # Análise de riscos identificados
│   ├── metricas_desempenho.csv # Métricas mensais de desempenho
│   └── componentes_sistema.csv # Dados dos componentes do sistema
├── screenshots/                # Capturas de tela do dashboard
├── analise_variaveis.md        # Documentação da análise de variáveis
├── dashboard_risco.py          # Código-fonte do dashboard Streamlit
├── gerar_dados_ficticios.py    # Script para geração de dados fictícios
├── instrucoes_importacao_google_sheets.md # Instruções para Google Sheets
├── requirements.txt            # Dependências do projeto
└── README.md                   # Este arquivo
```

## Requisitos

- Python 3.8+
- Bibliotecas Python listadas em `requirements.txt`
- Acesso ao Google Sheets (opcional, para a parte de planilha)

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/analise-risco-logistica.git
cd analise-risco-logistica
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Geração de Dados Fictícios

Os dados já estão incluídos no diretório `dados/`, mas caso queira gerar novos dados:

```bash
python gerar_dados_ficticios.py
```

### Importação para Google Sheets

Para importar os dados para o Google Sheets, siga as instruções detalhadas em `instrucoes_importacao_google_sheets.md`.

### Execução do Dashboard

Para iniciar o dashboard Streamlit:

```bash
streamlit run dashboard_risco.py
```

O dashboard estará disponível em `http://localhost:8501`.

## Funcionalidades do Dashboard

O dashboard oferece as seguintes visualizações e funcionalidades:

### Visão Geral
- KPIs principais: Total de incidentes, valor total de perdas, tempo médio de detecção e eficácia média de resposta
- Tendência de incidentes por categoria ao longo do tempo
- Valor total de perdas por categoria
- Evolução da eficácia de detecção e resposta
- Distribuição de incidentes por local

### Análise de Incidentes
- Filtros por subcategoria, local e status
- Distribuição por subcategoria e método de detecção
- Lista detalhada de incidentes
- Análise da relação entre tempo de detecção e eficácia da resposta

### Matriz de Risco
- Visualização da matriz de risco 5x5
- Filtros por categoria e nível de risco
- Lista de riscos identificados
- Análise de eficácia dos controles
- Comparação entre risco inerente e residual

### Desempenho do Sistema
- KPIs de componentes: total, operacionais, incidentes detectados e precisão média
- Distribuição por tipo de componente e status operacional
- Taxa média de precisão por tipo de componente
- Lista detalhada de componentes
- Análise de falsos positivos vs falsos negativos

### Análise Financeira
- KPIs financeiros: valor total de perdas, custo total de mitigação e ROI médio
- Evolução de perdas por categoria ao longo do tempo
- Evolução do ROI de segurança
- Análise de custo-benefício por categoria
- Métricas financeiras mensais
- Projeção de economia anual

## Personalização

### Dados

Para utilizar seus próprios dados, substitua os arquivos CSV no diretório `dados/` mantendo a mesma estrutura de colunas, ou modifique o script `gerar_dados_ficticios.py` para gerar dados que correspondam ao seu ambiente específico.

### Dashboard

O código do dashboard em `dashboard_risco.py` é modular e bem comentado, facilitando a personalização. Você pode:

- Adicionar novas visualizações
- Modificar os filtros existentes
- Ajustar o layout e as cores
- Integrar com fontes de dados em tempo real

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias.

## Licença

Este projeto foi realizado por Eliseu Melo e Juliano Gabriel 
