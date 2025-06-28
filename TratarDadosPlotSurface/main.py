import functions as fn
import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import sys
import threading


class App(tb.Window):
    def __init__(self):
        # Experimente "flatly", "cosmo", "morph", "litera", "pulse" etc.
        super().__init__(themename="flatly")
        self.title("Trabalhar dados do LI-180 | Platar pontos")
        self.geometry("450x650")
        self.resizable(True, True)
        self.usar_ppfd = tb.BooleanVar(value=True)
        self.create_widgets()
        self._setup_terminal()

    def _setup_terminal(self):
        # Frame lateral direita para o log de execução
        self.terminal_frame = tb.Frame(self)
        self.terminal_frame.place_forget()
        # Remove o log lateral e restaura o sys.stdout padrão
        sys.stdout = sys.__stdout__

    def write(self, msg):
        pass

    def flush(self):
        pass

    def log(self, msg):
        pass

    def create_widgets(self):
        # Seção de organização e extração
        frame_acao = tb.Labelframe(
            self, text="Organização e extração", bootstyle="info")
        frame_acao.pack(pady=(18, 10), padx=18, fill='x')
        tb.Button(frame_acao, text="Organizar arquivos", width=28,
                  bootstyle=PRIMARY, command=self.organizar_arquivos).pack(pady=4, padx=8)
        tb.Button(frame_acao, text="Extrair coordenadas e valores", width=28,
                  bootstyle=PRIMARY, command=self.extrair_coordenadas).pack(pady=4, padx=8)

        # Separador visual
        tb.Separator(self, orient="horizontal").pack(fill="x", pady=12)

        # Seção de plotagem
        frame_plot = tb.Labelframe(
            self, text="Plotagem de gráficos", bootstyle="info")
        frame_plot.pack(pady=4, padx=18, fill='x')
        tb.Button(frame_plot, text="Gráfico 3D de pontos", width=28,
                  bootstyle=PRIMARY, command=self.plotar_3d_simples).pack(pady=4, padx=8)
        tb.Button(frame_plot, text="Gráfico 3D de superfície", width=28,
                  bootstyle=PRIMARY, command=self.plotar_surface).pack(pady=4, padx=8)
        tb.Button(frame_plot, text="Gráfico 3D com múltiplas superfícies", width=28,
                  bootstyle=PRIMARY, command=self.plotar_multiplas_surfaces).pack(pady=4, padx=8)

        # Opções para gráficos
        frame_opts = tb.Labelframe(
            self, text="Opções para gráficos", bootstyle="secondary")
        frame_opts.pack(pady=(16, 8), padx=18, fill='x')

        # Subsessão: Tipo de valor (PPFD/PFD)
        frame_tipo = tb.Labelframe(
            frame_opts, text="Variável para eixo Z", bootstyle="info")
        frame_tipo.pack(fill='x', padx=8, pady=(8, 4))
        radio_frame = tb.Frame(frame_tipo)
        radio_frame.pack(anchor='w', padx=8, pady=(6, 2))
        tb.Radiobutton(radio_frame, text="PPFD (µmol m⁻² s⁻¹)", variable=self.usar_ppfd,
                       value=True, bootstyle="info").pack(side='left', padx=(0, 16))
        tb.Radiobutton(radio_frame, text="PFD (µmol m⁻² s⁻¹)", variable=self.usar_ppfd,
                       value=False, bootstyle="info").pack(side='left')

        # Subsessão: Interpolação
        frame_interp = tb.Labelframe(
            frame_opts, text="Interpolação para superfície", bootstyle="info")
        frame_interp.pack(fill='x', padx=8, pady=(8, 4))
        self.interpolar_var = tb.StringVar(value="cubic")
        interp_radio_frame = tb.Frame(frame_interp)
        interp_radio_frame.pack(anchor='w', padx=8, pady=(6, 2))
        tb.Radiobutton(interp_radio_frame, text="Cúbica", variable=self.interpolar_var,
                       value="cubic", bootstyle="info").pack(side='left', padx=(0, 16))
        tb.Radiobutton(interp_radio_frame, text="Linear", variable=self.interpolar_var,
                       value="linear", bootstyle="info").pack(side='left', padx=(0, 16))
        tb.Radiobutton(interp_radio_frame, text="Mais próxima", variable=self.interpolar_var,
                       value="nearest", bootstyle="info").pack(side='left')

        # Botão sair
        tb.Button(self, text="Sair", width=18, bootstyle=DANGER,
                  command=self.quit).pack(pady=18)

    def organizar_arquivos(self):
        if not messagebox.askyesno("Confirmação", "Deseja realmente organizar os arquivos? Esta ação move arquivos entre pastas."):
            return
        pasta = filedialog.askdirectory(
            title="Selecione a pasta para organizar arquivos")
        if pasta:
            threading.Thread(target=self._organizar_arquivos_thread,
                             args=(pasta,), daemon=True).start()

    def _organizar_arquivos_thread(self, pasta):
        print(f'Iniciando organização dos arquivos em: {pasta}')
        resultado = fn.organizar_arquivos_por_padrao(pasta)
        if resultado:
            print('Organização concluída!')
            self.after(0, lambda: messagebox.showinfo(
                "Concluído", "Arquivos organizados com sucesso!"))
        else:
            print('Nenhum arquivo encontrado para organizar.')
            self.after(0, lambda: messagebox.showinfo(
                "Nada a organizar", "Nenhum arquivo encontrado para organizar na pasta selecionada."))

    def extrair_coordenadas(self):
        if not messagebox.askyesno("Confirmação", "Deseja realmente extrair as coordenadas e valores? Esta ação sobrescreve arquivos CSV nas subpastas."):
            return
        pasta_principal = filedialog.askdirectory(
            title="Selecione a pasta principal com as subpastas ESPD")
        if pasta_principal:
            threading.Thread(target=self._extrair_coordenadas_thread, args=(
                pasta_principal,), daemon=True).start()

    def _extrair_coordenadas_thread(self, pasta_principal):
        print(f'Iniciando extração nas subpastas de: {pasta_principal}')
        subpastas = [os.path.join(pasta_principal, p) for p in os.listdir(
            pasta_principal) if os.path.isdir(os.path.join(pasta_principal, p))]
        for subpasta in subpastas:
            print(f'Extraindo: {os.path.basename(subpasta)}')
            df = fn.extrair_coordenadas_e_valores_espd(
                subpasta, salvar_csv=True)
            print(str(df))
        print('Extração finalizada!')
        self.after(0, lambda: messagebox.showinfo(
            "Concluído", "Extração finalizada. Veja o terminal para detalhes."))

    def plotar_3d_simples(self):
        pasta = filedialog.askdirectory(
            title="Selecione a pasta para gráfico 3D PPFD/PFD")
        if pasta:
            df = fn.extrair_coordenadas_e_valores_espd(pasta)
            if not df.empty:
                fn.plotar_3d_ppfd(df=df, usar_ppfd=self.usar_ppfd.get())
            else:
                messagebox.showwarning(
                    "Aviso", "Nenhum dado encontrado na pasta selecionada.")

    def plotar_surface(self):
        pasta = filedialog.askdirectory(
            title="Selecione a pasta para Surface Plot 3D PPFD/PFD")
        if pasta:
            df = fn.extrair_coordenadas_e_valores_espd(pasta)
            if not df.empty:
                fn.plotar_surface_ppfd(
                    df=df, usar_ppfd=self.usar_ppfd.get(), interpolar=self.interpolar_var.get())
            else:
                messagebox.showwarning(
                    "Aviso", "Nenhum dado encontrado na pasta selecionada.")

    def plotar_multiplas_surfaces(self):
        pasta_principal = filedialog.askdirectory(
            title="Selecione a pasta principal com as subpastas ESPD")
        if pasta_principal:
            subpastas = [os.path.join(pasta_principal, p) for p in os.listdir(
                pasta_principal) if os.path.isdir(os.path.join(pasta_principal, p))]
            dfs = []
            nomes = []
            for subpasta in subpastas:
                df = fn.extrair_coordenadas_e_valores_espd(subpasta)
                if not df.empty:
                    dfs.append(df)
                    nomes.append(os.path.basename(subpasta))
            if dfs:
                fn.plotar_multiple_surface_ppfd(
                    dfs, nomes, usar_ppfd=self.usar_ppfd.get(), interpolar=self.interpolar_var.get())
            else:
                messagebox.showwarning(
                    "Aviso", "Nenhum dado encontrado nas subpastas.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
