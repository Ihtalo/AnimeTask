import tkinter as tk
from tkinter import ttk
import json, os
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import winsound

# ================= PATHS =================
ASSETS = "assets"
SOUNDS = "sounds"

ICON_ADD = os.path.join(ASSETS, "add.png")
ICON_DONE = os.path.join(ASSETS, "done.png")
ICON_DEL = os.path.join(ASSETS, "delete.png")
SPLASH_IMG = os.path.join(ASSETS, "splash.png")
APP_ICON = os.path.join(ASSETS, "icon.png")
CLICK_SOUND = os.path.join(SOUNDS, "click.wav")

TASK_FILE = "tasks.json"
CONFIG_FILE = "config.json"

# ================= CONFIG =================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"tema_escuro": True, "som": True}

def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

config = load_config()

# ================= SOUND =================
def play_click():
    if config["som"] and os.path.exists(CLICK_SOUND):
        winsound.PlaySound(CLICK_SOUND, winsound.SND_ASYNC)

# ================= TASKS =================
def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks():
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)

tasks = load_tasks()

# ================= APP =================
root = tk.Tk()
root.title("AnimeTask")
root.geometry("780x700")

if os.path.exists(APP_ICON):
    root.iconphoto(True, tk.PhotoImage(file=APP_ICON))

# ================= SPLASH =================
def show_splash():
    if not os.path.exists(SPLASH_IMG):
        return

    splash = tk.Toplevel(root)
    splash.overrideredirect(True)

    img = Image.open(SPLASH_IMG).resize((420, 420))
    photo = ImageTk.PhotoImage(img)

    lbl = tk.Label(splash, image=photo)
    lbl.image = photo
    lbl.pack()

    x = root.winfo_screenwidth() // 2 - 210
    y = root.winfo_screenheight() // 2 - 210
    splash.geometry(f"420x420+{x}+{y}")

    root.withdraw()
    root.after(2000, lambda: close_splash(splash))

def close_splash(splash):
    splash.destroy()
    root.deiconify()

show_splash()

# ================= STYLE =================
style = ttk.Style()
style.theme_use("clam")

style.configure("TNotebook", background="#0f172a")
style.configure("TNotebook.Tab", padding=[14, 8])

# ================= NOTEBOOK =================
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab_tasks = tk.Frame(notebook)
tab_stats = tk.Frame(notebook)
tab_config = tk.Frame(notebook)

notebook.add(tab_tasks, text="Tarefas")
notebook.add(tab_stats, text="Estatísticas")
notebook.add(tab_config, text="Configurações")

# ================= THEME =================
def apply_theme():
    if config["tema_escuro"]:
        bg = "#0f172a"
        fg = "white"
        card = "#1f2937"
    else:
        bg = "white"
        fg = "black"
        card = "#f3f4f6"

    root.configure(bg=bg)
    for f in (tab_tasks, tab_stats, tab_config):
        f.configure(bg=bg)

    return card, fg

card_bg, text_fg = apply_theme()

def toggle_theme():
    config["tema_escuro"] = not config["tema_escuro"]
    save_config()
    global card_bg, text_fg
    card_bg, text_fg = apply_theme()
    refresh()

# ================= TAB TASKS =================
top = tk.Frame(tab_tasks, bg=tab_tasks["bg"])
top.pack(fill="x", pady=(12, 6))

entry = tk.Entry(top, font=("Segoe UI", 11))
entry.pack(side="left", padx=(14, 6), fill="x", expand=True, ipady=4)

priority = tk.StringVar(value="Média")
ttk.OptionMenu(top, priority, "Média", "Baixa", "Média", "Alta").pack(side="left", padx=(0, 14))

search_var = tk.StringVar()
tk.Entry(tab_tasks, textvariable=search_var).pack(fill="x", padx=14, pady=(0,4))

filter_var = tk.StringVar(value="Todas")
ttk.OptionMenu(tab_tasks, filter_var, "Todas", "Todas", "Alta", "Média", "Baixa", "Concluídas").pack(pady=(0,6))

btns = tk.Frame(tab_tasks, bg=tab_tasks["bg"])
btns.pack(pady=6)

def load_icon(path):
    if os.path.exists(path):
        return ImageTk.PhotoImage(Image.open(path).resize((20,20)))
    return None

icon_add = load_icon(ICON_ADD)
icon_done = load_icon(ICON_DONE)
icon_del = load_icon(ICON_DEL)

selected_index = None

def on_card_click(i):
    global selected_index
    selected_index = i
    refresh()

