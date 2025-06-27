import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy.interpolate import griddata


def organizar_arquivos_por_padrao(pasta: str) -> None:
    """
    Organiza arquivos em subpastas conforme padrões definidos no nome do arquivo.

    Args:
        pasta (str): Caminho da pasta a ser organizada. Os arquivos serão movidos para subpastas conforme o padrão de nome.

    Exemplo:
        organizar_arquivos_por_padrao('Caminho/para/pasta')
    """
    padroes = {
        '100A': r'.*100A\..*$',
        '100V': r'.*100V\..*$',
        '100B': r'.*100B\..*$',
        '0A': r'.*0A\..*$',
        '0B': r'.*0B\..*$',
        '0V': r'.*0V\..*$',
        '0T': r'.*0T\..*$',
        '99100': r'.*99100\..*$'
    }

    # Cria subpastas se não existirem
    for subpasta in padroes.keys():
        os.makedirs(os.path.join(pasta, subpasta), exist_ok=True)

    # Organiza os arquivos
    for arquivo in os.listdir(pasta):
        caminho_arquivo = os.path.join(pasta, arquivo)
        if os.path.isfile(caminho_arquivo):
            for subpasta, padrao in padroes.items():
                if re.match(padrao, arquivo):
                    destino = os.path.join(pasta, subpasta, arquivo)
                    shutil.move(caminho_arquivo, destino)
                    print(f'Movido: {arquivo} -> {subpasta}')
                    break

    print('Organização concluída!')


def extrair_coordenadas_e_valores_espd(pasta: str, salvar_csv: bool = False) -> pd.DataFrame:
    """
    Extrai coordenadas e valores dos arquivos ESPD_XX* de uma pasta, incluindo PFD e PPFD.
    Faz merge com o arquivo coordenadas.csv, se existir, para obter as coordenadas reais.

    Args:
        pasta (str): Caminho da pasta a ser analisada.
        salvar_csv (bool, opcional): Se True, salva o DataFrame resultante como 'coordenadas_espd.csv' na pasta. Padrão é False.

    Returns:
        pd.DataFrame: DataFrame com as colunas extraídas dos arquivos e coordenadas reais (se disponíveis).

    Exemplo:
        df = extrair_coordenadas_e_valores_espd('Caminho/para/pasta', salvar_csv=True)
    """
    padrao_nome = re.compile(r'^ESPD_(\d)(\d)')
    padroes_terminacao = {
        '100A': r'.*100A\..*$',
        '100V': r'.*100V\..*$',
        '100B': r'.*100B\..*$',
        '0A': r'.*0A\..*$',
        '0B': r'.*0B\..*$',
        '0V': r'.*0V\..*$',
        '0T': r'.*0T\..*$',
        '99100': r'.*99100\..*$'
    }
    dados = []

    for arquivo in os.listdir(pasta):
        match = padrao_nome.match(arquivo)
        if match:
            x = int(match.group(1))
            y = int(match.group(2))
            pfd = None
            ppfd = None
            terminacao = None
            for nome_terminacao, padrao in padroes_terminacao.items():
                if re.match(padrao, arquivo):
                    terminacao = nome_terminacao
                    break
            with open(os.path.join(pasta, arquivo), encoding='utf-8') as f:
                for linha in f:
                    if linha.startswith('PFD\t') or linha.startswith('PFD '):
                        partes = re.split(r'\s+|\t+', linha.strip())
                        if len(partes) > 1:
                            pfd = float(partes[1].replace(',', '.'))
                    if linha.startswith('PPFD\t') or linha.startswith('PPFD '):
                        partes = re.split(r'\s+|\t+', linha.strip())
                        if len(partes) > 1:
                            ppfd = float(partes[1].replace(',', '.'))
            dados.append({'arquivo': arquivo, 'ID': terminacao, 'linha': x,
                         'coluna': y, 'PFD': pfd, 'PPFD': ppfd})

    df = pd.DataFrame(dados)
    for col in ['linha', 'coluna']:
        if col not in df.columns:
            df[col] = pd.Series(dtype=int)

    # Caminho do coordenadas.csv
    caminho_coordenadas = os.path.join(pasta, '..', 'coordenadas.csv')
    caminho_coordenadas = os.path.abspath(caminho_coordenadas)

    if os.path.exists(caminho_coordenadas):
        df_coord = pd.read_csv(caminho_coordenadas)
        df = pd.merge(df, df_coord[['x', 'y', 'linha', 'coluna']], left_on=[
                      'linha', 'coluna'], right_on=['x', 'y'], how='left')
        df['X'] = df['linha_y']
        df['Y'] = df['coluna_y']
        df = df.drop(columns=['x', 'y', 'linha_y', 'coluna_y'])
        df = df.rename(columns={'linha_x': 'linha', 'coluna_x': 'coluna'})
        # Troca os nomes conforme solicitado
        df = df.rename(
            columns={'linha': 'X', 'coluna': 'Y', 'X': 'linha', 'Y': 'coluna'})

    if salvar_csv:
        df.to_csv(os.path.join(pasta, 'coordenadas_espd.csv'), index=False)
    return df


