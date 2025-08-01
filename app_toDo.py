import tkinter as tk  #kodları bir pencere şeklinde göstermek için gereken kütüphane
from tkinter import messagebox
import json
import os
import sys
import shutil

# -------------------------------
# PyInstaller uyumlu dosya yolu çözümleyici(bu kodları pc de exe yapmak için uğraşırken karşılaştığım bir problemin çözümü)
# -------------------------------
def get_resource_path(relative_path):
    """PyInstaller ile paketlenmiş uygulamalarda dosya yolu alimi"""
    try:
        base_path = sys._MEIPASS  # PyInstaller geçici dizin
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# -------------------------------
# Uygulama dizinleri ve dosya yolları
# -------------------------------
tasks = [] # görevlerin kaydedileceği yer 

#----------------------------
#yine exe ye dönüştürmek için işletim sistemine göre yapılması gereken ayarlar

def get_data_directory():    
    if sys.platform == "win32":
        base = os.getenv("LOCALAPPDATA")
    elif sys.platform == "darwin":  
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    app_folder = os.path.join(base, "ToDoApp")
    os.makedirs(app_folder, exist_ok=True)
    return app_folder

json_path = os.path.join(get_data_directory(), "tasks.json")
settings_path = os.path.join(get_data_directory(), "settings.json")
language_file_path = os.path.join(get_data_directory(), "languages.json")

# -------------------------------
# İlk çalıştırmada dil dosyasını kopyala  
# -------------------------------
def ensure_language_file():
    if not os.path.exists(language_file_path):
        try:
            src = get_resource_path("languages.json")
            shutil.copyfile(src, language_file_path)
        except Exception as e:
            messagebox.showerror("Dil Dosyasi", f"languages.json kopyalanamadi:\n{e}")
            sys.exit(1)

# -------------------------------
# Dil dosyasını yükle
# -------------------------------
def load_translations():
    try:
        with open(language_file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Hata", f"Dil dosyasi yüklenemedi:\n{e}")
        sys.exit(1)

# -------------------------------
# Ayarlar yükle/kaydet 
# -------------------------------
def load_language():
    if os.path.exists(settings_path):
        try:
            data = json.load(open(settings_path, encoding="utf-8"))
            return data.get("language", "tr")
        except:
            return "tr"
    return "tr"

def save_language(lang_code):
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump({"language": lang_code}, f)

# -------------------------------
# Görev yönetimi
# -------------------------------
def loadTasks():  #önceki görecvler varsa yani kaydedilmiş ise onları yazdırır
    if os.path.exists(json_path):
        try:
            data = json.load(open(json_path, encoding="utf-8"))
            if isinstance(data, list):
                tasks.extend(data)
        except json.JSONDecodeError:
            pass

def saveTasks():  #görevleri kaydeden fonksiyon
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)

def addTask():     #görev eklemek için
    txt = entry.get().strip()
    if txt:
        tasks.append({"text": txt, "done": False})
        entry.delete(0, tk.END)
        saveTasks()
        updateTaskList()
    else:
        messagebox.showwarning(translations[lang]["title"], translations[lang]["input_warning"])

def deleteTask(i):  #görev silmek için
    try:
        t = tasks[i]["text"]
        confirm = messagebox.askyesno(translations[lang]["title"], f"#{i+1} {t} {translations[lang]['delete_confirm']}")
        if confirm:
            tasks.pop(i)
            saveTasks()
            updateTaskList()
    except IndexError:
        messagebox.showwarning(translations[lang]["title"], translations[lang]["invalid_task"])

def toggleDone(i, var):
    tasks[i]["done"] = bool(var.get())
    saveTasks()

def updateTaskList():
    for w in scrollable_frame.winfo_children():
        w.destroy()
    for idx, task in enumerate(tasks):
        var = tk.IntVar(value=1 if task["done"] else 0)
        frm = tk.Frame(scrollable_frame, bg="#e6f0ff")
        frm.pack(fill="x", pady=2)
        cb = tk.Checkbutton(frm,
            text=f"#{idx+1}: {task['text']}",
            variable=var,
            command=lambda i=idx, v=var: toggleDone(i, v),
            anchor="w", padx=5,
            font=("Helvetica", 12), bg="#e6f0ff")
        cb.pack(side="left", fill="x", expand=True)
        btn = tk.Button(frm,
            text=translations[lang]["delete"],
            command=lambda i=idx: deleteTask(i),
            bg="#ff4d4d", fg="white",
            font=("Helvetica", 10, "bold"),
            activebackground="#ff4d4d",
            activeforeground="white",
            relief="ridge", bd=2,
            padx=10, pady=2, cursor="hand2")
        btn.pack(side="right", padx=5)

# -------------------------------
# Ayarlar penceresi #ayarlar sekmesinin butonları
# -------------------------------
def open_settings():
    sw = tk.Toplevel(root)
    sw.title(translations[lang]["settings"])
    sw.geometry("300x150")
    sw.resizable(False, False)

    lbl = tk.Label(sw, text=translations[lang]["language"], font=("Helvetica", 12))
    lbl.pack(pady=10)

    language_var = tk.StringVar(value=lang)
    opt = tk.OptionMenu(sw, language_var, *translations.keys())
    opt.pack(pady=10)

    def save_and_restart():
        new = language_var.get()
        save_language(new)
        sw.destroy()
        messagebox.showinfo(translations[new]["settings"], translations[new]["restart_info"])
        root.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

    btn = tk.Button(sw, text=translations[lang]["save"], command=save_and_restart)
    btn.pack(pady=10)

# -------------------------------
# Başlat
# -------------------------------
ensure_language_file()
translations = load_translations()
lang = load_language()

# GUI
root = tk.Tk()
root.title(translations[lang]["title"])
root.geometry("420x520")
root.resizable(False, False)
root.configure(bg="#e6f0ff")

# Menü #menü görünümü,butonlar, arka plan
menu_bar = tk.Menu(root)
settings_menu = tk.Menu(menu_bar, tearoff=0)
settings_menu.add_command(label=translations[lang]["settings"], command=open_settings)
menu_bar.add_cascade(label=translations[lang]["settings"], menu=settings_menu)
root.config(menu=menu_bar)

title_label = tk.Label(root, text=translations[lang]["title"], font=("Helvetica", 20, "bold"), bg="#e6f0ff")
title_label.pack(pady=10)

entry = tk.Entry(root, width=35, font=("Helvetica", 14))
entry.pack(pady=5)
entry.bind("<Return>", lambda event: addTask())

add_button = tk.Button(
    root,
    text=translations[lang]["add_task"],
    width=15,
    bg="#4caf50",
    fg="white",
    font=("Helvetica", 12, "bold"),
    command=addTask,
    cursor="hand2"
)
add_button.pack(pady=5)

task_frame = tk.Frame(root, bg="#e6f0ff")
task_frame.pack(pady=10, fill="both", expand=True)

canvas = tk.Canvas(task_frame, bg="#e6f0ff", highlightthickness=0)
scrollbar = tk.Scrollbar(task_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#e6f0ff")

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

exit_button = tk.Button(
    root,
    text=translations[lang]["exit"],
    width=10,
    bg="#f44336",
    fg="white",
    font=("Helvetica", 12, "bold"),
    command=root.destroy,
    cursor="hand2"
)
exit_button.pack(pady=10)


loadTasks()
updateTaskList()
root.mainloop()


#BVT