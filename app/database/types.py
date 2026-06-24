"""Cross-dialect JSON column type (JSONB on PostgreSQL)."""

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB

JSONType = JSON().with_variant(JSONB(), "postgresql")
