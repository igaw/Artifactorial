# vim: set ts=4
#
# Copyright 2026 Daniel Wagner
#
# SPDX-License-Identifier: MIT

import pathlib
import runpy

import pytest
from django.core.exceptions import ImproperlyConfigured

# share/settings.py is the Docker image's settings overlay; it isn't importable
# as a module, so load it the way Django would and check the result.
SETTINGS = pathlib.Path(__file__).resolve().parents[2] / "share" / "settings.py"


@pytest.fixture(autouse=True)
def no_yaml_config(monkeypatch):
    # Don't let a real /etc/artifactorial.yaml on the test host leak in.
    real_read_text = pathlib.Path.read_text

    def read_text(self, *args, **kwargs):
        if str(self) == "/etc/artifactorial.yaml":
            raise FileNotFoundError(self)
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, "read_text", read_text)
    monkeypatch.delenv("SENTRY_DSN", raising=False)


def test_secret_key_is_required(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ImproperlyConfigured, match="SECRET_KEY is not set"):
        runpy.run_path(str(SETTINGS))


def test_secret_key_from_environment(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "from-the-environment")
    assert runpy.run_path(str(SETTINGS))["SECRET_KEY"] == "from-the-environment"
