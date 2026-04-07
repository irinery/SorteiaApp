import json
import random
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "SorteiaApp - Sistema de Sorteio para Live"
STATE_DISCONNECTED = "DISCONNECTED"
STATE_CONNECTED = "CONNECTED"
STATE_CHAT_SELECTED = "CHAT_SELECTED"
STATE_PARTICIPANTS_LOADED = "PARTICIPANTS_LOADED"
STATE_READY_TO_DRAW = "READY_TO_DRAW"
STATE_DRAW_COMPLETED = "DRAW_COMPLETED"

PERSISTENCE_FILE = Path.home() / ".sorteiaapp_state.json"

MOCK_CHAT_DATA = {
    "Canal Principal": [
        "alice", "bob", "carol", "alice", "dave", "", "eve", "frank", "grace",
    ],
    "Live Secundária": [
        "henry", "irene", "jack", "kate", "leo", "irene", "maria", "nina", "",
    ],
    "Canal de Teste": [
        "oscar", "paula", "quentin", "rita", "sam", "tina", "ursula", "victor",
    ],
}

SOURCES = ["chat atual", "chat selecionado", "lista manual", "lista importada"]


class SorteiaApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1280x720")
        self.minsize(1280, 720)
        self.configure(bg="#0f172a")

        self.state_machine = STATE_DISCONNECTED
        self.is_drawing = False
        self.winner_name = ""

        self.participants: list[dict[str, str]] = []
        self.previous_participants: list[dict[str, str]] = []

        self.source_var = tk.StringVar(value=SOURCES[0])
        self.chat_var = tk.StringVar(value="")
        self.search_var = tk.StringVar(value="")
        self.manual_entry_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Estado: DISCONNECTED")
        self.result_var = tk.StringVar(value="Vencedor: --")
        self.total_var = tk.StringVar(value="Participantes: 0")
        self.chat_status_var = tk.StringVar(value="Status do chat: desconectado")

        self._setup_style()
        self._build_layout()
        self._load_persistence()
        self._refresh_ui()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#0f172a")
        style.configure("TLabel", background="#0f172a", foreground="#e2e8f0", font=("Segoe UI", 11))
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), foreground="#f8fafc")
        style.configure("Result.TLabel", font=("Segoe UI", 22, "bold"), foreground="#22d3ee")
        style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"))
        style.configure("TButton", font=("Segoe UI", 10))

    def _build_layout(self) -> None:
        main = ttk.Frame(self, padding=16)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1)

        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        connection_frame = ttk.LabelFrame(left, text="1) Conexão / Fonte", padding=12)
        connection_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        connection_frame.columnconfigure(1, weight=1)

        ttk.Button(connection_frame, text="Conectar", command=self.connect).grid(row=0, column=0, padx=(0, 8), pady=4)
        ttk.Label(connection_frame, text="Fonte:").grid(row=0, column=1, sticky="w")
        self.source_combo = ttk.Combobox(connection_frame, state="readonly", values=SOURCES, textvariable=self.source_var)
        self.source_combo.grid(row=0, column=2, sticky="ew")
        self.source_combo.bind("<<ComboboxSelected>>", lambda _e: self.on_source_changed())

        chat_frame = ttk.LabelFrame(left, text="2) Seleção de chat", padding=12)
        chat_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        chat_frame.columnconfigure(1, weight=1)

        ttk.Button(chat_frame, text="Selecionar chat", command=self.select_chat).grid(row=0, column=0, padx=(0, 8), pady=4)
        self.chat_combo = ttk.Combobox(chat_frame, state="readonly", values=list(MOCK_CHAT_DATA.keys()), textvariable=self.chat_var)
        self.chat_combo.grid(row=0, column=1, sticky="ew")
        ttk.Label(chat_frame, textvariable=self.chat_status_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        participants_frame = ttk.LabelFrame(left, text="3) Lista de participantes", padding=12)
        participants_frame.grid(row=2, column=0, sticky="nsew")
        participants_frame.columnconfigure(0, weight=1)
        participants_frame.rowconfigure(2, weight=1)

        top_controls = ttk.Frame(participants_frame)
        top_controls.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top_controls.columnconfigure(4, weight=1)

        ttk.Button(top_controls, text="Coletar participantes", command=self.collect_participants).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(top_controls, text="Adicionar participante", command=self.add_participant).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(top_controls, text="Remover participante", command=self.remove_selected_participant).grid(row=0, column=2, padx=(0, 6))
        ttk.Button(top_controls, text="Limpar lista", command=self.clear_list).grid(row=0, column=3, padx=(0, 6))
        ttk.Button(top_controls, text="Remover duplicados", command=self.remove_duplicates_manually).grid(row=0, column=4, padx=(0, 6), sticky="w")
        ttk.Button(top_controls, text="Restaurar lista", command=self.restore_previous_list).grid(row=0, column=5)

        second_controls = ttk.Frame(participants_frame)
        second_controls.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        second_controls.columnconfigure(1, weight=1)
        ttk.Label(second_controls, text="Nome:").grid(row=0, column=0, padx=(0, 6))
        ttk.Entry(second_controls, textvariable=self.manual_entry_var).grid(row=0, column=1, sticky="ew", padx=(0, 12))
        ttk.Label(second_controls, text="Busca:").grid(row=0, column=2, padx=(0, 6))
        search_entry = ttk.Entry(second_controls, textvariable=self.search_var)
        search_entry.grid(row=0, column=3, sticky="ew")
        second_controls.columnconfigure(3, weight=1)
        self.search_var.trace_add("write", lambda *_: self._refresh_participant_list())

        columns = ("name", "status")
        self.participants_tree = ttk.Treeview(participants_frame, columns=columns, show="headings", selectmode="browse")
        self.participants_tree.heading("name", text="Nome")
        self.participants_tree.heading("status", text="Status")
        self.participants_tree.column("name", width=260)
        self.participants_tree.column("status", width=120, anchor="center")
        self.participants_tree.grid(row=2, column=0, sticky="nsew")

        ttk.Label(participants_frame, textvariable=self.total_var).grid(row=3, column=0, sticky="w", pady=(8, 0))

        draw_frame = ttk.LabelFrame(right, text="4) Área de sorteio e resultado", padding=12)
        draw_frame.grid(row=0, column=0, sticky="nsew")
        draw_frame.columnconfigure(0, weight=1)

        ttk.Label(draw_frame, text="Resultado do sorteio", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(draw_frame, textvariable=self.result_var, style="Result.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 18))

        self.draw_button = ttk.Button(draw_frame, text="Sortear", style="Primary.TButton", command=self.draw_winner)
        self.draw_button.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        self.draw_again_button = ttk.Button(draw_frame, text="Sortear novamente", command=self.draw_again)
        self.draw_again_button.grid(row=3, column=0, sticky="ew", pady=(0, 8))

        ttk.Button(draw_frame, text="Reiniciar", command=self.restart).grid(row=4, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(draw_frame, text="Copiar vencedor", command=self.copy_winner).grid(row=5, column=0, sticky="ew", pady=(0, 12))

        ttk.Separator(draw_frame, orient="horizontal").grid(row=6, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(draw_frame, textvariable=self.status_var).grid(row=7, column=0, sticky="w")

    def connect(self) -> None:
        self.state_machine = STATE_CONNECTED
        self.chat_status_var.set("Status do chat: conectado")
        self._refresh_ui()

    def on_source_changed(self) -> None:
        self._save_persistence()

    def select_chat(self) -> None:
        if self.state_machine == STATE_DISCONNECTED:
            messagebox.showwarning("Atenção", "Conecte antes de selecionar o chat.")
            return
        selected = self.chat_var.get().strip()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um chat/canal.")
            return
        if self.participants and not messagebox.askyesno("Confirmar", "Trocar chat pode impactar a lista atual. Deseja continuar?"):
            return
        self.state_machine = STATE_CHAT_SELECTED
        self.chat_status_var.set(f"Status do chat: selecionado ({selected})")
        self._save_persistence()
        self._refresh_ui()

    def collect_participants(self) -> None:
        if self.state_machine == STATE_DISCONNECTED:
            messagebox.showerror("Erro", "Conecte o sistema antes de coletar participantes.")
            return
        if not self.chat_var.get().strip():
            messagebox.showerror("Erro", "Selecione um chat antes de coletar participantes.")
            return

        source = self.source_var.get()
        raw_names: list[str] = []

        if source in {"chat atual", "chat selecionado"}:
            raw_names = MOCK_CHAT_DATA.get(self.chat_var.get(), [])
        elif source == "lista manual":
            messagebox.showinfo("Lista manual", "Use 'Adicionar participante' para montar a lista manual.")
            self.state_machine = STATE_CHAT_SELECTED
            self._refresh_ui()
            return
        elif source == "lista importada":
            file_path = filedialog.askopenfilename(
                title="Importar lista de participantes",
                filetypes=(("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")),
            )
            if not file_path:
                return
            try:
                raw_names = Path(file_path).read_text(encoding="utf-8").splitlines()
            except OSError as exc:
                messagebox.showerror("Erro", f"Falha ao importar arquivo: {exc}")
                return

        self._snapshot_list()
        self.participants = []
        seen = set()
        for name in raw_names:
            clean = name.strip()
            if not clean or clean.lower() in seen:
                continue
            seen.add(clean.lower())
            self.participants.append({"name": clean, "status": "elegível"})

        self.state_machine = STATE_PARTICIPANTS_LOADED if self.participants else STATE_CHAT_SELECTED
        self._refresh_ui()
        self._save_persistence()

    def add_participant(self) -> None:
        name = self.manual_entry_var.get().strip()
        if not name:
            messagebox.showwarning("Atenção", "Informe um nome para adicionar.")
            return
        existing = {p["name"].lower() for p in self.participants if p["status"] == "elegível"}
        if name.lower() in existing:
            messagebox.showinfo("Duplicado", "Participante já existe e foi ignorado.")
            return
        self._snapshot_list()
        self.participants.append({"name": name, "status": "elegível"})
        self.manual_entry_var.set("")
        self._set_ready_state_if_possible()
        self._refresh_ui()
        self._save_persistence()

    def remove_selected_participant(self) -> None:
        selected = self.participants_tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um participante para remover.")
            return
        values = self.participants_tree.item(selected[0], "values")
        target_name = values[0]
        self._snapshot_list()
        for participant in self.participants:
            if participant["name"] == target_name and participant["status"] == "elegível":
                participant["status"] = "removido"
                break
        self._refresh_ui()
        self._save_persistence()

    def clear_list(self) -> None:
        if not self.participants:
            return
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja limpar a lista?"):
            return
        self._snapshot_list()
        self.participants = []
        self.winner_name = ""
        self.result_var.set("Vencedor: --")
        self.state_machine = STATE_CHAT_SELECTED if self.chat_var.get().strip() else STATE_CONNECTED
        self._refresh_ui()
        self._save_persistence()

    def remove_duplicates_manually(self) -> None:
        self._snapshot_list()
        seen = set()
        unique_list = []
        for participant in self.participants:
            key = participant["name"].strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            unique_list.append(participant)
        self.participants = unique_list
        self._refresh_ui()
        self._save_persistence()

    def restore_previous_list(self) -> None:
        if not self.previous_participants:
            messagebox.showinfo("Sem histórico", "Não há lista anterior para restaurar.")
            return
        self.participants = [p.copy() for p in self.previous_participants]
        self._set_ready_state_if_possible()
        self._refresh_ui()
        self._save_persistence()

    def draw_winner(self) -> None:
        if self.is_drawing:
            return
        if not self.chat_var.get().strip():
            messagebox.showerror("Erro", "Selecione um chat antes do sorteio.")
            return
        eligible = [p for p in self.participants if p["status"] == "elegível"]
        if not eligible:
            messagebox.showerror("Erro", "Não há participantes elegíveis para sorteio.")
            return

        self.is_drawing = True
        winner = random.choice(eligible)
        self.winner_name = winner["name"]
        self.result_var.set(f"Vencedor: {self.winner_name}")
        self.state_machine = STATE_DRAW_COMPLETED
        self.is_drawing = False
        self._refresh_ui()

    def draw_again(self) -> None:
        self.draw_winner()

    def restart(self) -> None:
        self.participants = []
        self.previous_participants = []
        self.winner_name = ""
        self.result_var.set("Vencedor: --")
        self.chat_var.set("")
        self.chat_status_var.set("Status do chat: conectado")
        self.state_machine = STATE_CONNECTED if self.state_machine != STATE_DISCONNECTED else STATE_DISCONNECTED
        self._refresh_ui()
        self._save_persistence()

    def copy_winner(self) -> None:
        if not self.winner_name:
            return
        self.clipboard_clear()
        self.clipboard_append(self.winner_name)
        self.update()

    def _snapshot_list(self) -> None:
        self.previous_participants = [p.copy() for p in self.participants]

    def _set_ready_state_if_possible(self) -> None:
        if self.state_machine == STATE_DRAW_COMPLETED and self.winner_name:
            return
        eligible_count = len([p for p in self.participants if p["status"] == "elegível"])
        if eligible_count > 0 and self.chat_var.get().strip():
            self.state_machine = STATE_READY_TO_DRAW
        elif self.chat_var.get().strip():
            self.state_machine = STATE_CHAT_SELECTED
        elif self.state_machine != STATE_DISCONNECTED:
            self.state_machine = STATE_CONNECTED

    def _refresh_participant_list(self) -> None:
        search = self.search_var.get().strip().lower()
        for row_id in self.participants_tree.get_children():
            self.participants_tree.delete(row_id)

        total_visible = 0
        for participant in self.participants:
            if search and search not in participant["name"].lower():
                continue
            self.participants_tree.insert("", "end", values=(participant["name"], participant["status"]))
            total_visible += 1

        eligible_count = len([p for p in self.participants if p["status"] == "elegível"])
        self.total_var.set(f"Participantes: {eligible_count} elegíveis ({total_visible} exibidos)")

    def _refresh_ui(self) -> None:
        self._set_ready_state_if_possible()
        self.status_var.set(f"Estado: {self.state_machine}")

        eligible_count = len([p for p in self.participants if p["status"] == "elegível"])
        draw_enabled = eligible_count > 0 and bool(self.chat_var.get().strip()) and self.state_machine != STATE_DISCONNECTED
        self.draw_button.config(state="normal" if draw_enabled else "disabled")
        self.draw_again_button.config(state="normal" if self.winner_name else "disabled")

        if draw_enabled:
            self.draw_button.config(text="Sortear (pronto)")
        else:
            self.draw_button.config(text="Sortear")

        self._refresh_participant_list()

    def _save_persistence(self) -> None:
        payload = {
            "source": self.source_var.get(),
            "chat": self.chat_var.get(),
            "participants": self.participants,
        }
        try:
            PERSISTENCE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def _load_persistence(self) -> None:
        if not PERSISTENCE_FILE.exists():
            return
        try:
            payload = json.loads(PERSISTENCE_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        source = payload.get("source")
        if source in SOURCES:
            self.source_var.set(source)

        chat = payload.get("chat", "")
        if isinstance(chat, str):
            self.chat_var.set(chat)

        participants = payload.get("participants", [])
        if isinstance(participants, list):
            sanitized = []
            for item in participants:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name", "")).strip()
                status = item.get("status", "elegível")
                if name and status in {"elegível", "removido"}:
                    sanitized.append({"name": name, "status": status})
            self.participants = sanitized

        if self.chat_var.get().strip():
            self.state_machine = STATE_CHAT_SELECTED
            self.chat_status_var.set(f"Status do chat: selecionado ({self.chat_var.get().strip()})")
        if self.participants:
            self.state_machine = STATE_PARTICIPANTS_LOADED


if __name__ == "__main__":
    app = SorteiaApp()
    app.mainloop()
