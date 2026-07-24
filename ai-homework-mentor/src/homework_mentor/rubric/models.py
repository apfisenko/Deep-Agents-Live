"""Rubric schema (SGR-friendly)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RubricCriterion(BaseModel):
    id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    required: bool = True


class Rubric(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    criteria: list[RubricCriterion] = Field(min_length=1)
