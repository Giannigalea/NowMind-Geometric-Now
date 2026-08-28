"""L1.5 Present Geometry records and builders."""

from nowmind.geometry.builder import PresentGeometryBuilder, build_present_geometry
from nowmind.geometry.entity import Entity
from nowmind.geometry.present_geometry import PresentGeometry
from nowmind.geometry.relation import Provenance, Relation, RelationType
from nowmind.geometry.validation import ValidationIssue, ValidationIssueType, ValidationResult

__all__ = [
    "Entity",
    "PresentGeometry",
    "PresentGeometryBuilder",
    "Provenance",
    "Relation",
    "RelationType",
    "ValidationIssue",
    "ValidationIssueType",
    "ValidationResult",
    "build_present_geometry",
]

