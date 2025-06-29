import functions as fn
import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, ttk, scrolledtext
import sys
import threading
import tkinter as tk


class ToolTip:
    def __init__(self, widget, text, delay=600):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.delay = delay  # tempo em ms
        self._after_id = None
        self.widget.bind("<Enter>", self.schedule_tip)
        self.widget.bind("<Leave>", self.hide_tip)
        self.widget.bind("<Motion>", self.move_tip)
        self._last_xy = (0, 0)

    def schedule_tip(self, event=None):
        self._after_id = self.widget.after(self.delay, self.show_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y = self.widget.winfo_pointerxy()
        tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        # Cria label para medir tamanho
        label = tk.Label(tw, text=self.text, justify='left', background="#ffffe0",
                         relief='solid', borderwidth=1, font=("Segoe UI", 10))
        label.pack(ipadx=6, ipady=2)
        tw.update_idletasks()
        # Calcula posição para não sair da tela
        screen_w = tw.winfo_screenwidth()
        screen_h = tw.winfo_screenheight()
        tip_w = tw.winfo_width()
        tip_h = tw.winfo_height()
        pos_x = x + 20
        pos_y = y + 20
        if pos_x + tip_w > screen_w:
            pos_x = x - tip_w - 10
        if pos_y + tip_h > screen_h:
            pos_y = y - tip_h - 10
        tw.wm_geometry(f"+{pos_x}+{pos_y}")
        self.tipwindow = tw

    def move_tip(self, event):
        if self.tipwindow:
            x, y = self.widget.winfo_pointerxy()
            tw = self.tipwindow
            tw.update_idletasks()
            screen_w = tw.winfo_screenwidth()
            screen_h = tw.winfo_screenheight()
            tip_w = tw.winfo_width()
            tip_h = tw.winfo_height()
            pos_x = x + 20
            pos_y = y + 20
            if pos_x + tip_w > screen_w:
                pos_x = x - tip_w - 10
            if pos_y + tip_h > screen_h:
                pos_y = y - tip_h - 10
            tw.wm_geometry(f"+{pos_x}+{pos_y}")

    def hide_tip(self, event=None):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class App(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Trabalhar dados do LI-180 | Platar pontos")
        self.resizable(True, True)
        self.usar_ppfd = tb.BooleanVar(value=True)
        self._create_main_interface()
        self.update_idletasks()
        self.geometry("")  # Ajusta ao conteúdo
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_main_interface(self):
        self._create_widgets(self)
        self._create_bottom_buttons()

    def _create_bottom_buttons(self):
        bottom_btn_frame = tb.Frame(self)
        bottom_btn_frame.pack(pady=(0, 8))
        help_button = tb.Button(
            bottom_btn_frame, text="Ajuda", bootstyle=INFO, command=self.open_help_window)
        help_button.pack(side='left', padx=(0, 12))
        sair_button = tb.Button(
            bottom_btn_frame, text="Sair", width=18, bootstyle=DANGER, command=self.confirmar_sair)
        sair_button.pack(side='left')

    def open_help_window(self):
        help_win = tb.Toplevel(self)
        help_win.title("Ajuda")
        help_win.geometry("900x1000")
        help_win.resizable(True, True)
        self._create_help_tab(help_win)

    def _create_help_tab(self, parent):
        help_text = self._load_help_text()
        if not help_text.strip():
            help_text = "Arquivo de ajuda vazio ou não encontrado."
        text_widget = scrolledtext.ScrolledText(
            parent, wrap='word', font=('Consolas', 11))
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        text_widget.pack(fill='both', expand=True, padx=8, pady=8)
        parent.update_idletasks()
        parent.lift()
        parent.focus_force()

    def _load_help_text(self):
        help_path = os.path.join(os.path.dirname(__file__), 'Forma_de_uso.md')
        try:
            with open(help_path, encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Não foi possível carregar o arquivo de ajuda.\n\nErro: {e}"

    def _create_widgets(self, parent):
        self._create_organizacao_extracao(parent)
        tb.Separator(parent, orient="horizontal").pack(fill="x", pady=12)
        self._create_plotagem(parent)
        self._create_opcoes_graficos(parent)

    def _create_organizacao_extracao(self, parent):
        frame_acao = tb.Labelframe(
            parent, text="Organização e extração", bootstyle="info")
        frame_acao.pack(pady=(18, 10), padx=18, fill='x')
        btn_org = tb.Button(frame_acao, text="Organizar arquivos", width=28, bootstyle=PRIMARY,
                            command=self.organizar_arquivos)
        btn_org.pack(pady=4, padx=8)
        ToolTip(btn_org, "Move arquivos para subpastas conforme o padrão de nome. Use após copiar arquivos do LI-180.")
        btn_ext = tb.Button(frame_acao, text="Extrair coordenadas e valores", width=28, bootstyle=PRIMARY,
                            command=self.extrair_coordenadas)
        btn_ext.pack(pady=4, padx=8)
        ToolTip(
            btn_ext, "Extrai coordenadas e valores PPFD e PFD dos arquivos nas subpastas e gera arquivos CSV.")

    def _create_plotagem(self, parent):
        frame_plot = tb.Labelframe(
            parent, text="Plotagem de gráficos", bootstyle="info")
        frame_plot.pack(pady=4, padx=18, fill='x')
        btn_pontos = tb.Button(frame_plot, text="Gráfico 3D de pontos", width=28, bootstyle=PRIMARY,
                               command=self.plotar_3d_simples)
        btn_pontos.pack(pady=4, padx=8)
        ToolTip(
            btn_pontos, "Plota um gráfico 3D de pontos com os dados extraídos da pasta selecionada.")
        btn_surface = tb.Button(frame_plot, text="Gráfico 3D de superfície", width=28, bootstyle=PRIMARY,
                                command=self.plotar_surface)
        btn_surface.pack(pady=4, padx=8)
        ToolTip(
            btn_surface, "Plota uma superfície 3D interpolada para os dados da pasta selecionada.")
        btn_mult = tb.Button(frame_plot, text="Gráfico 3D com múltiplas superfícies", width=28, bootstyle=PRIMARY,
                             command=self.plotar_multiplas_surfaces)
        btn_mult.pack(pady=4, padx=8)
        ToolTip(
            btn_mult, "Plota múltiplas superfícies 3D para todas as subpastas encontradas.")

    def _create_opcoes_graficos(self, parent):
        frame_opts = tb.Labelframe(
            parent, text="Opções para gráficos", bootstyle="secondary")
        frame_opts.pack(pady=(16, 8), padx=18, fill='x')
        self._create_tipo_valor(frame_opts)
        self._create_interpolacao(frame_opts)

    def _create_tipo_valor(self, parent):
        frame_tipo = tb.Labelframe(
            parent, text="Variável para eixo Z", bootstyle="info")
        frame_tipo.pack(fill='x', padx=8, pady=(8, 4))
        radio_frame = tb.Frame(frame_tipo)
        radio_frame.pack(anchor='w', padx=8, pady=(6, 2))
        tb.Radiobutton(radio_frame, text="PPFD (µmol m⁻² s⁻¹)", variable=self.usar_ppfd,
                       value=True, bootstyle="info").pack(side='left', padx=(0, 16))
        tb.Radiobutton(radio_frame, text="PFD (µmol m⁻² s⁻¹)", variable=self.usar_ppfd,
                       value=False, bootstyle="info").pack(side='left')

    def _create_interpolacao(self, parent):
        frame_interp = tb.Labelframe(
            parent, text="Interpolação para superfície", bootstyle="info")
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

    def organizar_arquivos(self):
        if not messagebox.askyesno(
                "Confirmação", "Deseja realmente organizar os arquivos? Esta ação move arquivos entre pastas."):
            return
        pasta = filedialog.askdirectory(
            title="Selecione a pasta para organizar arquivos")
        if pasta:
            threading.Thread(target=self._organizar_arquivos_thread,
                             args=(pasta,), daemon=True).start()

    def _organizar_arquivos_thread(self, pasta):
        try:
            print(f'Iniciando organização dos arquivos em: {pasta}')
            fn.organizar_arquivos_por_padrao(pasta)
            print('Organização concluída!')
            self.after(0, lambda: messagebox.showinfo(
                "Concluído", "Arquivos organizados com sucesso!"))
        except Exception as e:
            print(f'Erro ao organizar arquivos: {e}')
            self.after(0, lambda: messagebox.showerror(
                "Erro ao organizar arquivos", str(e)))

    def extrair_coordenadas(self):
        if not messagebox.askyesno(
                "Confirmação", "Deseja realmente extrair as coordenadas e valores? Esta ação sobrescreve arquivos CSV nas subpastas."):
            return
        pasta_principal = filedialog.askdirectory(
            title="Selecione a pasta principal com as subpastas ESPD")
        if pasta_principal:
            threading.Thread(target=self._extrair_coordenadas_thread, args=(
                pasta_principal,), daemon=True).start()

    def _extrair_coordenadas_thread(self, pasta_principal):
        try:
            print(f'Iniciando extração nas subpastas de: {pasta_principal}')
            subpastas = [os.path.join(pasta_principal, p) for p in os.listdir(pasta_principal)
                         if os.path.isdir(os.path.join(pasta_principal, p))]
            for subpasta in subpastas:
                print(f'Extraindo: {os.path.basename(subpasta)}')
                df = fn.extrair_coordenadas_e_valores_espd(
                    subpasta, salvar_csv=True)
                print(str(df))
            print('Extração finalizada!')
            self.after(0, lambda: messagebox.showinfo(
                "Concluído", "Extração finalizada. Veja o terminal para detalhes."))
        except Exception as e:
            print(f'Erro ao extrair coordenadas: {e}')
            self.after(0, lambda: messagebox.showerror(
                "Erro ao extrair coordenadas e valores", str(e)))

    def plotar_3d_simples(self):
        pasta = filedialog.askdirectory(
            title="Selecione a pasta para gráfico 3D PPFD/PFD")
        if pasta:
            try:
                df = fn.extrair_coordenadas_e_valores_espd(pasta)
                if not df.empty:
                    fn.plotar_3d_ppfd(df=df, usar_ppfd=self.usar_ppfd.get())
                else:
                    messagebox.showwarning(
                        "Aviso", "Nenhum dado encontrado na pasta selecionada. Garanta que foi selecionado uma pasta com arquivos válidos.")
            except Exception as e:
                messagebox.showerror(
                    "Erro ao plotar gráfico 3D de pontos", str(e))

    def plotar_surface(self):
        pasta = filedialog.askdirectory(
            title="Selecione a pasta para Surface Plot 3D PPFD/PFD")
        if pasta:
            try:
                df = fn.extrair_coordenadas_e_valores_espd(pasta)
                if not df.empty:
                    metodo = self.interpolar_var.get()
                    print(f"Método de interpolação selecionado: {metodo}")
                    fn.plotar_surface_ppfd(
                        df, self.usar_ppfd.get(), metodo)
                else:
                    messagebox.showwarning(
                        "Aviso", "Nenhum dado encontrado na pasta selecionada. Garanta que foi selecionado uma pasta com arquivos válidos.")
            except Exception as e:
                messagebox.showerror(
                    "Erro ao plotar superfície", str(e))

    def plotar_multiplas_surfaces(self):
        pasta_principal = filedialog.askdirectory(
            title="Selecione a pasta principal com as subpastas ESPD")
        if pasta_principal:
            try:
                subpastas = [os.path.join(pasta_principal, p) for p in os.listdir(pasta_principal)
                             if os.path.isdir(os.path.join(pasta_principal, p))]
                dfs = []
                nomes = []
                for subpasta in subpastas:
                    df = fn.extrair_coordenadas_e_valores_espd(subpasta)
                    if not df.empty:
                        dfs.append(df)
                        nomes.append(os.path.basename(subpasta))
                if dfs:
                    metodo = self.interpolar_var.get()
                    print(f"Método de interpolação selecionado: {metodo}")
                    fn.plotar_multiple_surface_ppfd(
                        dfs, nomes, self.usar_ppfd.get(), metodo)
                else:
                    messagebox.showwarning(
                        "Aviso", "Nenhum dado encontrado nas subpastas. Garanta que foi escolhida uma pasta que contenha as subpastas com arquivos válidos.")
            except Exception as e:
                messagebox.showerror(
                    "Erro ao plotar múltiplas superfícies", str(e))

    def confirmar_sair(self):
        if messagebox.askyesno("Confirmação", "Deseja realmente sair do programa?"):
            self.quit()


if __name__ == "__main__":
    app = App()
    app.mainloop()