# ================= SCROLL =================
canvas = tk.Canvas(tab_tasks, highlightthickness=0)
canvas.pack(fill="both", expand=True)

scroll = ttk.Scrollbar(tab_tasks, command=canvas.yview)
scroll.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scroll.set)

card_container = tk.Frame(canvas)
canvas.create_window((0,0), window=card_container, anchor="nw")

card_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# ================= CARD =================
def create_card(task, index):
    selected = index == selected_index

    priority_colors = {
        "Alta": "#ef4444",
        "Média": "#f59e0b",
        "Baixa": "#10b981"
    }

    border_color = "#3b82f6" if selected else "#000000"
    priority_color = priority_colors.get(task["prioridade"], "#6b7280")

    shadow = tk.Frame(card_container, bg="#000000")
    shadow.pack(fill="x", padx=14, pady=8)

    border = tk.Frame(shadow, bg=border_color, padx=1, pady=1)
    border.pack(fill="x")

    card = tk.Frame(border, bg=card_bg)
    card.pack(fill="x")

    status = "✔" if task["concluida"] else "✘"

    title = tk.Label(card, text=f"{status} {task['texto']}",
                     bg=card_bg, fg=text_fg,
                     font=("Segoe UI", 11, "bold"),
                     anchor="w")
    title.pack(fill="x", padx=12, pady=(8, 2))

    info = tk.Label(card,
                    text=f"Prioridade: {task['prioridade']}   •   {task['data']}",
                    bg=card_bg,
                    fg=priority_color,
                    font=("Segoe UI", 9),
                    anchor="w")
    info.pack(fill="x", padx=12, pady=(0, 10))

    for w in (card, title, info):
        w.bind("<Button-1>", lambda e, i=index: on_card_click(i))

# ================= ACTIONS =================
def add_task():
    txt = entry.get().strip()
    if not txt:
        return

    tasks.append({
        "texto": txt,
        "prioridade": priority.get(),
        "concluida": False,
        "data": datetime.now().strftime("%Y-%m-%d")
    })

    entry.delete(0, tk.END)
    play_click()
    save_tasks()
    refresh()
    update_stats()

def toggle_done():
    if selected_index is None:
        return
    tasks[selected_index]["concluida"] = not tasks[selected_index]["concluida"]
    play_click()
    save_tasks()
    refresh()
    update_stats()

def delete_task():
    if selected_index is None:
        return
    tasks.pop(selected_index)
    play_click()
    save_tasks()
    refresh()
    update_stats()

ttk.Button(btns, text="Adicionar", image=icon_add, compound="left", command=add_task).pack(side="left", padx=6)
ttk.Button(btns, text="Concluir", image=icon_done, compound="left", command=toggle_done).pack(side="left", padx=6)
ttk.Button(btns, text="Remover", image=icon_del, compound="left", command=delete_task).pack(side="left", padx=6)
ttk.Button(btns, text="Tema", command=toggle_theme).pack(side="left", padx=6)

# ================= REFRESH =================
def refresh():
    for w in card_container.winfo_children():
        w.destroy()

    term = search_var.get().lower()
    flt = filter_var.get()

    for i, t in enumerate(tasks):
        if term and term not in t["texto"].lower():
            continue
        if flt == "Alta" and t["prioridade"] != "Alta":
            continue
        if flt == "Média" and t["prioridade"] != "Média":
            continue
        if flt == "Baixa" and t["prioridade"] != "Baixa":
            continue
        if flt == "Concluídas" and not t["concluida"]:
            continue

        create_card(t, i)

search_var.trace_add("write", lambda *_: refresh())
filter_var.trace_add("write", lambda *_: refresh())

# ================= STATS =================
stats_label = tk.Label(tab_stats, font=("Segoe UI", 12))
stats_label.pack(pady=30)

def update_stats():
    week = datetime.now() - timedelta(days=7)
    created = sum(datetime.fromisoformat(t["data"]) >= week for t in tasks)
    done = sum(datetime.fromisoformat(t["data"]) >= week and t["concluida"] for t in tasks)
    pct = int((done / created) * 100) if created else 0
    stats_label.config(text=f"Tarefas criadas: {created}\nConcluídas: {done}\nProdutividade: {pct}%")

# ================= CONFIG =================
def toggle_sound():
    config["som"] = not config["som"]
    save_config()

ttk.Button(tab_config, text="Ativar/Desativar Som", command=toggle_sound).pack(pady=20)

# ================= INIT =================
refresh()
update_stats()
root.mainloop()