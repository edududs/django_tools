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


def should_run_ruff(plan: ValidationPlan) -> bool:
    """Check if ruff should run.

    Args:
        plan: Validation plan

    Returns:
        True if ruff should run

    """
    return plan.ruff


def should_run_pyright(plan: ValidationPlan) -> bool:
    """Check if pyright should run.

    Args:
        plan: Validation plan

    Returns:
        True if pyright should run

    """
    return plan.pyright


def should_run_tests(plan: ValidationPlan) -> bool:
    """Check if tests should run.

    Args:
        plan: Validation plan

    Returns:
        True if tests should run

    """
    return plan.tests

