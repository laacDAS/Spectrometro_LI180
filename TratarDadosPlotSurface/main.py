import functions as fn
import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox


class App(tb.Window):
    def __init__(self):
        # Experimente "flatly", "cosmo", "morph", "litera", "pulse" etc.
        super().__init__(themename="flatly")
        self.title("Trabalhar dados do LI-180 | Platar pontos")
        self.geometry("600x500")
        self.resizable(False, False)
        self.usar_ppfd = tb.BooleanVar(value=True)
        self.create_widgets()

    def create_widgets(self):
        tb.Label(self, text="Selecione a ação desejada:",
                 font=("Segoe UI", 16, "bold")).pack(pady=10)
        tb.Button(self, text="Organizar arquivos",
                  width=40, bootstyle=PRIMARY, command=self.organizar_arquivos).pack(pady=4)
        tb.Button(self, text="Extrair coordenadas e valores",
                  width=40, bootstyle=PRIMARY, command=self.extrair_coordenadas).pack(pady=4)
        tb.Button(self, text="Gráfico 3D de pontos",
                  width=40, bootstyle=PRIMARY, command=self.plotar_3d_simples).pack(pady=4)
        tb.Button(self, text="Gráfico 3D de superfície",
                  width=40, bootstyle=PRIMARY, command=self.plotar_surface).pack(pady=4)
        tb.Button(self, text="Gráfico 3D com múltiplas superfícies",
                  width=40, bootstyle=PRIMARY, command=self.plotar_multiplas_surfaces).pack(pady=4)
        tb.Label(self, text="\nOpções para gráficos:",
                 font=("Segoe UI", 14, "bold")).pack()
        tb.Radiobutton(self, text="PPFD (µmol m⁻² s⁻¹)", variable=self.usar_ppfd,
                       value=True, bootstyle="info").pack(anchor='w', padx=60)
        tb.Radiobutton(self, text="PFD (µmol m⁻² s⁻¹)", variable=self.usar_ppfd,
                       value=False, bootstyle="info").pack(anchor='w', padx=60)
        tb.Button(self, text="Sair", width=40, bootstyle=DANGER,
                  command=self.quit).pack(pady=14)

    def organizar_arquivos(self):
        pasta = filedialog.askdirectory(
            title="Selecione a pasta para organizar arquivos")
        if pasta:
            fn.organizar_arquivos_por_padrao(pasta)
            messagebox.showinfo(
                "Concluído", "Arquivos organizados com sucesso!")

    def extrair_coordenadas(self):
        pasta_principal = filedialog.askdirectory(
            title="Selecione a pasta principal com as subpastas ESPD")
        if pasta_principal:
            subpastas = [os.path.join(pasta_principal, p) for p in os.listdir(
                pasta_principal) if os.path.isdir(os.path.join(pasta_principal, p))]
            for subpasta in subpastas:
                df = fn.extrair_coordenadas_e_valores_espd(
                    subpasta, salvar_csv=True)
                print(f"Subpasta: {os.path.basename(subpasta)}")
                print(df)
            messagebox.showinfo(
                "Concluído", "Extração finalizada. Veja o terminal para detalhes.")

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
                fn.plotar_surface_ppfd(df=df, usar_ppfd=self.usar_ppfd.get())
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
                    dfs, nomes, usar_ppfd=self.usar_ppfd.get())
            else:
                messagebox.showwarning(
                    "Aviso", "Nenhum dado encontrado nas subpastas.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