def plotar_3d_ppfd(df: pd.DataFrame, usar_ppfd: bool = True) -> None:
    """
    Plota um gráfico 3D de pontos usando Plotly, com linha (X), coluna (Y) e PPFD ou PFD (Z).

    Args:
        df (pd.DataFrame): DataFrame com colunas 'linha', 'coluna', 'PPFD', 'PFD'.
        usar_ppfd (bool, opcional): Se True, plota PPFD; se False, plota PFD. Padrão é True.

    Exemplo:
        plotar_3d_ppfd(df, usar_ppfd=True)
    """
    z_col = 'PPFD' if usar_ppfd else 'PFD'
    z_label = 'PPFD (umol m⁻² s⁻¹)' if usar_ppfd else 'PFD (umol m⁻² s⁻¹)'

    fig = go.Figure(data=[go.Scatter3d(
        x=df['linha'],
        y=df['coluna'],
        z=df[z_col],
        mode='markers',
        marker=dict(
            size=6,
            color=df[z_col],
            colorscale='Viridis',
            colorbar=dict(title=z_label),
            opacity=0.8
        )
    )])

    fig.update_layout(
        scene=dict(
            xaxis_title='Linha (X)',
            yaxis_title='Coluna (Y)',
            zaxis_title=z_label
        ),
        title=f'Distribuição 3D de {z_label}'
    )
    fig.show()


def plotar_surface_ppfd(df: pd.DataFrame, usar_ppfd: bool = True) -> None:
    """
    Plota um gráfico Surface 3D interpolado com contornos usando Plotly.
    Inclui botões de Play/Pause para rotação automática.
    Permite escolher entre PPFD ou PFD via argumento.

    Args:
        df (pd.DataFrame): DataFrame com colunas 'linha', 'coluna', 'PPFD', 'PFD'.
        usar_ppfd (bool, opcional): Se True, plota PPFD; se False, plota PFD. Padrão é True.

    Exemplo:
        plotar_surface_ppfd(df, usar_ppfd=False)
    """
    z_col = 'PPFD' if usar_ppfd else 'PFD'
    z_label = 'PPFD (umol m⁻² s⁻¹)' if usar_ppfd else 'PFD (umol m⁻² s⁻¹)'

    x = df['linha']
    y = df['coluna']
    z = df[z_col]

    xi = np.linspace(x.min(), x.max(), 50)
    yi = np.linspace(y.min(), y.max(), 50)
    xi, yi = np.meshgrid(xi, yi)
    zi = griddata((x, y), z, (xi, yi), method='cubic')

    fig = go.Figure(data=[
        go.Surface(
            x=xi,
            y=yi,
            z=zi,
            colorscale='Viridis',
            colorbar=dict(title=z_label),
            contours={
                "z": {"show": True, "usecolormap": True, "highlightcolor": "limegreen", "project_z": True}
            },
            hovertemplate=f"Linha (X): %{{x}}<br>Coluna (Y): %{{y}}<br>{z_label}: %{{z:.2f}}<extra></extra>"
        )
    ])

    axis_style = dict(
        showbackground=False,
        showgrid=True,
        zeroline=True,
        showticklabels=True,
        title=''
    )

    fig.update_layout(
        scene=dict(
            xaxis=axis_style,
            yaxis=axis_style,
            zaxis=axis_style
        ),
        title=f'Surface Plot 3D Interpolado de {z_label}',
        updatemenus=[{
            "type": "buttons",
            "showactive": False,
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True, "transition": {"duration": 0}}]
                },
                {
                    "label": "Pause",
                    "method": "animate",
                    "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]
                }
            ]
        }]
    )

    total_frames = 1200
    frames = []
    for i, angle in enumerate(np.linspace(0, 1080, total_frames)):
        frames.append(go.Frame(layout=dict(
            scene_camera_eye=dict(
                x=2*np.cos(np.radians(angle)), y=2*np.sin(np.radians(angle)), z=0.7)
        )))
    fig.frames = frames

    fig.update_layout(scene_camera_eye=dict(x=2, y=2, z=0.7))

    fig.show()


