import os
import re
import shutil
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy.interpolate import griddata
from scipy.signal import find_peaks
import tkinter as tk
from tkinter import filedialog, messagebox
import plotly.io as pio
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
from matplotlib.colors import ListedColormap
from tkinter import filedialog, messagebox, ttk
import matplotlib.cm as cm
import math


def organizar_arquivos_por_padrao(pasta: str) -> None:
    """
    Organiza arquivos em subpastas conforme padrões definidos no nome do arquivo.

    Args:
        pasta (str): Caminho da pasta a ser organizada. Os arquivos serão movidos para subpastas conforme o padrão de nome.

    Exemplo:
        organizar_arquivos_por_padrao('Caminho/para/pasta')
    """
    try:
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
    except Exception as e:
        print(f'Erro ao organizar arquivos: {e}')
        raise


def extrair_coordenadas_e_valores_espd(pasta: str, salvar_csv: bool = False) -> pd.DataFrame:
    """
    Extrai coordenadas e valores dos arquivos ESPD_XX* de uma pasta, incluindo PFD e PPFD.
    Faz merge com o arquivo coordenadas.csv, se existir, para obter as coordenadas reais.

    Args:
        pasta (str): Caminho da pasta a ser analisada.
        salvar_csv (bool, opcional): Se True, salva o DataFrame resultante como 'df_all_files_X.csv' na pasta, onde X é a terminação dos arquivos. Padrão é False.

    Returns:
        pd.DataFrame: DataFrame com as colunas extraídas dos arquivos e coordenadas reais (se disponíveis).

    Exemplo:
        df = extrair_coordenadas_e_valores_espd('Caminho/para/pasta', salvar_csv=True)
    """
    try:
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
        terminacao_encontrada = None
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
                if terminacao and not terminacao_encontrada:
                    terminacao_encontrada = terminacao
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
            df = df.rename(
                columns={'linha': 'X', 'coluna': 'Y', 'X': 'linha', 'Y': 'coluna'})

        if salvar_csv and terminacao_encontrada:
            nome_csv = f"df_all_files_{terminacao_encontrada}.csv"
            caminho_csv = os.path.join(pasta, nome_csv)
            if os.path.exists(caminho_csv):
                os.remove(caminho_csv)
            df.to_csv(caminho_csv, index=False)
        elif salvar_csv:
            caminho_csv = os.path.join(pasta, "df_all_files.csv")
            if os.path.exists(caminho_csv):
                os.remove(caminho_csv)
            df.to_csv(caminho_csv, index=False)
        return df
    except Exception as e:
        print(f'Erro ao extrair coordenadas e valores: {e}')
        raise


def plotar_3d_ppfd(df: pd.DataFrame, usar_ppfd: bool = True) -> None:
    """
    Plota um gráfico 3D de pontos usando Plotly, com linha (X), coluna (Y) e PPFD ou PFD (Z).

    Args:
        df (pd.DataFrame): DataFrame com colunas 'linha', 'coluna', 'PPFD', 'PFD'.
        usar_ppfd (bool, opcional): Se True, plota PPFD; se False, plota PFD. Padrão é True.

    Exemplo:
        plotar_3d_ppfd(df, usar_ppfd=True)
    """
    try:
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

        axis_style = dict(
            showbackground=True,
            showgrid=True,
            zeroline=True,
            showticklabels=True,
            title=''
        )

        fig.update_layout(
            scene=dict(
                xaxis_title='Linha (X)',
                yaxis_title='Coluna (Y)',
                zaxis_title=z_label
            ),
            title=f'Distribuição 3D de {z_label}',
            font=dict(family='Segoe UI, Segoe, Arial', size=14),
            template='plotly_white',
            hovermode='closest',
        )

        fig.update_layout(scene_camera_eye=dict(x=2, y=-2, z=2.0))

        fig.show()
    except Exception as e:
        print(f'Erro ao plotar gráfico 3D de pontos: {e}')
        raise


