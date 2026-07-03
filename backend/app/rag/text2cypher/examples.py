"""Few-shot NL→Cypher pairs (schema.md §3.3-3.4)."""

from __future__ import annotations

FEW_SHOT_EXAMPLES: tuple[str, ...] = (
    (
        "Q: Сколько стоит комбо «ИИ-агенты», какая сумма курсов по отдельности "
        "и какой процент скидки? "
        "A: MATCH (combo:Combo {slug: 'ai-agents-combo'}) "
        "MATCH (combo)-[:INCLUDES]->(c:Course) "
        "WITH combo, sum(c.priceRub) AS sumParts "
        "RETURN combo.priceRub AS comboPrice, sumParts, "
        "round(100.0 * (1 - toFloat(combo.priceRub) / sumParts), 1) AS discountPct "
        "LIMIT 1"
    ),
    (
        "Q: Какие темы проходят во всех 4 ступенях комбо ai-agents-combo? "
        "A: MATCH (:Combo {slug: 'ai-agents-combo'})-[:INCLUDES]->(c:Course) "
        "MATCH (c)-[:COVERS]->(t:Theme) "
        "WITH t.canonicalName AS theme, count(DISTINCT c) AS n "
        "WHERE n = 4 "
        "RETURN theme ORDER BY theme LIMIT 50"
    ),
    (
        "Q: Какие аудитории у каждого курса комбо «ИИ-агенты»? "
        "A: MATCH (:Combo {slug: 'ai-agents-combo'})-[:INCLUDES]->(c:Course) "
        "MATCH (c)-[:TARGETS]->(a:Audience) "
        "RETURN c.slug, collect(a.name) AS audiences "
        "ORDER BY c.stepOrder LIMIT 50"
    ),
    (
        "Q: Сколько курсов входит в комбо ai-agents-combo? "
        "A: MATCH (:Combo {slug: 'ai-agents-combo'})-[:INCLUDES]->(c:Course) "
        "RETURN count(c) AS courseCount LIMIT 1"
    ),
    (
        "Q: Какова сумма lessonCount по всем курсам комбо ai-agents-combo? "
        "A: MATCH (:Combo {slug: 'ai-agents-combo'})-[:INCLUDES]->(c:Course) "
        "RETURN sum(c.lessonCount) AS totalLessons LIMIT 1"
    ),
    (
        "Q: Сколько уникальных тем покрывают курсы комбо ai-agents-combo? "
        "A: MATCH (:Combo {slug: 'ai-agents-combo'})-[:INCLUDES]->(c:Course) "
        "MATCH (c)-[:COVERS]->(t:Theme) "
        "RETURN count(DISTINCT t.canonicalName) AS themeCount LIMIT 1"
    ),
    (
        "Q: Перечисли slug всех ступеней комбо ai-agents-combo по порядку stepOrder. "
        "A: MATCH (:Combo {slug: 'ai-agents-combo'})-[:INCLUDES]->(c:Course) "
        "RETURN c.slug AS slug, c.stepOrder AS stepOrder "
        "ORDER BY c.stepOrder LIMIT 50"
    ),
)


def get_few_shot_examples() -> list[str]:
    return list(FEW_SHOT_EXAMPLES)
