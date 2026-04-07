import app as sorteia


class FakeVar:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeButton:
    def __init__(self):
        self.last_config = {}

    def config(self, **kwargs):
        self.last_config.update(kwargs)


class FakeTree:
    def __init__(self, selected_name=""):
        self.selected_name = selected_name

    def selection(self):
        return ["iid-1"] if self.selected_name else []

    def item(self, _item_id, _key):
        return (self.selected_name, "elegível")

    def get_children(self):
        return []

    def delete(self, _row_id):
        return None

    def insert(self, *_args, **_kwargs):
        return None


def make_app():
    instance = sorteia.SorteiaApp.__new__(sorteia.SorteiaApp)
    instance.state_machine = sorteia.STATE_DISCONNECTED
    instance.is_drawing = False
    instance.winner_name = ""
    instance.participants = []
    instance.previous_participants = []
    instance.source_var = FakeVar(sorteia.SOURCES[0])
    instance.chat_var = FakeVar("")
    instance.search_var = FakeVar("")
    instance.manual_entry_var = FakeVar("")
    instance.status_var = FakeVar("Estado: DISCONNECTED")
    instance.result_var = FakeVar("Vencedor: --")
    instance.total_var = FakeVar("Participantes: 0")
    instance.chat_status_var = FakeVar("Status do chat: desconectado")
    instance.draw_button = FakeButton()
    instance.draw_again_button = FakeButton()
    instance.participants_tree = FakeTree()
    instance._save_persistence = lambda: None
    instance._refresh_participant_list = lambda: None
    return instance


def test_connect_altera_estado_e_status_chat():
    app = make_app()

    app.connect()

    assert app.state_machine == sorteia.STATE_CONNECTED
    assert app.chat_status_var.get() == "Status do chat: conectado"


def test_select_chat_bloqueia_quando_desconectado(monkeypatch):
    app = make_app()
    mensagens = []
    monkeypatch.setattr(sorteia.messagebox, "showwarning", lambda *_args: mensagens.append("warning"))

    app.select_chat()

    assert mensagens == ["warning"]
    assert app.state_machine == sorteia.STATE_DISCONNECTED


def test_select_chat_define_estado_chat_selected(monkeypatch):
    app = make_app()
    app.state_machine = sorteia.STATE_CONNECTED
    app.chat_var.set("Canal Principal")
    monkeypatch.setattr(sorteia.messagebox, "showwarning", lambda *_args: None)

    app.select_chat()

    assert app.state_machine == sorteia.STATE_CHAT_SELECTED
    assert "Canal Principal" in app.chat_status_var.get()


def test_collect_participants_remove_duplicados_e_vazios(monkeypatch):
    app = make_app()
    app.state_machine = sorteia.STATE_CONNECTED
    app.chat_var.set("Canal Principal")
    app.source_var.set("chat atual")
    monkeypatch.setattr(sorteia.messagebox, "showerror", lambda *_args: None)

    app.collect_participants()

    nomes = [p["name"] for p in app.participants]
    assert nomes == ["alice", "bob", "carol", "dave", "eve", "frank", "grace"]
    assert all(p["status"] == "elegível" for p in app.participants)
    assert app.state_machine == sorteia.STATE_READY_TO_DRAW


def test_add_participant_ignora_nome_duplicado(monkeypatch):
    app = make_app()
    app.chat_var.set("Canal Principal")
    app.participants = [{"name": "Alice", "status": "elegível"}]
    app.manual_entry_var.set("alice")
    mensagens = []
    monkeypatch.setattr(sorteia.messagebox, "showinfo", lambda *_args: mensagens.append("duplicado"))

    app.add_participant()

    assert len(app.participants) == 1
    assert mensagens == ["duplicado"]


def test_add_participant_adiciona_e_limpa_campo():
    app = make_app()
    app.chat_var.set("Canal Principal")
    app.manual_entry_var.set("novo_nome")

    app.add_participant()

    assert app.participants == [{"name": "novo_nome", "status": "elegível"}]
    assert app.manual_entry_var.get() == ""
    assert app.state_machine == sorteia.STATE_READY_TO_DRAW


def test_remove_selected_participant_marca_como_removido():
    app = make_app()
    app.participants = [{"name": "alice", "status": "elegível"}, {"name": "bob", "status": "elegível"}]
    app.participants_tree = FakeTree(selected_name="alice")

    app.remove_selected_participant()

    assert app.participants[0]["status"] == "removido"
    assert app.participants[1]["status"] == "elegível"


def test_draw_winner_define_vencedor(monkeypatch):
    app = make_app()
    app.chat_var.set("Canal Principal")
    app.participants = [{"name": "alice", "status": "elegível"}, {"name": "bob", "status": "removido"}]
    monkeypatch.setattr(sorteia.random, "choice", lambda items: items[0])

    app.draw_winner()

    assert app.winner_name == "alice"
    assert app.result_var.get() == "Vencedor: alice"
    assert app.state_machine == sorteia.STATE_DRAW_COMPLETED


def test_draw_winner_sem_elegiveis_mostra_erro(monkeypatch):
    app = make_app()
    app.chat_var.set("Canal Principal")
    app.participants = [{"name": "bob", "status": "removido"}]
    mensagens = []
    monkeypatch.setattr(sorteia.messagebox, "showerror", lambda *_args: mensagens.append("erro"))

    app.draw_winner()

    assert mensagens == ["erro"]
    assert app.winner_name == ""


def test_restart_limpa_dados_e_mantem_conectado():
    app = make_app()
    app.state_machine = sorteia.STATE_DRAW_COMPLETED
    app.chat_var.set("Canal Principal")
    app.winner_name = "alice"
    app.participants = [{"name": "alice", "status": "elegível"}]
    app.previous_participants = [{"name": "old", "status": "elegível"}]

    app.restart()

    assert app.participants == []
    assert app.previous_participants == []
    assert app.winner_name == ""
    assert app.chat_var.get() == ""
    assert app.state_machine == sorteia.STATE_CONNECTED