def plotar_surface_ppfd(df: pd.DataFrame, usar_ppfd: bool = True, interpolar: str = 'cubic') -> None:
    """
    Plota um gráfico Surface 3D interpolado com contornos usando Plotly.
    Permite escolher entre PPFD ou PFD via argumento.
    O argumento 'interpolar' define o método de interpolação do griddata ('cubic', 'linear', 'nearest').

    Args:
        df (pd.DataFrame): DataFrame com colunas 'linha', 'coluna', 'PPFD', 'PFD'.
        usar_ppfd (bool, opcional): Se True, plota PPFD; se False, plota PFD. Padrão é True.
        interpolar (str, opcional): Método de interpolação. Padrão é 'cubic'.

    Exemplo:
        plotar_surface_ppfd(df, usar_ppfd=False, interpolar='linear')
    """
    try:
        z_col = 'PPFD' if usar_ppfd else 'PFD'
        z_label = 'PPFD (umol m⁻² s⁻¹)' if usar_ppfd else 'PFD (umol m⁻² s⁻¹)'

        x = df['linha']
        y = df['coluna']
        z = df[z_col]

        xi = np.linspace(x.min(), x.max(), 50)
        yi = np.linspace(y.min(), y.max(), 50)
        xi, yi = np.meshgrid(xi, yi)
        zi = griddata((x, y), z, (xi, yi), method=interpolar)

        axis_style = dict(
            showbackground=False,
            showgrid=True,
            zeroline=True,
            showticklabels=True,
            title=''
        )

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

        fig.update_layout(
            scene=dict(
                xaxis_title='Linha (X)',
                yaxis_title='Coluna (Y)',
                zaxis_title=z_label
            ),
            title=f'Surface Plot 3D Interpolado de {z_label} ({interpolar})',
            font=dict(family='Segoe UI, Segoe, Arial', size=14),
            template='plotly_white',
            hovermode='closest',
        )

        fig.update_layout(scene_camera_eye=dict(x=2, y=-2, z=0.7))

        fig.show()
    except Exception as e:
        print(f'Erro ao plotar superfície: {e}')
        raise


