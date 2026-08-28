from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from nowmind.core.now_state import NowState
from nowmind.reasoning.query import Answer, Query


@dataclass(frozen=True, slots=True)
class ExperimentRecord:
    now_id: UUID
    cycle_id: int
    query: Query | None
    answer_status: str | None
    relation_count: int
    validation_issue_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "now_id": str(self.now_id),
            "cycle_id": self.cycle_id,
            "query": self.query.query_type.value if self.query is not None else None,
            "answer_status": self.answer_status,
            "relation_count": self.relation_count,
            "validation_issue_count": self.validation_issue_count,
        }


class ExperimentRecorder:
    """External recorder that may retain historical Nows for evaluation.

    Runtime cognitive modules do not import this class. It is intended for demo,
    tests, and later experiment analysis only.
    """

    def __init__(self, log_path: Path | None = None) -> None:
        self.log_path = log_path
        self._records: list[ExperimentRecord] = []

    @property
    def history(self) -> tuple[ExperimentRecord, ...]:
        return tuple(self._records)

    def record(
        self,
        now: NowState,
        query: Query | None = None,
        answer: Answer | None = None,
    ) -> ExperimentRecord:
        record = ExperimentRecord(
            now_id=now.now_id,
            cycle_id=now.cycle_id,
            query=query,
            answer_status=answer.status.value if answer is not None else None,
            relation_count=len(now.geometry.relations),
            validation_issue_count=len(now.geometry.validation.issues),
        )
        self._records.append(record)
        if self.log_path is not None:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record.to_dict(), sort_keys=True))
                stream.write("\n")
        return record

    def delete_logs(self) -> None:
        self._records.clear()
        if self.log_path is not None and self.log_path.exists():
            self.log_path.unlink()

