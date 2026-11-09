import pytest

from storage.history import ConversationStore


def test_save_load_roundtrip(tmp_path):
    store = ConversationStore(tmp_path / "history")
    cid = store.new_id()
    msgs = [{"role": "user", "content": "Bebeğim ne zaman emekler?"}, {"role": "assistant", "content": "…"}]
    store.save(cid, msgs)
    assert store.load(cid) == msgs
    assert store.list_ids() == [cid]
    assert not list((tmp_path / "history").glob("*.tmp"))


def test_rejects_path_traversal(tmp_path):
    with pytest.raises(ValueError):
        ConversationStore(tmp_path).save("../disari", [])


def test_empty_dir(tmp_path):
    assert ConversationStore(tmp_path / "yok").list_ids() == []


def test_list_conversations_newest_first_with_titles(tmp_path, monkeypatch):
    import storage.history as h

    store = ConversationStore(tmp_path)
    times = iter(["2026-10-01T10:00:00", "2026-10-02T10:00:00"])

    class FakeNow:
        @staticmethod
        def now():
            class T:
                def isoformat(self, timespec):
                    return next(times)
            return T()

    monkeypatch.setattr(h, "datetime", FakeNow)
    store.save("eski", [{"role": "user", "content": "Gebelikte  folik asit\nne işe yarar?"}])
    store.save("yeni", [{"role": "user", "content": "x" * 100}])
    items = store.list_conversations()
    assert [c.id for c in items] == ["yeni", "eski"]
    assert items[1].title == "Gebelikte folik asit ne işe yarar?"
    assert len(items[0].title) == 48 and items[0].title.endswith("…")


def test_corrupt_file_is_skipped(tmp_path):
    store = ConversationStore(tmp_path)
    store.save("iyi", [{"role": "user", "content": "a"}])
    (tmp_path / "bozuk.json").write_text("{", encoding="utf-8")
    assert [c.id for c in store.list_conversations()] == ["iyi"]


def test_delete_and_delete_all(tmp_path):
    store = ConversationStore(tmp_path)
    for cid in ("a", "b", "c"):
        store.save(cid, [{"role": "user", "content": cid}])
    store.delete("a")
    assert store.list_ids() == ["b", "c"]
    assert store.delete_all() == 2
    assert store.list_ids() == []