def plotar_multiple_surface_ppfd(dfs: list, nomes: list, usar_ppfd: bool = True, interpolar: str = 'cubic') -> None:
    """
    Plota múltiplas superfícies 3D interpoladas de PPFD ou PFD em um único gráfico Plotly.
    Permite seleção dinâmica dos grupos (superfícies) via checkboxes na página HTML, igual à função plot_spectral.
    """
    try:
        # Paletas de degradê personalizadas conforme solicitado
        cores_por_nome = {
            '99100': [[0, 'rgb(120,81,169)'], [1, 'rgb(186,104,200)']],
            '0T':    [[0, 'rgb(103,58,183)'], [1, 'rgb(179,136,255)']],
            '100B':  [[0, 'rgb(80,80,80)'], [1, 'rgb(220,220,220)']],
            '0B':    [[0, 'rgb(120,120,120)'], [1, 'rgb(240,240,240)']],
            '100V':  [[0, 'rgb(183,28,28)'], [1, 'rgb(255,138,128)']],
            '0V':    [[0, 'rgb(229,57,53)'], [1, 'rgb(255,205,210)']],
            '100A':  [[0, 'rgb(13,71,161)'], [1, 'rgb(100,181,246)']],
            '0A':    [[0, 'rgb(21,101,192)'], [1, 'rgb(144,202,249)']]
        }
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

        def nome_legenda_grupo(nome):
            for chave, valor in nomes_legenda.items():
                if chave in nome:
                    return valor
            return nome
        z_col = 'PPFD' if usar_ppfd else 'PFD'
        z_label = 'PPFD (umol m⁻² s⁻¹)' if usar_ppfd else 'PFD (umol m⁻² s⁻¹)'
        fig = go.Figure()
        grupos_legenda = []
        for idx, (df, nome) in enumerate(zip(dfs, nomes)):
            x = df['linha']
            y = df['coluna']
            z = df[z_col]
            xi = np.linspace(x.min(), x.max(), 50)
            yi = np.linspace(y.min(), y.max(), 50)
            xi, yi = np.meshgrid(xi, yi)
            zi = griddata((x, y), z, (xi, yi), method=interpolar)
            nome_leg = nome_legenda_grupo(nome)
            grupos_legenda.append(nome_leg)
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
                name=nome_leg,
                legendgroup=nome_leg,
                opacity=0.8,
                showscale=(idx == 0),
                hovertemplate=f"{nome_leg}<br>Linha (Y): %{{y}}<br>Coluna (X): %{{x}}<br>{z_label}: %{{z:.2f}}<extra></extra>",
                visible=True
            ))
        fig.update_layout(
            scene=dict(
                xaxis_title='Linha (X)',
                yaxis_title='Coluna (Y)',
                zaxis_title=z_label,
                camera_eye=dict(x=2, y=-2, z=0.7)
            ),
            title='',
            legend_title_text='Grupo',
            font=dict(family='Segoe UI, Segoe, Arial', size=14),
            template='plotly_white',
            hovermode='closest',
            uirevision='manter_rotacao',
        )
        # Gera HTML com checkboxes para grupos (usando nomes amigáveis) - lista horizontal acima do gráfico
        grupos_ordenados = sorted(set(grupos_legenda))
        checkboxes = "".join([
            f'<label style="margin-right:18px;font-family:Segoe UI,Segoe,Arial;font-size:15px;"><input type="checkbox" class="grupo-cb" value="{g}" checked> {g}</label>'
            for g in grupos_ordenados
        ])
        js = '''<script>
        function updateGroups() {
            var checked = Array.from(document.querySelectorAll('.grupo-cb:checked')).map(cb => cb.value);
            var plot = document.querySelector('.js-plotly-plot');
            var update = {visible: []};
            var data = plot.data;
            for (var i = 0; i < data.length; i++) {
                var grupo = data[i].legendgroup;
                update.visible.push(checked.includes(grupo));
            }
            Plotly.update(plot, update, {});
        }
        document.querySelectorAll('.grupo-cb').forEach(cb => cb.addEventListener('change', updateGroups));
        </script>'''

        html = pio.to_html(fig, include_plotlyjs='cdn',
                           full_html=False, config={"displayModeBar": True})
        html_final = f"""
        <html><head><meta charset='utf-8'><title>Múltiplas Superfícies 3D</title></head><body style='font-family:Segoe UI,Segoe,Arial;'>
        <h2 style='font-family:Segoe UI,Segoe,Arial;'>Múltiplas Superfícies 3D Interpoladas ({interpolar})</h2>
        <div style='margin-bottom:12px;'>{checkboxes}</div>
        {html}
        {js}
        </body></html>
        """

        saida = os.path.join(os.getcwd(), "multiplas_surfaces_interativo.html")
        with open(saida, 'w', encoding='utf-8') as f:
            f.write(html_final)
        webbrowser.open('file://' + os.path.abspath(saida))
    except Exception as e:
        print(f'Erro ao plotar múltiplas superfícies: {e}')
        raise


