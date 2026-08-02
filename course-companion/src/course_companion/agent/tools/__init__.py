"""Тулы агента Companion — все режимы."""

from course_companion.agent.tools.mode_tools import (
    ask_course_qa,
    complete_homework,
    explain_feedback,
    resubmit_homework,
    return_to_qa,
    run_homework_check,
    show_fix_plan,
    switch_to_homework,
)

ALL_TOOLS: list = [
    switch_to_homework,
    complete_homework,
    return_to_qa,
    resubmit_homework,
    ask_course_qa,
    run_homework_check,
    explain_feedback,
    show_fix_plan,
]

__all__ = [
    "ALL_TOOLS",
    "ask_course_qa",
    "complete_homework",
    "explain_feedback",
    "resubmit_homework",
    "return_to_qa",
    "run_homework_check",
    "show_fix_plan",
    "switch_to_homework",
]