def plotar_multiple_surface_ppfd(dfs: list, nomes: list, usar_ppfd: bool = True) -> None:
    """
    Plota múltiplas superfícies 3D interpoladas de PPFD ou PFD em um único gráfico Plotly.
    Adiciona uma lista clicável (legenda) para mostrar/ocultar superfícies.
    Permite rotação automática via botão Play/Pause e mantém a rotação/câmera ao interagir.

    Args:
        dfs (list of pd.DataFrame): Lista de DataFrames, um para cada superfície.
        nomes (list of str): Lista de nomes para cada superfície (usado na legenda e hover).
        usar_ppfd (bool, opcional): Se True, plota PPFD; se False, plota PFD. Padrão é True.

    Exemplo:
        plotar_multiple_surface_ppfd([df1, df2], ['Pasta1', 'Pasta2'], usar_ppfd=True)
    """
    fig = go.Figure()
    # Paletas de degradê personalizadas conforme solicitado
    cores_por_nome = {
        # Roxo degradê
        '99100': [[0, 'rgb(120,81,169)'], [1, 'rgb(186,104,200)']],
        # Roxo degradê
        '0T':    [[0, 'rgb(103,58,183)'], [1, 'rgb(179,136,255)']],
        # Cinza degradê
        '100B':  [[0, 'rgb(80,80,80)'], [1, 'rgb(220,220,220)']],
        # Cinza degradê
        '0B':    [[0, 'rgb(120,120,120)'], [1, 'rgb(240,240,240)']],
        # Vermelho degradê
        '100V':  [[0, 'rgb(183,28,28)'], [1, 'rgb(255,138,128)']],
        # Vermelho degradê
        '0V':    [[0, 'rgb(229,57,53)'], [1, 'rgb(255,205,210)']],
        # Azul degradê
        '100A':  [[0, 'rgb(13,71,161)'], [1, 'rgb(100,181,246)']],
        # Azul degradê
        '0A':    [[0, 'rgb(21,101,192)'], [1, 'rgb(144,202,249)']]
    }

    # Mapeamento dos nomes para exibição no hover
    nomes_legenda = {
        '99100': 'RBW100%',
        '0T':    'RBW15%',
        '100V':  'R100%',
        '100B':  'W100%',
        '100A':  'B100%',
        '0V':    'R15%',
        '0B':    'W15%',
        '0A':    'B15%'
    }

    def escolher_cores(nome):
        for chave, cores in cores_por_nome.items():
            if chave in nome:
                return cores
        return [[0, 'rgb(200,200,200)'], [1, 'rgb(80,80,80)']]

    def nome_hover(nome):
        for chave, valor in nomes_legenda.items():
            if chave in nome:
                return valor
        return nome

    z_col = 'PPFD' if usar_ppfd else 'PFD'
    z_label = 'PPFD (umol m⁻² s⁻¹)' if usar_ppfd else 'PFD (umol m⁻² s⁻¹)'

    for idx, (df, nome) in enumerate(zip(dfs, nomes)):
        x = df['linha']
        y = df['coluna']
        z = df[z_col]
        xi = np.linspace(x.min(), x.max(), 50)
        yi = np.linspace(y.min(), y.max(), 50)
        xi, yi = np.meshgrid(xi, yi)
        zi = griddata((x, y), z, (xi, yi), method='cubic')
        nome_legenda = nome_hover(nome)
        fig.add_trace(go.Surface(
            x=xi,
            y=yi,
            z=zi,
            colorscale=escolher_cores(nome),
            colorbar=dict(title=z_label, len=0.5, y=0.75 -
                          0.25*idx) if idx == 0 else None,
            contours={
                "z": {"show": True, "usecolormap": True, "highlightcolor": "limegreen", "project_z": True}
            },
            name=nome_legenda,
            opacity=0.8,
            showscale=(idx == 0),
            hovertemplate=f"{nome_legenda}<br>Linha (Y): %{{y}}<br>Coluna (X): %{{x}}<br>{z_label}: %{{z:.2f}}<extra></extra>",
            visible=True
        ))

    axis_style = dict(
        showbackground=False,
        showgrid=True,
        zeroline=True,
        showticklabels=True,
        title=''
    )

    # Cria frames para rotação automática (60fps, 1 minuto, 3 voltas)
    total_frames = 1200
    frames = []
    for i, angle in enumerate(np.linspace(0, 1080, total_frames)):
        frames.append(go.Frame(layout=dict(
            scene_camera_eye=dict(
                x=2*np.cos(np.radians(angle)), y=2*np.sin(np.radians(angle)), z=0.7)
        )))
    fig.frames = frames

    fig.update_layout(
        scene=dict(
            xaxis=axis_style,
            yaxis=axis_style,
            zaxis=axis_style,
            camera_eye=dict(x=2, y=0, z=0.7)
        ),
        title=f'Múltiplas Superfícies 3D Interpoladas de {z_label}<br><sup>Para rotação automática, clique em Play</sup>',
        legend=dict(
            title="Superfícies",
            itemsizing='constant',
            x=0,
            y=0.5,
            xanchor='left',
            yanchor='middle'
        ),
        uirevision='manter_rotacao',
        updatemenus=[{
            "type": "buttons",
            "showactive": False,
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True, "transition": {"duration": 0}}]
                },
                {
                    "label": "Pause",
                    "method": "animate",
                    "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]
                }
            ]
        }]
    )

    # Ativa a legenda clicável para Surface
    for trace in fig.data:
        trace.showlegend = True
        trace.legendgroup = trace.name

    fig.show()
