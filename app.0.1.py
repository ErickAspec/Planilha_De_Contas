import json
import os
import csv
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog

ARQUIVO_DADOS = "dados.json"

# ----- Tooltip -----
class ToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#333333", foreground="white",
                         relief='solid', borderwidth=1,
                         font=("Segoe UI", 9))
        label.pack(ipadx=5, ipady=2)

    def hide(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None

# ----- Linha Hover na Treeview -----
def treeview_hover(tree):
    def on_motion(event):
        region = tree.identify("region", event.x, event.y)
        if region == "cell":
            item = tree.identify_row(event.y)
            tree.tag_remove("hover", *tree.get_children())
            if item:
                tree.tag_configure("hover", background="#555555")
                tree.item(item, tags=("hover",))
        else:
            tree.tag_remove("hover", *tree.get_children())
    tree.bind("<Motion>", on_motion)

# ----- Classe principal -----
class ControleContas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Controle de Contas")
        self.geometry("900x600")
        self.configure(bg="#1e1e1e")

        # Dados
        self.contas = self.carregar_dados()

        # Variáveis
        self.var_nome = tk.StringVar()
        self.var_valor = tk.StringVar()
        self.var_continuo = tk.BooleanVar()
        self.var_categoria = tk.StringVar()
        self.var_periodo = tk.StringVar()
        self.filtro_var = tk.StringVar(value="Todas")

        # Estilo
        self.estilo_widgets()

        # Interface
        self.criar_widgets()
        self.atualizar_lista()

        # Atalhos de teclado
        self.bind_all("<Control-a>", lambda e: self.adicionar_conta())
        self.bind_all("<Control-e>", lambda e: self.editar_conta())
        self.bind_all("<Control-r>", lambda e: self.remover_conta())
        self.bind_all("<Control-m>", lambda e: self.mover_conta())
        self.bind_all("<Control-t>", lambda e: self.selecionar_todas())
        self.bind_all("<Control-n>", lambda e: self.ordenar_nome())
        self.bind_all("<Control-v>", lambda e: self.ordenar_valor())
        self.bind_all("<Control-s>", lambda e: self.exportar_csv())
        self.bind_all("<Return>", lambda e: self.adicionar_conta())
        self.bind_all("<Delete>", lambda e: self.remover_conta())

    def estilo_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground="#2e2e2e",
                        background="#2e2e2e",
                        foreground="white",
                        selectbackground="#555555",
                        selectforeground="white",
                        font=("Segoe UI", 10))
        style.configure("TButton",
                        background="#3e3e3e",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"),
                        padding=5)
        style.map("TButton", background=[('active', '#555555')])
        style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 10))
        style.configure("Treeview",
                        background="#2e2e2e",
                        foreground="white",
                        fieldbackground="#2e2e2e",
                        rowheight=25,
                        font=("Segoe UI", 10),
                        bordercolor="#555555",
                        relief="solid")
        style.configure("Treeview.Heading",
                        background="#3e3e3e",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"),
                        relief="raised")
        style.map("Treeview", background=[('selected', '#555555')])

    def carregar_dados(self):
        if not os.path.exists(ARQUIVO_DADOS):
            with open(ARQUIVO_DADOS, "w") as f:
                json.dump([], f)
        with open(ARQUIVO_DADOS, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def salvar_dados(self):
        with open(ARQUIVO_DADOS, "w") as f:
            json.dump(self.contas, f, indent=4)

    def criar_widgets(self):
        # ----- BARRA DE BOTÕES NO TOPO -----
        frame_botoes = tk.Frame(self, bg="#1e1e1e")
        frame_botoes.pack(pady=5, padx=10, fill="x")

        botoes_info = [
            ("Editar", self.editar_conta),
            ("Mover", self.mover_conta),
            ("Remover", self.remover_conta),
            ("Selecionar Todas", self.selecionar_todas),
            ("Ordenar Nome", self.ordenar_nome),
            ("Ordenar Valor", self.ordenar_valor),
            ("Exportar CSV", self.exportar_csv)
        ]

        for nome, func in botoes_info:
            btn = tk.Button(frame_botoes, text=nome, command=func,
                            bg="#3e3e3e", fg="white", font=("Segoe UI",10,"bold"),
                            relief="raised", bd=2, width=12, height=2)
            btn.pack(side="left", padx=5)

            # Tooltip
            ToolTip(btn, f"Ação: {nome}")

            # Hover effect
            def on_enter(e, b=btn):
                b['bg'] = '#555555'
            def on_leave(e, b=btn):
                b['bg'] = '#3e3e3e'
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        # ----- CAMPOS COMPACTOS DE ENTRADA -----
        frame_campos = tk.Frame(self, bg="#1e1e1e")
        frame_campos.pack(pady=5, padx=10, fill="x")

        tk.Label(frame_campos, text="Nome:").grid(row=0, column=0, sticky="w")
        tk.Entry(frame_campos, textvariable=self.var_nome, bg="#2e2e2e", fg="white", insertbackground="white", width=20).grid(row=0, column=1, padx=5)
        tk.Label(frame_campos, text="Valor R$").grid(row=0, column=2, sticky="w")
        tk.Entry(frame_campos, textvariable=self.var_valor, bg="#2e2e2e", fg="white", insertbackground="white", width=10).grid(row=0, column=3, padx=5)
        tk.Label(frame_campos, text="Categoria:").grid(row=0, column=4, sticky="w")
        ttk.Combobox(frame_campos, textvariable=self.var_categoria, values=["Casa","Trabalho","Outros"], width=15).grid(row=0, column=5, padx=5)
        tk.Label(frame_campos, text="Período:").grid(row=0, column=6, sticky="w")
        ttk.Combobox(frame_campos, textvariable=self.var_periodo, values=["Dia","Semanal","Mensal","Anual"], width=12).grid(row=0, column=7, padx=5)
        tk.Checkbutton(frame_campos, text="Contínuo", variable=self.var_continuo, bg="#1e1e1e", fg="white", selectcolor="#2e2e2e").grid(row=0, column=8, padx=5)
        ttk.Button(frame_campos, text="Adicionar", command=self.adicionar_conta).grid(row=0, column=9, padx=5)

        # ----- TREEVIEW ESTILO EXCEL -----
        frame_lista = tk.Frame(self, bg="#1e1e1e")
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
        columns = ("Categoria","Nome","Valor","Tipo","Período")
        self.tree = ttk.Treeview(frame_lista, columns=columns, show="headings", selectmode="extended")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160, anchor="center", minwidth=100)
        self.tree.pack(fill="both", expand=True)
        scrollbar_v = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        scrollbar_v.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar_v.set)
        scrollbar_h = ttk.Scrollbar(frame_lista, orient="horizontal", command=self.tree.xview)
        scrollbar_h.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=scrollbar_h.set)
        treeview_hover(self.tree)

        # ----- TOTAL -----
        self.label_total = tk.Label(self, text="Total: R$0.00", font=("Segoe UI",12,"bold"), bg="#1e1e1e", fg="white")
        self.label_total.pack(pady=5)

    # ----- FUNÇÕES PRINCIPAIS -----
    def adicionar_conta(self):
        nome = self.var_nome.get().strip()
        valor = self.var_valor.get().strip()
        continuo = self.var_continuo.get()
        categoria = self.var_categoria.get()
        periodo = self.var_periodo.get()
        if not nome or not valor or not categoria or not periodo:
            messagebox.showerror("Erro","Preencha todos os campos!"); return
        try: valor = float(valor)
        except ValueError: messagebox.showerror("Erro","Valor inválido!"); return
        self.contas.append({"nome":nome,"valor":valor,"continuo":continuo,"categoria":categoria,"periodo":periodo})
        self.salvar_dados()
        self.atualizar_lista()
        self.var_nome.set(""); self.var_valor.set(""); self.var_continuo.set(False)

    def atualizar_lista(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        total_cont = 0; total_uni = 0
        for i, conta in enumerate(self.contas):
            tipo = "Contínuo" if conta["continuo"] else "Único"
            valor_text = f"R${conta['valor']:.2f}"
            tag = "even" if i%2==0 else "odd"
            tag_val = "valor_positivo" if conta['valor']>=0 else "valor_negativo"
            self.tree.insert("", "end", values=(conta["categoria"],conta["nome"],valor_text,tipo,conta["periodo"]), tags=(tag,tag_val))
            if conta["continuo"]: total_cont += conta["valor"]
            else: total_uni += conta["valor"]
        self.tree.tag_configure("odd", background="#2e2e2e")
        self.tree.tag_configure("even", background="#3a3a3a")
        self.tree.tag_configure("valor_positivo", foreground="#00ff00")
        self.tree.tag_configure("valor_negativo", foreground="#ff4c4c")
        self.label_total.config(text=f"Total Contínuas: R${total_cont:.2f} | Total Únicas: R${total_uni:.2f}")

    def remover_conta(self):
        selecao = self.tree.selection()
        if not selecao: messagebox.showerror("Erro","Selecione uma conta para remover!"); return
        if messagebox.askyesno("Confirmar","Deseja realmente remover a(s) conta(s) selecionada(s)?"):
            indices = [self.tree.index(s) for s in selecao]
            for index in sorted(indices, reverse=True): del self.contas[index]
            self.salvar_dados()
            self.atualizar_lista()

    def editar_conta(self):
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showerror("Erro", "Selecione uma conta para editar!")
            return
        index = self.tree.index(selecao[0])
        conta = self.contas[index]

        edit_win = tk.Toplevel(self)
        edit_win.title("Editar Conta")
        edit_win.configure(bg="#1e1e1e")

        tk.Label(edit_win, text="Nome:", bg="#1e1e1e", fg="white").grid(row=0, column=0, sticky="w")
        var_nome = tk.StringVar(value=conta["nome"])
        tk.Entry(edit_win, textvariable=var_nome, bg="#2e2e2e", fg="white", insertbackground="white").grid(row=0, column=1, padx=5, pady=5)

        tk.Label(edit_win, text="Valor R$:", bg="#1e1e1e", fg="white").grid(row=1, column=0, sticky="w")
        var_valor = tk.StringVar(value=str(conta["valor"]))
        tk.Entry(edit_win, textvariable=var_valor, bg="#2e2e2e", fg="white", insertbackground="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(edit_win, text="Categoria:", bg="#1e1e1e", fg="white").grid(row=2, column=0, sticky="w")
        var_categoria = tk.StringVar(value=conta["categoria"])
        ttk.Combobox(edit_win, textvariable=var_categoria, values=["Casa","Trabalho","Outros"], width=20).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(edit_win, text="Período:", bg="#1e1e1e", fg="white").grid(row=3, column=0, sticky="w")
        var_periodo = tk.StringVar(value=conta["periodo"])
        ttk.Combobox(edit_win, textvariable=var_periodo, values=["Dia","Semanal","Mensal","Anual"], width=20).grid(row=3, column=1, padx=5, pady=5)

        var_continuo = tk.BooleanVar(value=conta["continuo"])
        tk.Checkbutton(edit_win, text="Contínuo", variable=var_continuo, bg="#1e1e1e", fg="white", selectcolor="#2e2e2e").grid(row=4, column=0, columnspan=2, pady=5)

        def salvar_edicao():
            try:
                valor_float = float(var_valor.get())
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido!")
                return
            self.contas[index] = {
                "nome": var_nome.get(),
                "valor": valor_float,
                "continuo": var_continuo.get(),
                "categoria": var_categoria.get(),
                "periodo": var_periodo.get()
            }
            self.salvar_dados()
            self.atualizar_lista()
            edit_win.destroy()

        ttk.Button(edit_win, text="Salvar", command=salvar_edicao).grid(row=5, column=0, columnspan=2, pady=10)

    def mover_conta(self):
        selecao = self.tree.selection()
        if not selecao: messagebox.showerror("Erro","Selecione uma conta para mover!"); return
        nova_categoria = simpledialog.askstring("Mover","Nova categoria:")
        if not nova_categoria: return
        indices = [self.tree.index(s) for s in selecao]
        for index in indices: self.contas[index]["categoria"] = nova_categoria
        self.salvar_dados()
        self.atualizar_lista()

    def selecionar_todas(self):
        for item in self.tree.get_children(): self.tree.selection_add(item)

    def exportar_csv(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files","*.csv")])
        if not caminho: return
        with open(caminho,"w",newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Categoria","Nome","Valor","Tipo","Período"])
            for conta in self.contas:
                tipo = "Contínuo" if conta["continuo"] else "Único"
                writer.writerow([conta["categoria"],conta["nome"],conta["valor"],tipo,conta["periodo"]])
        messagebox.showinfo("Sucesso","Dados exportados com sucesso!")

    def ordenar_nome(self):
        self.contas.sort(key=lambda x: x["nome"].lower())
        self.atualizar_lista()

    def ordenar_valor(self):
        self.contas.sort(key=lambda x: x["valor"])
        self.atualizar_lista()

# ----- MAIN -----
if __name__ == "__main__":
    app = ControleContas()
    app.mainloop()