def plot_spectral():
    """
    Permite ao usuário selecionar uma pasta principal, busca recursivamente todos os arquivos uMOL_*.txt nas subpastas,
    plota todas as curvas em um único gráfico interativo com Plotly, e permite selecionar quais subpastas visualizar via checkboxes na própria página HTML.
    """

    root = tk.Tk()
    root.withdraw()
    pasta_principal = filedialog.askdirectory(
        title="Selecione a pasta principal com subpastas contendo arquivos uMOL_*")
    if not pasta_principal:
        messagebox.showwarning("Aviso", "Nenhuma pasta selecionada.")
        return
    arquivos_umol = []
    grupos = []
    for dirpath, _, filenames in os.walk(pasta_principal):
        subpasta = os.path.relpath(dirpath, pasta_principal)
        if subpasta == ".":
            continue
        for f in filenames:
            if f.startswith('uMOL_') and f.endswith('.txt'):
                arquivos_umol.append(os.path.join(dirpath, f))
                grupos.append(subpasta)
    if not arquivos_umol:
        messagebox.showwarning(
            "Aviso", "Nenhum arquivo uMOL_*.txt encontrado nas subpastas.")
        return
    # Mapeamento dos nomes para exibição amigável
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
    fig = go.Figure()
    grupo_set = set()
    grupo_legenda_map = {}
    for arquivo, grupo in zip(arquivos_umol, grupos):
        try:
            try:
                df = pd.read_csv(arquivo, sep=r'\t|\s+',
                                 engine='python', comment='#')
            except pd.errors.ParserError:
                messagebox.showwarning(
                    "Aviso", f"O arquivo {os.path.basename(arquivo)} não pôde ser lido como CSV padrão (tab ou espaço).")
                continue
            if 'Wavelength(nm)' not in df.columns or not any('PFD' in col and 'umol' in col for col in df.columns):
                messagebox.showwarning(
                    "Aviso", f"O arquivo {os.path.basename(arquivo)} não segue o padrão esperado de colunas ('Wavelength(nm)' e 'PFD ... umol').")
                continue
            col_wave = 'Wavelength(nm)'
            col_pfd = None
            for col in df.columns:
                if 'PFD' in col and 'umol' in col:
                    col_pfd = col
            if col_wave not in df.columns or col_pfd is None:
                continue
            x = df[col_wave].values
            y = df[col_pfd].values
            if len(x) == 0 or len(y) == 0:
                continue
            nome_legenda = nomes_legenda.get(grupo, grupo)
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=f"{nome_legenda}", legendgroup=nome_legenda, visible=True,
                                     customdata=[[nome_legenda]]*len(x),
                                     hovertemplate=f"Grupo: {nome_legenda}<br>Arquivo: {os.path.basename(arquivo)}<br>Wavelength: %{{x}}<br>PFD: %{{y}}<extra></extra>"))
            # Detecção de picos usando scipy.signal.find_peaks
            try:
                peaks, _ = find_peaks(y, prominence=0.05 * np.max(y))
                if len(peaks) > 0:
                    fig.add_trace(go.Scatter(
                        x=x[peaks], y=y[peaks],
                        mode='markers',
                        marker=dict(symbol='x', size=10, color='red'),
                        name=f"Picos {nome_legenda}",
                        legendgroup=nome_legenda,
                        showlegend=False,
                        hovertemplate=f"<b>Pico</b><br>Grupo: {nome_legenda}<br>Arquivo: {os.path.basename(arquivo)}<br>Wavelength: %{{x}}<br>PFD: %{{y}}<extra></extra>"
                    ))
            except Exception as e:
                print(f"Erro ao detectar picos em {arquivo}: {e}")
            grupo_set.add(grupo)
            grupo_legenda_map[grupo] = nome_legenda
        except Exception as e:
            print(f'Erro ao ler {arquivo}: {e}')
    fig.update_layout(
        title='',
        xaxis_title='Wavelength (nm)',
        yaxis_title='PFD (μmol m⁻² s⁻¹)',
        hovermode='closest',
        template='plotly_white',
        legend_title_text='Grupo',
        font=dict(family='Segoe UI, Segoe, Arial', size=14)
    )
    # Gera HTML com checkboxes para grupos (usando nomes amigáveis) - agora acima do gráfico, em linha
    grupos_ordenados = sorted(grupo_set, key=lambda g: nomes_legenda.get(g, g))
    checkboxes = "".join([
        f'<label style="margin-right:18px;font-family:Segoe UI,Segoe,Arial;font-size:15px;"><input type="checkbox" class="grupo-cb" value="{nomes_legenda.get(g, g)}" checked> {nomes_legenda.get(g, g)}</label>'
        for g in grupos_ordenados
    ])
    js = '''<script>
    function updateGroups() {
        var checked = Array.from(document.querySelectorAll('.grupo-cb:checked')).map(cb => cb.value);
        var plot = document.querySelector('.js-plotly-plot');
        var update = {visible: []};
        var data = plot.data;
        for (var i = 0; i < data.length; i++) {
            var grupo = data[i].legendgroup;
            update.visible.push(checked.includes(grupo));
        }
        Plotly.update(plot, update, {});
    }
    document.querySelectorAll('.grupo-cb').forEach(cb => cb.addEventListener('change', updateGroups));
    </script>'''
    html = pio.to_html(fig, include_plotlyjs='cdn',
                       full_html=False, config={"displayModeBar": True})
    html_final = f"""
    <html><head><meta charset='utf-8'><title>Espectros uMOL_ por grupo</title></head><body style='font-family:Segoe UI,Segoe,Arial;'>
    <h2 style='font-family:Segoe UI,Segoe,Arial;'>Espectros de arquivos uMOL</h2>
    <div style='margin-bottom:12px;'>{checkboxes}</div>
    {html}
    {js}
    </body></html>
    """
    saida = os.path.join(pasta_principal, "espectros_umol_interativo.html")
    with open(saida, 'w', encoding='utf-8') as f:
        f.write(html_final)
    webbrowser.open('file://' + os.path.abspath(saida))


