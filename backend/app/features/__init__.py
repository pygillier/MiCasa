"""Functional features: OPML import/export, Uptime Kuma sync, weather, scheduled jobs.

Feature modules may use the technical root (``extensions``, ``models``, ``settings``, ...)
but the root never depends on them, except ``create_app`` wiring the scheduler jobs.
"""
