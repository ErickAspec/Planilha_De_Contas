import json
import os
import tkinter as tk
from tkinter import messagebox

# Nome do arquivo para salvar as contas
ARQUIVO_DADOS = "dados.json"

# Função para carregar dados do arquivo
def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "w") as f:
            json.dump([], f)  # cria lista vazia no arquivo
    with open(ARQUIVO_DADOS, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

# Função para salvar dados no arquivo
def salvar_dados():
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(contas, f, indent=4)

# Função para adicionar conta
def adicionar_conta():
    nome = entrada_nome.get().strip()
    valor = entrada_valor.get().strip()
    continuo = var_continuo.get()

    if not nome or not valor:
        messagebox.showerror("Erro", "Preencha todos os campos!")
        return

    try:
        valor = float(valor)
    except ValueError:
        messagebox.showerror("Erro", "Valor inválido!")
        return

    contas.append({"nome": nome, "valor": valor, "continuo": continuo})
    salvar_dados()
    atualizar_lista()
    entrada_nome.delete(0, tk.END)
    entrada_valor.delete(0, tk.END)
    var_continuo.set(False)

# Função para atualizar lista de contas
def atualizar_lista():
    lista_contas.delete(0, tk.END)
    total = 0
    for conta in contas:
        status = "Contínuo" if conta["continuo"] else "Único"
        lista_contas.insert(tk.END, f"{conta['nome']} - R${conta['valor']:.2f} ({status})")
        total += conta["valor"]
    label_total.config(text=f"Total: R${total:.2f}")

# Função para remover conta
def remover_conta():
    selecao = lista_contas.curselection()
    if not selecao:
        messagebox.showerror("Erro", "Selecione uma conta para remover!")
        return
    index = selecao[0]
    del contas[index]
    salvar_dados()
    atualizar_lista()

# Criar janela principal
janela = tk.Tk()
janela.title("Controle de Contas")
janela.geometry("400x500")

# Campos de entrada
tk.Label(janela, text="Nome da Conta:").pack()
entrada_nome = tk.Entry(janela)
entrada_nome.pack()

tk.Label(janela, text="Valor (R$):").pack()
entrada_valor = tk.Entry(janela)
entrada_valor.pack()

var_continuo = tk.BooleanVar()
tk.Checkbutton(janela, text="Pagamento Contínuo", variable=var_continuo).pack()

# Botões
tk.Button(janela, text="Adicionar", command=adicionar_conta).pack(pady=5)
tk.Button(janela, text="Remover", command=remover_conta).pack(pady=5)

# Lista de contas
lista_contas = tk.Listbox(janela, height=15)
lista_contas.pack(fill=tk.BOTH, expand=True)

# Total
label_total = tk.Label(janela, text="Total: R$0.00", font=("Arial", 12, "bold"))
label_total.pack(pady=10)

# Carregar dados iniciais
contas = carregar_dados()
atualizar_lista()

# Rodar programa
janela.mainloop()
