import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import os

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Análise de Risco - Ambientes Logísticos",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar os dados
@st.cache_data
def carregar_dados():
    # Definir caminho para os dados
    data_path = "dados"
    
    # Carregar os arquivos CSV
    try:
        df_incidentes = pd.read_csv(os.path.join(data_path, "registro_incidentes.csv"))
        df_riscos = pd.read_csv(os.path.join(data_path, "analise_riscos.csv"))
        df_metricas = pd.read_csv(os.path.join(data_path, "metricas_desempenho.csv"))
        df_componentes = pd.read_csv(os.path.join(data_path, "componentes_sistema.csv"))
        
        # Converter colunas de data
        df_incidentes['Data_Hora'] = pd.to_datetime(df_incidentes['Data_Hora'])
        df_incidentes['Data'] = df_incidentes['Data_Hora'].dt.date
        df_incidentes['Mes_Ano'] = df_incidentes['Data_Hora'].dt.strftime('%Y-%m')
        
        df_riscos['Prazo'] = pd.to_datetime(df_riscos['Prazo'])
        
        return df_incidentes, df_riscos, df_metricas, df_componentes
    
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None, None, None, None

# Função para criar mapa de calor de matriz de risco
def criar_matriz_risco(df_riscos):
    # Criar matriz de contagem
    matriz = np.zeros((5, 5))
    
    for _, row in df_riscos.iterrows():
        prob = int(row['Probabilidade']) - 1  # Ajustar para índice 0-4
        imp = int(row['Impacto']) - 1  # Ajustar para índice 0-4
        matriz[prob, imp] += 1
    
    # Criar figura com plotly
    fig = go.Figure(data=go.Heatmap(
        z=matriz,
        x=['1-Insignificante', '2-Menor', '3-Moderado', '4-Maior', '5-Catastrófico'],
        y=['1-Rara', '2-Improvável', '3-Possível', '4-Provável', '5-Quase Certa'],
        colorscale=[
            [0, 'green'],
            [0.25, 'lightgreen'],
            [0.5, 'yellow'],
            [0.75, 'orange'],
            [1, 'red']
        ],
        showscale=False,
        text=matriz.astype(int),
        texttemplate="%{text}",
        textfont={"size":14},
    ))
    
    # Adicionar linhas para separar níveis de risco
    fig.add_shape(type="line", x0=1.5, y0=-0.5, x1=1.5, y1=4.5, line=dict(color="white", width=2))
    fig.add_shape(type="line", x0=3.5, y0=-0.5, x1=3.5, y1=4.5, line=dict(color="white", width=2))
    fig.add_shape(type="line", x0=-0.5, y0=1.5, x1=4.5, y1=1.5, line=dict(color="white", width=2))
    fig.add_shape(type="line", x0=-0.5, y0=3.5, x1=4.5, y1=3.5, line=dict(color="white", width=2))
    
    fig.update_layout(
        title="Matriz de Risco",
        xaxis_title="Impacto",
        yaxis_title="Probabilidade",
        height=500,
    )
    
    return fig

# Função para criar gráfico de tendência de incidentes
def criar_grafico_tendencia_incidentes(df_incidentes):
    # Agrupar por mês e categoria
    df_trend = df_incidentes.groupby(['Mes_Ano', 'Categoria_Risco']).size().reset_index(name='Contagem')
    
    # Criar gráfico
    fig = px.line(
        df_trend, 
        x='Mes_Ano', 
        y='Contagem', 
        color='Categoria_Risco',
        markers=True,
        title='Tendência de Incidentes por Categoria',
        labels={'Mes_Ano': 'Mês/Ano', 'Contagem': 'Número de Incidentes', 'Categoria_Risco': 'Categoria de Risco'}
    )
    
    fig.update_layout(height=400)
    
    return fig

# Função para criar gráfico de perdas por categoria
def criar_grafico_perdas_categoria(df_incidentes):
    # Agrupar por categoria
    df_perdas = df_incidentes.groupby('Categoria_Risco')['Valor_Perda'].sum().reset_index()
    
    # Criar gráfico
    fig = px.bar(
        df_perdas,
        x='Categoria_Risco',
        y='Valor_Perda',
        color='Categoria_Risco',
        title='Valor Total de Perdas por Categoria',
        labels={'Categoria_Risco': 'Categoria de Risco', 'Valor_Perda': 'Valor Total (R$)'}
    )
    
    fig.update_layout(height=400)
    
    return fig

