import os
import re
import shutil
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy.interpolate import griddata
import tkinter as tk
from tkinter import filedialog, messagebox
import plotly.io as pio
import webbrowser


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
                df = pd.read_csv(arquivo, sep='\t|\s+',
                                 engine='python', comment='#')
            except Exception as e:
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
    import webbrowser
    webbrowser.open('file://' + os.path.abspath(saida))
