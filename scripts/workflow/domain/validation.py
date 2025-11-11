"""Validation orchestration - business logic for validation planning."""

from dataclasses import dataclass


@dataclass
class ValidationPlan:
    """Plan for validation execution."""

    ruff: bool
    pyright: bool
    tests: bool
