"""Validation orchestration - business logic for validation planning."""

from dataclasses import dataclass


@dataclass
class ValidationPlan:
    """Plan for validation execution."""

    ruff: bool
    pyright: bool
    tests: bool


def create_validation_plan(ruff: bool, pyright: bool, tests: bool) -> ValidationPlan:
    """Create validation plan from flags.

    Args:
        ruff: Whether to run ruff
        pyright: Whether to run pyright
        tests: Whether to run tests

    Returns:
        ValidationPlan

    """
    return ValidationPlan(ruff=ruff, pyright=pyright, tests=tests)
