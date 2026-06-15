"""Item- and run-level evaluators for Langfuse experiments (E-17, E-19)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

from langfuse.experiment import Evaluation
from openai import AsyncOpenAI

from app.agent.run_config import JudgeSection, RunConfig
from ragas_compat import ensure_ragas_imports

ensure_ragas_imports()

from ragas.embeddings import embedding_factory
from ragas.llms import llm_factory
from ragas.metrics.collections import AnswerCorrectness, AnswerRelevancy, ContextRecall, Faithfulness

B2B_HINTS = ("b2b", "корпорат", "договор", "кп", "команд", "юрлиц")


@dataclass
class JudgeRuntime:
    llm: Any
    embeddings: Any
    answer_correctness: AnswerCorrectness
    faithfulness: Faithfulness
    answer_relevancy: AnswerRelevancy
    context_recall: ContextRecall


def build_judge_runtime(config: RunConfig) -> JudgeRuntime:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        msg = "OPENROUTER_API_KEY is required for evaluators"
        raise RuntimeError(msg)

    embedding_model = os.environ.get("EMBEDDING_MODEL", "")
    if not embedding_model:
        msg = "EMBEDDING_MODEL is required for evaluators"
        raise RuntimeError(msg)

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    )
    llm = llm_factory(
        config.judge.name,
        provider="openai",
        client=client,
        max_tokens=8192,
    )
    embeddings = embedding_factory(
        provider="openai",
        model=embedding_model,
        client=client,
    )
    return JudgeRuntime(
        llm=llm,
        embeddings=embeddings,
        answer_correctness=AnswerCorrectness(llm=llm, weights=[1.0, 0.0]),
        faithfulness=Faithfulness(llm=llm),
        answer_relevancy=AnswerRelevancy(llm=llm, embeddings=embeddings),
        context_recall=ContextRecall(llm=llm),
    )


def _unwrap_output(output: Any) -> tuple[str | None, list[str], list[str], str | None]:
    if output is None:
        return None, [], [], "no output"
    if isinstance(output, str):
        return output, [], [], None
    if isinstance(output, dict):
        if output.get("error"):
            return None, [], list(output.get("tools_called") or []), str(output["error"])
        answer = output.get("answer")
        contexts = output.get("contexts") or []
        tools_called = list(output.get("tools_called") or [])
        if not answer:
            return None, list(contexts), tools_called, "empty answer"
        return str(answer), [str(c) for c in contexts], tools_called, None
    return str(output), [], [], None


def _expected_answer(expected_output: Any) -> str:
    if expected_output is None:
        return ""
    if isinstance(expected_output, dict):
        return str(expected_output.get("answer", ""))
    return str(expected_output)


def _expected_tools(expected_output: Any) -> list[str]:
    if isinstance(expected_output, dict):
        tools = expected_output.get("expected_tools") or []
        return [str(t) for t in tools]
    return []


def _metadata_dict(metadata: Any) -> dict[str, Any]:
    if metadata is None:
        return {}
    if isinstance(metadata, dict):
        return metadata
    if hasattr(metadata, "model_dump"):
        return metadata.model_dump()
    return {}


def _facts(metadata: Any, expected_output: Any = None) -> list[str]:
    if isinstance(expected_output, dict):
        ref_facts = expected_output.get("reference_facts")
        if ref_facts:
            return [str(f) for f in ref_facts]
    raw = _metadata_dict(metadata).get("facts") or []
    return [str(f) for f in raw]


def _user_input(input_data: Any) -> str:
    if isinstance(input_data, dict):
        return str(input_data.get("message", ""))
    return str(input_data)


def fact_coverage_score(answer: str, facts: list[str]) -> float:
    if not facts:
        return 1.0
    answer_lower = answer.lower()
    hits = sum(1 for fact in facts if _fact_present(answer_lower, fact))
    return hits / len(facts)


def _fact_present(answer_lower: str, fact: str) -> bool:
    fact_lower = fact.lower()
    if fact_lower in answer_lower:
        return True
    numbers = re.findall(r"\d+", fact)
    if numbers and any(num in answer_lower for num in numbers):
        return True
    words = [w for w in re.findall(r"[\wа-яё]+", fact_lower, flags=re.IGNORECASE) if len(w) >= 4]
    if not words:
        return False
    matched = sum(1 for word in words if word in answer_lower)
    return matched >= max(1, len(words) // 2)


def tool_correctness_in_order(called: list[str], expected: list[str]) -> float:
    if not expected:
        return 1.0
    if not called:
        return 0.0
    idx = 0
    for tool in called:
        if idx < len(expected) and tool == expected[idx]:
            idx += 1
    return idx / len(expected)


def detect_segment(answer: str, tools_called: list[str]) -> str:
    answer_lower = answer.lower()
    if any(hint in answer_lower for hint in B2B_HINTS):
        return "b2b"
    if any(token in answer_lower for token in ("физлиц", "для себя", "на сайте", "рознич")):
        return "b2c"
    if "create_payment_link" in tools_called:
        return "b2c"
    return "b2c"


def evaluator_names_for_slug(
    dataset_slug: str,
    *,
    simulation: bool = False,
) -> tuple[str, ...]:
    slug = dataset_slug.strip().strip("/")
    if slug == "e2e-qa":
        slug = "e2e/e2e-qa"
    funnel_profile: tuple[str, ...] = (
        ("task_error", "tool_correctness", "state_check_lead", "task_completion")
        if simulation
        else ("task_error", "tool_correctness")
    )
    mapping: dict[str, tuple[str, ...]] = {
        "e2e/e2e-qa": ("task_error", "answer_correctness", "faithfulness", "answer_relevancy"),
        "rag/rag-format-facts": (
            "task_error",
            "answer_correctness",
            "faithfulness",
            "fact_coverage",
            "context_recall",
        ),
        "rag/rag-product-facts": (
            "task_error",
            "answer_correctness",
            "faithfulness",
            "fact_coverage",
        ),
        "behavior/segment-routing": (
            "task_error",
            "answer_correctness",
            "tool_correctness",
            "segment_match",
            "must_not_compliance",
        ),
        "behavior/funnel-to-lead": funnel_profile,
        "edge/out-of-catalog": ("task_error", "answer_correctness", "faithfulness"),
        "edge/objections-trust": (
            "task_error",
            "answer_correctness",
            "faithfulness",
            "fact_coverage",
        ),
    }
    if slug not in mapping:
        msg = f"No evaluator profile for {dataset_slug}"
        raise ValueError(msg)
    return mapping[slug]


def evaluate_state_check_lead(*, output: Any, expected_output: Any) -> Evaluation:
    _, _, called, err = _unwrap_output(output)
    if err:
        return Evaluation(
            name="state_check_lead",
            value=0.0,
            comment=err,
            data_type="BOOLEAN",
        )
    expected_contact = ""
    if isinstance(expected_output, dict):
        expected_contact = str(expected_output.get("lead_contact", ""))
    lead_saved = False
    if isinstance(output, dict) and "lead_saved" in output:
        lead_saved = bool(output["lead_saved"])
    elif expected_contact and isinstance(output, dict):
        from user_simulation import state_check_lead as check_lead_saved

        session_id = str(output.get("session_id", ""))
        lead_saved = bool(session_id) and check_lead_saved(session_id, expected_contact)
    elif "save_lead" in called:
        lead_saved = True
    return Evaluation(
        name="state_check_lead",
        value=1.0 if lead_saved else 0.0,
        comment=f"contact={expected_contact or 'n/a'} saved={lead_saved}",
        data_type="BOOLEAN",
    )


def evaluate_task_completion(*, output: Any, expected_output: Any) -> Evaluation:
    _, _, called, err = _unwrap_output(output)
    if err:
        return Evaluation(name="task_completion", value=0.0, comment=err)
    if isinstance(output, dict) and output.get("task_completion") is not None:
        value = float(output["task_completion"])
        return Evaluation(
            name="task_completion",
            value=value,
            comment=f"simulation score={value:.3f}",
        )
    expected = _expected_tools(expected_output)
    tool_score = tool_correctness_in_order(called, expected)
    lead_ok = isinstance(output, dict) and bool(output.get("lead_saved"))
    if not lead_ok and "save_lead" in called:
        lead_ok = True
    value = round(tool_score * (1.0 if lead_ok else 0.5), 3)
    return Evaluation(
        name="task_completion",
        value=value,
        comment=f"tools={tool_score:.2f} lead={lead_ok}",
    )


def make_item_evaluators(
    judge: JudgeRuntime,
    *,
    dataset_slug: str,
    simulation: bool = False,
) -> list[Any]:
    names = set(evaluator_names_for_slug(dataset_slug, simulation=simulation))
    evaluators: list[Any] = []

    def task_error(*, output: Any, **_kw: Any) -> Evaluation:
        _, _, _, err = _unwrap_output(output)
        failed = output is None or err is not None
        return Evaluation(
            name="task_error",
            value=1.0 if failed else 0.0,
            comment=err or "ok",
            data_type="BOOLEAN",
        )

    evaluators.append(task_error)

    if "answer_correctness" in names:
        async def answer_correctness(
            *,
            input: Any,
            output: Any,
            expected_output: Any,
            **_kw: Any,
        ) -> Evaluation:
            answer, _, _, err = _unwrap_output(output)
            if err:
                return Evaluation(name="answer_correctness", value=0.0, comment=err)
            result = await judge.answer_correctness.ascore(
                _user_input(input),
                answer or "",
                _expected_answer(expected_output),
            )
            value = float(result.value)
            return Evaluation(name="answer_correctness", value=value, comment=f"ragas score={value:.3f}")

        evaluators.append(answer_correctness)

    if "faithfulness" in names:
        async def faithfulness(*, input: Any, output: Any, **_kw: Any) -> Evaluation:
            answer, contexts, _, err = _unwrap_output(output)
            if err:
                return Evaluation(name="faithfulness", value=0.0, comment=err)
            result = await judge.faithfulness.ascore(
                _user_input(input),
                answer or "",
                contexts or [" "],
            )
            value = float(result.value)
            comment = f"ragas score={value:.3f}"
            if not contexts:
                comment = f"{comment}; no retrieved contexts"
            return Evaluation(name="faithfulness", value=value, comment=comment)

        evaluators.append(faithfulness)

    if "answer_relevancy" in names:
        async def answer_relevancy(*, input: Any, output: Any, **_kw: Any) -> Evaluation:
            answer, _, _, err = _unwrap_output(output)
            if err:
                return Evaluation(name="answer_relevancy", value=0.0, comment=err)
            result = await judge.answer_relevancy.ascore(_user_input(input), answer or "")
            value = float(result.value)
            return Evaluation(name="answer_relevancy", value=value, comment=f"ragas score={value:.3f}")

        evaluators.append(answer_relevancy)

    if "fact_coverage" in names:
        def fact_coverage(
            *,
            output: Any,
            metadata: Any = None,
            expected_output: Any = None,
            **_kw: Any,
        ) -> Evaluation:
            answer, _, _, err = _unwrap_output(output)
            if err:
                return Evaluation(name="fact_coverage", value=0.0, comment=err)
            facts = _facts(metadata, expected_output)
            value = fact_coverage_score(answer or "", facts)
            return Evaluation(
                name="fact_coverage",
                value=value,
                comment=f"{int(value * len(facts))}/{len(facts)} facts",
            )

        evaluators.append(fact_coverage)

    if "context_recall" in names:
        async def context_recall(
            *,
            input: Any,
            output: Any,
            expected_output: Any,
            **_kw: Any,
        ) -> Evaluation:
            _, contexts, _, err = _unwrap_output(output)
            if err:
                return Evaluation(name="context_recall", value=0.0, comment=err)
            reference = _expected_answer(expected_output)
            result = await judge.context_recall.ascore(
                _user_input(input),
                contexts or [" "],
                reference,
            )
            value = float(result.value)
            comment = f"ragas score={value:.3f}"
            if not contexts:
                comment = f"{comment}; no retrieved contexts"
            return Evaluation(name="context_recall", value=value, comment=comment)

        evaluators.append(context_recall)

    if "tool_correctness" in names:
        def tool_correctness(*, output: Any, expected_output: Any, **_kw: Any) -> Evaluation:
            _, _, called, err = _unwrap_output(output)
            if err:
                return Evaluation(name="tool_correctness", value=0.0, comment=err)
            expected = _expected_tools(expected_output)
            value = tool_correctness_in_order(called, expected)
            return Evaluation(
                name="tool_correctness",
                value=value,
                comment=f"called={called} expected={expected}",
            )

        evaluators.append(tool_correctness)

    if "segment_match" in names:
        def segment_match(*, output: Any, metadata: Any = None, **_kw: Any) -> Evaluation:
            answer, _, called, err = _unwrap_output(output)
            if err:
                return Evaluation(name="segment_match", value=0.0, comment=err, data_type="BOOLEAN")
            expected = str(_metadata_dict(metadata).get("segment", "b2c"))
            detected = detect_segment(answer or "", called)
            matched = detected == expected
            return Evaluation(
                name="segment_match",
                value=1.0 if matched else 0.0,
                comment=f"expected={expected} detected={detected}",
                data_type="BOOLEAN",
            )

        evaluators.append(segment_match)

    if "must_not_compliance" in names:
        def must_not_compliance(*, output: Any, metadata: Any = None, **_kw: Any) -> Evaluation:
            _, _, called, err = _unwrap_output(output)
            must_not = [str(t) for t in (_metadata_dict(metadata).get("must_not") or [])]
            if not must_not:
                return Evaluation(name="must_not_compliance", value=1.0, comment="n/a", data_type="BOOLEAN")
            if err:
                return Evaluation(name="must_not_compliance", value=0.0, comment=err, data_type="BOOLEAN")
            violated = [tool for tool in must_not if tool in called]
            ok = not violated
            return Evaluation(
                name="must_not_compliance",
                value=1.0 if ok else 0.0,
                comment=f"violated={violated}" if violated else "ok",
                data_type="BOOLEAN",
            )

        evaluators.append(must_not_compliance)

    if "state_check_lead" in names:

        def state_check_lead(*, output: Any, expected_output: Any, **_kw: Any) -> Evaluation:
            return evaluate_state_check_lead(output=output, expected_output=expected_output)

        evaluators.append(state_check_lead)

    if "task_completion" in names:

        def task_completion(*, output: Any, expected_output: Any, **_kw: Any) -> Evaluation:
            return evaluate_task_completion(output=output, expected_output=expected_output)

        evaluators.append(task_completion)

    return evaluators


def _metric_values(item_results: list[Any], metric_name: str) -> list[float]:
    values: list[float] = []
    for result in item_results:
        for evaluation in result.evaluations:
            if evaluation.name == metric_name and isinstance(evaluation.value, (int, float)):
                values.append(float(evaluation.value))
    return values


def make_run_evaluators(*, dataset_slug: str, simulation: bool = False) -> list[Any]:
    item_names = evaluator_names_for_slug(dataset_slug, simulation=simulation)
    avg_candidates = [
        name
        for name in item_names
        if name
        not in {"task_error", "segment_match", "must_not_compliance"}
    ]

    evaluators: list[Any] = []

    def error_rate(*, item_results: list[Any], **_kw: Any) -> Evaluation:
        total = max(len(item_results), 1)
        failed = sum(
            1
            for result in item_results
            if result.output is None or _unwrap_output(result.output)[3] is not None
        )
        return Evaluation(name="error_rate", value=failed / total)

    evaluators.append(error_rate)

    for metric in avg_candidates:

        def _avg_factory(name: str) -> Any:
            def _avg(*, item_results: list[Any], **_kw: Any) -> Evaluation:
                values = _metric_values(item_results, name)
                if not values:
                    return Evaluation(name=f"avg_{name}", value=0.0, comment="no scores")
                avg = sum(values) / len(values)
                return Evaluation(name=f"avg_{name}", value=avg)

            return _avg

        evaluators.append(_avg_factory(metric))

    return evaluators


def judge_metadata(judge: JudgeSection) -> dict[str, str]:
    return {
        "judge_model": judge.name,
        "judge_temperature": str(judge.temperature),
        "judge_provider": judge.provider,
    }
