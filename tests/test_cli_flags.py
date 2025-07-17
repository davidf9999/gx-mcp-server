import sys
from gx_mcp_server.__main__ import parse_args


def test_inspector_auth_default(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['prog'])
    args = parse_args()
    assert args.inspector_auth is None


def test_inspector_auth_value(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['prog', '--inspector-auth', 'secret'])
    args = parse_args()
    assert args.inspector_auth == 'secret'