# Função para criar gráfico de eficácia de detecção e resposta
def criar_grafico_eficacia(df_metricas):
    # Preparar dados
    df_eficacia = df_metricas.groupby('Mes_Ano')[['Eficacia_Deteccao', 'Eficacia_Resposta']].mean().reset_index()
    
    # Criar gráfico
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_eficacia['Mes_Ano'],
        y=df_eficacia['Eficacia_Deteccao'],
        mode='lines+markers',
        name='Eficácia de Detecção',
        line=dict(color='blue')
    ))
    
    fig.add_trace(go.Scatter(
        x=df_eficacia['Mes_Ano'],
        y=df_eficacia['Eficacia_Resposta'],
        mode='lines+markers',
        name='Eficácia de Resposta',
        line=dict(color='green')
    ))
    
    fig.update_layout(
        title='Evolução da Eficácia de Detecção e Resposta',
        xaxis_title='Mês/Ano',
        yaxis_title='Eficácia (%)',
        height=400
    )
    
    return fig

# Função para criar gráfico de distribuição de incidentes por local
def criar_grafico_incidentes_local(df_incidentes):
    # Agrupar por local
    df_local = df_incidentes.groupby(['Local', 'Categoria_Risco']).size().reset_index(name='Contagem')
    
    # Criar gráfico
    fig = px.bar(
        df_local,
        x='Local',
        y='Contagem',
        color='Categoria_Risco',
        title='Distribuição de Incidentes por Local',
        labels={'Local': 'Local', 'Contagem': 'Número de Incidentes', 'Categoria_Risco': 'Categoria de Risco'}
    )
    
    fig.update_layout(height=400)
    
    return fig

# Função para criar gráfico de precisão dos componentes
def criar_grafico_precisao_componentes(df_componentes):
    # Agrupar por tipo de componente
    df_precisao = df_componentes.groupby('Tipo_Componente')['Taxa_Precisao'].mean().reset_index()
    
    # Criar gráfico
    fig = px.bar(
        df_precisao,
        x='Tipo_Componente',
        y='Taxa_Precisao',
        color='Tipo_Componente',
        title='Taxa Média de Precisão por Tipo de Componente',
        labels={'Tipo_Componente': 'Tipo de Componente', 'Taxa_Precisao': 'Taxa de Precisão (%)'}
    )
    
    fig.update_layout(height=400)
    
    return fig

# Função para criar gráfico de ROI de segurança
def criar_grafico_roi(df_metricas):
    # Preparar dados
    df_roi = df_metricas.groupby('Mes_Ano')['ROI_Seguranca'].mean().reset_index()
    
    # Criar gráfico
    fig = px.line(
        df_roi,
        x='Mes_Ano',
        y='ROI_Seguranca',
        markers=True,
        title='Evolução do ROI de Segurança',
        labels={'Mes_Ano': 'Mês/Ano', 'ROI_Seguranca': 'ROI (%)'}
    )
    
    fig.update_layout(height=400)
    
    return fig

