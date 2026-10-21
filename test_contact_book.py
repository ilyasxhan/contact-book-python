"""Tests for contact_book.py — run with:  python -m pytest"""

import json

import contact_book as cb


def test_load_missing_file_returns_empty(tmp_path):
    assert cb.load_contacts(tmp_path / "missing.json") == {}


def test_load_invalid_json_returns_empty(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    assert cb.load_contacts(bad) == {}


def test_old_format_is_upgraded(tmp_path):
    old = tmp_path / "old.json"
    old.write_text(json.dumps({"Ali": "03001234567"}))
    assert cb.load_contacts(old) == {"Ali": {"phone": "03001234567", "email": ""}}


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "contacts.json"
    data = {"Sara": {"phone": "+923001234567", "email": "sara@example.com"}}
    cb.save_contacts(data, path)
    assert cb.load_contacts(path) == data


def test_find_name_is_case_insensitive():
    contacts = {"Ali Khan": {"phone": "123", "email": ""}}
    assert cb.find_name(contacts, "ali khan") == "Ali Khan"
    assert cb.find_name(contacts, "Bilal") is None


def test_phone_validation():
    assert cb.PHONE_PATTERN.match("+923001234567")
    assert cb.PHONE_PATTERN.match("0300-1234567")
    assert not cb.PHONE_PATTERN.match("hello")
    assert not cb.PHONE_PATTERN.match("12")


def test_add_duplicate_raises(monkeypatch):
    contacts = {"Ali": {"phone": "03001234567", "email": ""}}
    monkeypatch.setattr("builtins.input", lambda _: "ali")
    try:
        cb.add_contact(contacts)
        assert False, "expected DuplicateContactError"
    except cb.DuplicateContactError:
        pass


def test_export_csv(tmp_path):
    out = tmp_path / "out.csv"
    cb.export_csv({"Ali": {"phone": "03001234567", "email": ""}}, out)
    lines = out.read_text().splitlines()
    assert lines[0] == "Name,Phone,Email"
    assert lines[1] == "Ali,03001234567,"