def plot_spectral_matplotlib():
    """
    Plota todos os espectros uMOL_ encontrados nas subpastas, usando matplotlib,
    com linhas multicoloridas conforme o comprimento de onda (Wavelength),
    exibindo todos os grupos em subplots (painéis) em uma única janela.
    Não exibe colorbar. O label do eixo Y aparece apenas na primeira coluna, e o do eixo X apenas na última linha.
    O eixo X vai de 380 a 780 nm, com marcação a cada 50 nm.
    As cores seguem o degradê espectral solicitado.
    Layout ajustado conforme solicitado.
    Se o usuário selecionar uma subpasta (sem subpastas), plota um único gráfico com todos os arquivos dessa subpasta.
    """

    # Função para mapear comprimento de onda para cor RGB com degradê suave entre as faixas
    def wavelength_to_rgb(wavelength):
        color_points = [
            (380, (0.56, 0.0, 1.0)),    # Violeta
            (440, (0.0, 0.3, 1.0)),     # Azul
            (485, (0.0, 0.8, 0.8)),     # Ciano
            (500, (0.0, 0.7, 0.2)),     # Verde
            (565, (1.0, 0.85, 0.0)),    # Amarelo
            (590, (1.0, 0.5, 0.0)),     # Laranja
            (625, (1.0, 0.0, 0.0)),     # Vermelho
            (700, (0.7, 0.0, 0.0)),     # Vermelho distante
            (780, (0.5, 0.0, 0.0)),     # Fim do espectro visível
        ]
        if wavelength < 380:
            return (0.6, 0.6, 0.7)  # UVA
        if wavelength > 780:
            return (0.5, 0.5, 0.5)
        for i in range(len(color_points) - 1):
            wl0, c0 = color_points[i]
            wl1, c1 = color_points[i + 1]
            if wl0 <= wavelength <= wl1:
                t = (wavelength - wl0) / (wl1 - wl0)
                r = c0[0] + (c1[0] - c0[0]) * t
                g = c0[1] + (c1[1] - c0[1]) * t
                b = c0[2] + (c1[2] - c0[2]) * t
                return (r, g, b)
        return (0.5, 0.5, 0.5)

    root = tk.Tk()
    root.withdraw()
    pasta_principal = filedialog.askdirectory(
        title="Selecione a pasta principal com subpastas contendo arquivos uMOL_*")
    if not pasta_principal:
        messagebox.showwarning("Aviso", "Nenhuma pasta selecionada.")
        return

    # Verifica se a pasta selecionada possui subpastas
    subpastas = [d for d in os.listdir(pasta_principal)
                 if os.path.isdir(os.path.join(pasta_principal, d))]
    arquivos_umol = []
    grupos = []

    if subpastas:
        # Caso pasta principal com subpastas: busca recursiva
        for dirpath, _, filenames in os.walk(pasta_principal):
            subpasta = os.path.relpath(dirpath, pasta_principal)
            if subpasta == ".":
                continue
            for f in filenames:
                if f.startswith('uMOL_') and f.endswith('.txt'):
                    arquivos_umol.append(os.path.join(dirpath, f))
                    grupos.append(subpasta)
    else:
        # Caso subpasta (sem subpastas): busca apenas nesta pasta
        for f in os.listdir(pasta_principal):
            if f.startswith('uMOL_') and f.endswith('.txt'):
                arquivos_umol.append(os.path.join(pasta_principal, f))
                grupos.append("Selecionada")

    if not arquivos_umol:
        messagebox.showwarning(
            "Aviso", "Nenhum arquivo uMOL_*.txt encontrado.")
        return

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

    # Agrupa arquivos por grupo
    grupos_dict = {}
    for arquivo, grupo in zip(arquivos_umol, grupos):
        if grupo not in grupos_dict:
            grupos_dict[grupo] = []
        grupos_dict[grupo].append(arquivo)

    if not grupos_dict:
        messagebox.showwarning("Aviso", "Nenhum grupo encontrado.")
        return

    grupos_lista = list(grupos_dict.keys())
    n_grupos = len(grupos_lista)

    # Se for só um grupo (caso subpasta), plota um único gráfico
    if n_grupos == 1:
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        arquivos = grupos_dict[grupos_lista[0]]
        for arquivo in arquivos:
            try:
                df = pd.read_csv(arquivo, sep=r'\t|\s+',
                                 engine='python', comment='#')
                if 'Wavelength(nm)' not in df.columns or not any('PFD' in col and 'umol' in col for col in df.columns):
                    continue
                col_wave = 'Wavelength(nm)'
                col_pfd = None
                for col in df.columns:
                    if 'PFD' in col and 'umol' in col:
                        col_pfd = col
                if col_wave not in df.columns or col_pfd is None:
                    continue
                x = df[col_wave].values
                y = df[col_pfd].values
                if len(x) < 2 or len(y) < 2:
                    continue
                points = np.array([x, y]).T.reshape((-1, 1, 2))
                segments = np.concatenate([points[:-1], points[1:]], axis=1)
                colors = [wavelength_to_rgb(wl) for wl in x[:-1]]
                lc = LineCollection(segments, colors=colors, linewidth=2)
                ax.add_collection(lc)
            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")
        ax.set_xlim(380, 780)
        # Limites de Y personalizados conforme os dados do grupo
        y_min, y_max = None, None
        for arquivo in arquivos:
            try:
                df = pd.read_csv(arquivo, sep=r'\t|\s+',
                                 engine='python', comment='#')
                col_pfd = None
                for col in df.columns:
                    if 'PFD' in col and 'umol' in col:
                        col_pfd = col
                if col_pfd is None:
                    continue
                y = df[col_pfd].values
                if len(y) < 2:
                    continue
                ymin, ymax = np.nanmin(y), np.nanmax(y)
                if y_min is None or ymin < y_min:
                    y_min = ymin
                if y_max is None or ymax > y_max:
                    y_max = ymax
            except Exception:
                continue
        if y_min is not None and y_max is not None and y_max > y_min:
            ax.set_ylim(y_min - 0.05*(y_max-y_min),
                        y_max + 0.05*(y_max-y_min))
        xticks = np.arange(380, 781, 50)
        ax.set_xticks(xticks)
        ax.set_ylabel("PFD (μmol m⁻² s⁻¹)", fontsize=12)
        ax.set_xlabel("Wavelength, λ (nm)", fontsize=12)
        titulo = grupos_lista[0]
        if titulo in nomes_legenda:
            titulo = nomes_legenda[titulo]
        elif titulo == "Selecionada":
            titulo = "Arquivos da pasta selecionada"
        ax.set_title(f"Grupo: {titulo}", fontsize=13)
        ax.grid(True, alpha=0.3)
        fig.subplots_adjust(left=0.10, top=0.93, right=0.98,
                            wspace=0.15, hspace=0.350, bottom=0.13)
        plt.show()
        plt.ioff()
        return

    # Caso múltiplos grupos (pasta principal com subpastas)
    ncols = min(3, n_grupos)
    nrows = math.ceil(n_grupos / ncols)
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols,
                            figsize=(7*ncols, 4*nrows), dpi=100)
    if n_grupos == 1:
        axs = np.array([[axs]])
    elif n_grupos > 1 and nrows == 1:
        axs = np.array([axs])
    axs = axs.flatten()
    xticks = np.arange(380, 781, 50)

    for idx, grupo in enumerate(grupos_lista):
        ax = axs[idx]
        arquivos = grupos_dict[grupo]
        for arquivo in arquivos:
            try:
                df = pd.read_csv(arquivo, sep=r'\t|\s+',
                                 engine='python', comment='#')
                if 'Wavelength(nm)' not in df.columns or not any('PFD' in col and 'umol' in col for col in df.columns):
                    continue
                col_wave = 'Wavelength(nm)'
                col_pfd = None
                for col in df.columns:
                    if 'PFD' in col and 'umol' in col:
                        col_pfd = col
                if col_wave not in df.columns or col_pfd is None:
                    continue
                x = df[col_wave].values
                y = df[col_pfd].values
                if len(x) < 2 or len(y) < 2:
                    continue
                points = np.array([x, y]).T.reshape((-1, 1, 2))
                segments = np.concatenate([points[:-1], points[1:]], axis=1)
                colors = [wavelength_to_rgb(wl) for wl in x[:-1]]
                lc = LineCollection(segments, colors=colors, linewidth=2)
                ax.add_collection(lc)
            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")
        ax.set_xlim(380, 780)
        # Limites de Y personalizados conforme os dados do grupo
        if arquivos:
            y_min, y_max = None, None
            for arquivo in arquivos:
                try:
                    df = pd.read_csv(arquivo, sep=r'\t|\s+',
                                     engine='python', comment='#')
                    if 'Wavelength(nm)' not in df.columns or not any('PFD' in col and 'umol' in col for col in df.columns):
                        continue
                    col_pfd = None
                    for col in df.columns:
                        if 'PFD' in col and 'umol' in col:
                            col_pfd = col
                    if col_pfd is None:
                        continue
                    y = df[col_pfd].values
                    if len(y) < 2:
                        continue
                    ymin, ymax = np.nanmin(y), np.nanmax(y)
                    if y_min is None or ymin < y_min:
                        y_min = ymin
                    if y_max is None or ymax > y_max:
                        y_max = ymax
                except Exception:
                    continue
            if y_min is not None and y_max is not None and y_max > y_min:
                ax.set_ylim(y_min - 0.05*(y_max-y_min),
                            y_max + 0.05*(y_max-y_min))
        ax.set_xticks(xticks)
        # Label do eixo Y apenas na primeira coluna
        if idx % ncols == 0:
            ax.set_ylabel("PFD (μmol m⁻² s⁻¹)", fontsize=12)
        else:
            ax.set_ylabel("")
        # Label do eixo X apenas na última linha
        if idx // ncols == nrows - 1:
            ax.set_xlabel("Wavelength, λ (nm)", fontsize=12)
        else:
            ax.set_xlabel("")
        ax.set_title(f"Grupo: {nomes_legenda.get(grupo, grupo)}", fontsize=12)
        ax.grid(True, alpha=0.3)

    # Remove subplots vazios
    for j in range(idx+1, len(axs)):
        fig.delaxes(axs[j])
    fig.subplots_adjust(left=0.060, top=0.95, right=0.975,
                        wspace=0.15, hspace=0.350, bottom=0.08)
    plt.show()
    plt.ioff()