# Função principal
def main():
    # Carregar dados
    df_incidentes, df_riscos, df_metricas, df_componentes = carregar_dados()
    
    if df_incidentes is None:
        st.warning("Por favor, verifique se os arquivos de dados estão disponíveis no diretório 'dados'.")
        return
    
    # Sidebar
    st.sidebar.title("🛡️ Análise de Risco")
    st.sidebar.subheader("Ambientes Logísticos")
    
    # Opções de navegação
    pagina = st.sidebar.radio(
        "Navegação",
        ["Visão Geral", "Análise de Incidentes", "Matriz de Risco", "Desempenho do Sistema", "Análise Financeira"]
    )
    
    # Filtros globais
    st.sidebar.subheader("Filtros")
    
    # Filtro de período
    min_date = df_incidentes['Data_Hora'].min().date()
    max_date = df_incidentes['Data_Hora'].max().date()
    
    periodo = st.sidebar.date_input(
        "Período de Análise",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(periodo) == 2:
        start_date, end_date = periodo
        mask_periodo = (df_incidentes['Data'] >= start_date) & (df_incidentes['Data'] <= end_date)
        df_incidentes_filtrado = df_incidentes[mask_periodo]
    else:
        df_incidentes_filtrado = df_incidentes
    
    # Filtro de categoria de risco
    categorias = df_incidentes['Categoria_Risco'].unique().tolist()
    categorias_selecionadas = st.sidebar.multiselect(
        "Categorias de Risco",
        options=categorias,
        default=categorias
    )
    
    if categorias_selecionadas:
        df_incidentes_filtrado = df_incidentes_filtrado[df_incidentes_filtrado['Categoria_Risco'].isin(categorias_selecionadas)]
    
    # Informações do filtro
    st.sidebar.info(f"Exibindo {len(df_incidentes_filtrado)} incidentes de um total de {len(df_incidentes)}")
    
    # Créditos
    st.sidebar.markdown("---")
    st.sidebar.caption("Desenvolvido para análise de risco em ambientes logísticos")
    
    # Conteúdo principal
    if pagina == "Visão Geral":
        st.title("Dashboard de Análise de Risco - Visão Geral")
        
        # KPIs na primeira linha
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_incidentes = len(df_incidentes_filtrado)
            st.metric("Total de Incidentes", f"{total_incidentes}")
        
        with col2:
            valor_total_perdas = df_incidentes_filtrado['Valor_Perda'].sum()
            st.metric("Valor Total de Perdas", f"R$ {valor_total_perdas:,.2f}")
        
        with col3:
            tempo_medio_deteccao = df_incidentes_filtrado['Tempo_Deteccao'].mean()
            st.metric("Tempo Médio de Detecção", f"{tempo_medio_deteccao:.1f} horas")
        
        with col4:
            eficacia_media = df_incidentes_filtrado['Eficacia_Resposta'].mean()
            st.metric("Eficácia Média de Resposta", f"{eficacia_media:.1f}%")
        
        st.markdown("---")
        
        # Gráficos na segunda linha
        col1, col2 = st.columns(2)
        
        with col1:
            fig_tendencia = criar_grafico_tendencia_incidentes(df_incidentes_filtrado)
            st.plotly_chart(fig_tendencia, use_container_width=True)
        
        with col2:
            fig_perdas = criar_grafico_perdas_categoria(df_incidentes_filtrado)
            st.plotly_chart(fig_perdas, use_container_width=True)
        
        # Gráficos na terceira linha
        col1, col2 = st.columns(2)
        
        with col1:
            fig_eficacia = criar_grafico_eficacia(df_metricas)
            st.plotly_chart(fig_eficacia, use_container_width=True)
        
        with col2:
            fig_local = criar_grafico_incidentes_local(df_incidentes_filtrado)
            st.plotly_chart(fig_local, use_container_width=True)
    
    elif pagina == "Análise de Incidentes":
        st.title("Análise Detalhada de Incidentes")
        
        # Filtros específicos para esta página
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subcategorias = df_incidentes_filtrado['Subcategoria'].unique().tolist()
            subcategoria_selecionada = st.selectbox(
                "Subcategoria",
                options=["Todas"] + subcategorias
            )
        
        with col2:
            locais = df_incidentes_filtrado['Local'].unique().tolist()
            local_selecionado = st.selectbox(
                "Local",
                options=["Todos"] + locais
            )
        
        with col3:
            status_opcoes = df_incidentes_filtrado['Status'].unique().tolist()
            status_selecionado = st.selectbox(
                "Status",
                options=["Todos"] + status_opcoes
            )
        
        # Aplicar filtros adicionais
        df_filtrado = df_incidentes_filtrado.copy()
        
        if subcategoria_selecionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Subcategoria'] == subcategoria_selecionada]
        
        if local_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Local'] == local_selecionado]
        
        if status_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Status'] == status_selecionado]
        
        # Gráficos e análises
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição por subcategoria
            df_sub = df_filtrado.groupby('Subcategoria').size().reset_index(name='Contagem')
            fig_sub = px.pie(
                df_sub,
                values='Contagem',
                names='Subcategoria',
                title='Distribuição por Subcategoria',
                hole=0.4
            )
            st.plotly_chart(fig_sub, use_container_width=True)
        
        with col2:
            # Distribuição por método de detecção
            df_metodo = df_filtrado.groupby('Metodo_Deteccao').size().reset_index(name='Contagem')
            fig_metodo = px.pie(
                df_metodo,
                values='Contagem',
                names='Metodo_Deteccao',
                title='Distribuição por Método de Detecção',
                hole=0.4
            )
            st.plotly_chart(fig_metodo, use_container_width=True)
        
        # Tabela de incidentes
        st.subheader("Lista de Incidentes")
        
        colunas_exibir = ['ID_Incidente', 'Data_Hora', 'Categoria_Risco', 'Subcategoria', 
                         'Local', 'Valor_Perda', 'Tempo_Deteccao', 'Eficacia_Resposta', 'Status']
        
        st.dataframe(
            df_filtrado[colunas_exibir].sort_values('Data_Hora', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Análise de tempo de detecção vs eficácia
        st.subheader("Relação entre Tempo de Detecção e Eficácia da Resposta")
        
        fig_scatter = px.scatter(
            df_filtrado,
            x='Tempo_Deteccao',
            y='Eficacia_Resposta',
            color='Categoria_Risco',
            size='Valor_Perda',
            hover_name='ID_Incidente',
            hover_data=['Subcategoria', 'Local', 'Status'],
            title='Tempo de Detecção vs. Eficácia da Resposta',
            labels={
                'Tempo_Deteccao': 'Tempo de Detecção (horas)',
                'Eficacia_Resposta': 'Eficácia da Resposta (%)',
                'Categoria_Risco': 'Categoria de Risco'
            }
        )
        
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    elif pagina == "Matriz de Risco":
        st.title("Matriz de Risco")
        
        # Filtros específicos para esta página
        col1, col2 = st.columns(2)
        
        with col1:
            categorias_risco = df_riscos['Categoria_Risco'].unique().tolist()
            categoria_selecionada = st.selectbox(
                "Categoria de Risco",
                options=["Todas"] + categorias_risco
            )
        
        with col2:
            niveis_risco = ['Baixo', 'Médio', 'Alto', 'Extremo']
            nivel_selecionado = st.selectbox(
                "Nível de Risco",
                options=["Todos"] + niveis_risco
            )
        
        # Aplicar filtros
        df_riscos_filtrado = df_riscos.copy()
        
        if categoria_selecionada != "Todas":
            df_riscos_filtrado = df_riscos_filtrado[df_riscos_filtrado['Categoria_Risco'] == categoria_selecionada]
        
        if nivel_selecionado != "Todos":
            df_riscos_filtrado = df_riscos_filtrado[df_riscos_filtrado['Nivel_Risco'] == nivel_selecionado]
        
        # Matriz de risco
        fig_matriz = criar_matriz_risco(df_riscos_filtrado)
        st.plotly_chart(fig_matriz, use_container_width=True)
        
        # Tabela de riscos
        st.subheader("Lista de Riscos Identificados")
        
        colunas_exibir = ['ID_Risco', 'Categoria_Risco', 'Subcategoria', 'Descricao_Risco',
                         'Probabilidade', 'Impacto', 'Nivel_Risco', 'Eficacia_Controles',
                         'Nivel_Risco_Residual', 'Status_Plano']
        
        st.dataframe(
            df_riscos_filtrado[colunas_exibir].sort_values(['Nivel_Risco', 'Probabilidade', 'Impacto'], 
                                                         ascending=[False, False, False]),
            use_container_width=True,
            hide_index=True
        )
        
        # Análise de eficácia dos controles
        st.subheader("Eficácia dos Controles por Categoria de Risco")
        
        df_eficacia = df_riscos_filtrado.groupby('Categoria_Risco')['Eficacia_Controles'].mean().reset_index()
        
        fig_eficacia = px.bar(
            df_eficacia,
            x='Categoria_Risco',
            y='Eficacia_Controles',
            color='Categoria_Risco',
            title='Eficácia Média dos Controles por Categoria',
            labels={'Categoria_Risco': 'Categoria de Risco', 'Eficacia_Controles': 'Eficácia Média (%)'}
        )
        
        st.plotly_chart(fig_eficacia, use_container_width=True)
        
        # Comparação entre risco inerente e residual
        st.subheader("Comparação entre Risco Inerente e Residual")
        
        # Contar riscos por nível antes e depois dos controles
        df_comparacao = pd.DataFrame({
            'Nível': niveis_risco,
            'Risco Inerente': [
                len(df_riscos_filtrado[df_riscos_filtrado['Nivel_Risco'] == nivel])
                for nivel in niveis_risco
            ],
            'Risco Residual': [
                len(df_riscos_filtrado[df_riscos_filtrado['Nivel_Risco_Residual'] == nivel])
                for nivel in niveis_risco
            ]
        })
        
        df_comparacao_melted = pd.melt(
            df_comparacao, 
            id_vars=['Nível'], 
            value_vars=['Risco Inerente', 'Risco Residual'],
            var_name='Tipo de Risco', 
            value_name='Quantidade'
        )
        
        fig_comparacao = px.bar(
            df_comparacao_melted,
            x='Nível',
            y='Quantidade',
            color='Tipo de Risco',
            barmode='group',
            title='Comparação entre Risco Inerente e Residual',
            category_orders={"Nível": ["Baixo", "Médio", "Alto", "Extremo"]}
        )
        
        st.plotly_chart(fig_comparacao, use_container_width=True)
    
    elif pagina == "Desempenho do Sistema":
        st.title("Desempenho do Sistema de Prevenção")
        
        # Filtros específicos para esta página
        col1, col2 = st.columns(2)
        
        with col1:
            tipos_componente = df_componentes['Tipo_Componente'].unique().tolist()
            tipo_selecionado = st.selectbox(
                "Tipo de Componente",
                options=["Todos"] + tipos_componente
            )
        
        with col2:
            locais_componente = df_componentes['Localizacao'].unique().tolist()
            local_selecionado = st.selectbox(
                "Localização",
                options=["Todos"] + locais_componente
            )
        
        # Aplicar filtros
        df_componentes_filtrado = df_componentes.copy()
        
        if tipo_selecionado != "Todos":
            df_componentes_filtrado = df_componentes_filtrado[df_componentes_filtrado['Tipo_Componente'] == tipo_selecionado]
        
        if local_selecionado != "Todos":
            df_componentes_filtrado = df_componentes_filtrado[df_componentes_filtrado['Localizacao'] == local_selecionado]
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_componentes = len(df_componentes_filtrado)
            st.metric("Total de Componentes", f"{total_componentes}")
        
        with col2:
            componentes_operacionais = len(df_componentes_filtrado[df_componentes_filtrado['Status_Operacional'] == 'Operacional'])
            percentual_operacional = (componentes_operacionais / total_componentes * 100) if total_componentes > 0 else 0
            st.metric("Componentes Operacionais", f"{componentes_operacionais} ({percentual_operacional:.1f}%)")
        
        with col3:
            total_incidentes_detectados = df_componentes_filtrado['Incidentes_Detectados'].sum()
            st.metric("Total de Incidentes Detectados", f"{total_incidentes_detectados}")
        
        with col4:
            precisao_media = df_componentes_filtrado['Taxa_Precisao'].mean()
            st.metric("Taxa Média de Precisão", f"{precisao_media:.1f}%")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição por tipo de componente
            df_tipo = df_componentes_filtrado.groupby('Tipo_Componente').size().reset_index(name='Contagem')
            fig_tipo = px.pie(
                df_tipo,
                values='Contagem',
                names='Tipo_Componente',
                title='Distribuição por Tipo de Componente',
                hole=0.4
            )
            st.plotly_chart(fig_tipo, use_container_width=True)
        
        with col2:
            # Distribuição por status operacional
            df_status = df_componentes_filtrado.groupby('Status_Operacional').size().reset_index(name='Contagem')
            fig_status = px.pie(
                df_status,
                values='Contagem',
                names='Status_Operacional',
                title='Distribuição por Status Operacional',
                hole=0.4
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        # Gráfico de precisão
        fig_precisao = criar_grafico_precisao_componentes(df_componentes_filtrado)
        st.plotly_chart(fig_precisao, use_container_width=True)
        
        # Tabela de componentes
        st.subheader("Lista de Componentes")
        
        colunas_exibir = ['ID_Componente', 'Tipo_Componente', 'Localizacao', 'Status_Operacional',
                         'Incidentes_Detectados', 'Falsos_Positivos', 'Taxa_Precisao',
                         'Ultima_Manutencao', 'Proxima_Manutencao']
        
        st.dataframe(
            df_componentes_filtrado[colunas_exibir].sort_values(['Taxa_Precisao'], ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Análise de falsos positivos vs falsos negativos
        st.subheader("Relação entre Falsos Positivos e Falsos Negativos")
        
        fig_falsos = px.scatter(
            df_componentes_filtrado,
            x='Falsos_Positivos',
            y='Falsos_Negativos',
            color='Tipo_Componente',
            size='Incidentes_Detectados',
            hover_name='ID_Componente',
            hover_data=['Localizacao', 'Status_Operacional', 'Taxa_Precisao'],
            title='Falsos Positivos vs. Falsos Negativos por Componente',
            labels={
                'Falsos_Positivos': 'Falsos Positivos',
                'Falsos_Negativos': 'Falsos Negativos',
                'Tipo_Componente': 'Tipo de Componente'
            }
        )
        
        fig_falsos.update_layout(height=500)
        st.plotly_chart(fig_falsos, use_container_width=True)
    
    elif pagina == "Análise Financeira":
        st.title("Análise Financeira e ROI")
        
        # Filtros específicos para esta página
        categorias_metricas = df_metricas['Categoria_Risco'].unique().tolist()
        categorias_selecionadas = st.multiselect(
            "Categorias de Risco",
            options=categorias_metricas,
            default=categorias_metricas
        )
        
        # Aplicar filtros
        if categorias_selecionadas:
            df_metricas_filtrado = df_metricas[df_metricas['Categoria_Risco'].isin(categorias_selecionadas)]
        else:
            df_metricas_filtrado = df_metricas
        
        # KPIs financeiros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            valor_total_perdas = df_metricas_filtrado['Valor_Total_Perdas'].sum()
            st.metric("Valor Total de Perdas", f"R$ {valor_total_perdas:,.2f}")
        
        with col2:
            custo_total_mitigacao = df_metricas_filtrado['Custo_Mitigacao'].sum()
            st.metric("Custo Total de Mitigação", f"R$ {custo_total_mitigacao:,.2f}")
        
        with col3:
            roi_medio = df_metricas_filtrado['ROI_Seguranca'].mean()
            st.metric("ROI Médio de Segurança", f"{roi_medio:.1f}%")
        
        # Gráficos financeiros
        col1, col2 = st.columns(2)
        
        with col1:
            # Evolução de perdas por categoria
            df_perdas_tempo = df_metricas_filtrado.pivot_table(
                index='Mes_Ano',
                columns='Categoria_Risco',
                values='Valor_Total_Perdas',
                aggfunc='sum'
            ).reset_index()
            
            fig_perdas_tempo = px.line(
                df_perdas_tempo.melt(id_vars=['Mes_Ano'], var_name='Categoria_Risco', value_name='Valor'),
                x='Mes_Ano',
                y='Valor',
                color='Categoria_Risco',
                markers=True,
                title='Evolução de Perdas por Categoria',
                labels={'Mes_Ano': 'Mês/Ano', 'Valor': 'Valor Total de Perdas (R$)'}
            )
            
            st.plotly_chart(fig_perdas_tempo, use_container_width=True)
        
        with col2:
            # Gráfico de ROI
            fig_roi = criar_grafico_roi(df_metricas_filtrado)
            st.plotly_chart(fig_roi, use_container_width=True)
        
        # Análise de custo-benefício
        st.subheader("Análise de Custo-Benefício por Categoria")
        
        df_custo_beneficio = df_metricas_filtrado.groupby('Categoria_Risco').agg({
            'Valor_Total_Perdas': 'sum',
            'Custo_Mitigacao': 'sum',
            'ROI_Seguranca': 'mean'
        }).reset_index()
        
        df_custo_beneficio['Razao_Custo_Beneficio'] = df_custo_beneficio['Valor_Total_Perdas'] / df_custo_beneficio['Custo_Mitigacao']
        
        fig_cb = px.bar(
            df_custo_beneficio,
            x='Categoria_Risco',
            y='Razao_Custo_Beneficio',
            color='Categoria_Risco',
            title='Razão Custo-Benefício por Categoria (Perdas Evitadas / Custo de Mitigação)',
            labels={'Categoria_Risco': 'Categoria de Risco', 'Razao_Custo_Beneficio': 'Razão Custo-Benefício'}
        )
        
        st.plotly_chart(fig_cb, use_container_width=True)
        
        # Tabela de métricas financeiras
        st.subheader("Métricas Financeiras por Mês")
        
        df_metricas_mes = df_metricas_filtrado.groupby('Mes_Ano').agg({
            'Valor_Total_Perdas': 'sum',
            'Custo_Mitigacao': 'sum',
            'ROI_Seguranca': 'mean',
            'Numero_Incidentes': 'sum'
        }).reset_index()
        
        df_metricas_mes['Custo_Medio_Incidente'] = df_metricas_mes['Valor_Total_Perdas'] / df_metricas_mes['Numero_Incidentes']
        
        colunas_exibir = ['Mes_Ano', 'Numero_Incidentes', 'Valor_Total_Perdas', 
                         'Custo_Medio_Incidente', 'Custo_Mitigacao', 'ROI_Seguranca']
        
        st.dataframe(
            df_metricas_mes[colunas_exibir].sort_values('Mes_Ano'),
            use_container_width=True,
            hide_index=True
        )
        
        # Projeção de economia
        st.subheader("Projeção de Economia Anual")
        
        # Calcular tendência de redução de perdas
        df_tendencia = df_metricas_filtrado.groupby('Mes_Ano')['Valor_Total_Perdas'].sum().reset_index()
        df_tendencia['Mes_Ano'] = pd.to_datetime(df_tendencia['Mes_Ano'] + '-01')
        df_tendencia = df_tendencia.sort_values('Mes_Ano')
        
        # Calcular média dos primeiros 3 meses vs últimos 3 meses
        if len(df_tendencia) >= 6:
            primeiros_meses = df_tendencia['Valor_Total_Perdas'].iloc[:3].mean()
            ultimos_meses = df_tendencia['Valor_Total_Perdas'].iloc[-3:].mean()
            reducao_percentual = (primeiros_meses - ultimos_meses) / primeiros_meses * 100
            economia_anual = (primeiros_meses - ultimos_meses) * 12
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Redução Percentual de Perdas", f"{reducao_percentual:.1f}%")
            
            with col2:
                st.metric("Economia Anual Projetada", f"R$ {economia_anual:,.2f}")
        
        # Gráfico de projeção
        fig_projecao = go.Figure()
        
        # Dados históricos
        fig_projecao.add_trace(go.Scatter(
            x=df_tendencia['Mes_Ano'],
            y=df_tendencia['Valor_Total_Perdas'],
            mode='lines+markers',
            name='Dados Históricos',
            line=dict(color='blue')
        ))
        
        # Linha de tendência (regressão linear simples)
        if len(df_tendencia) >= 3:
            x = np.arange(len(df_tendencia))
            y = df_tendencia['Valor_Total_Perdas'].values
            
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            
            # Projetar 6 meses à frente
            x_proj = np.arange(len(df_tendencia) + 6)
            y_proj = p(x_proj)
            
            # Criar datas para projeção
            ultima_data = df_tendencia['Mes_Ano'].iloc[-1]
            datas_proj = [ultima_data + pd.DateOffset(months=i) for i in range(-len(df_tendencia)+1, 7)]
            
            fig_projecao.add_trace(go.Scatter(
                x=datas_proj,
                y=y_proj,
                mode='lines',
                name='Tendência e Projeção',
                line=dict(color='red', dash='dash')
            ))
        
        fig_projecao.update_layout(
            title='Tendência de Perdas e Projeção Futura',
            xaxis_title='Mês/Ano',
            yaxis_title='Valor Total de Perdas (R$)',
            height=500
        )
        
        st.plotly_chart(fig_projecao, use_container_width=True)

# Executar a aplicação
if __name__ == "__main__":
    main()
