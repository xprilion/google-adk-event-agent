from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Event(BaseModel):
    name: str
    city: Optional[str] = None
    country: Optional[str] = None
    location: Optional[str] = None
    hyperlink: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    misc: Optional[str] = None
    cfp: Dict[str, Any] = Field(default_factory=dict)
    closed_captions: bool = False
    scholarship: bool = False
    status: Optional[str] = None

    # Normalized fields derived from the raw "date" field in the source
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @staticmethod
    def _epoch_ms_to_datetime(ms: int) -> datetime:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)

    @staticmethod
    def _normalize_tags(value: Any) -> List[str]:
        if not value:
            return []
        result: List[str] = []
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    key = str(item.get("key", "")).strip()
                    val = str(item.get("value", "")).strip()
                    if key or val:
                        if key and val:
                            result.append(f"{key}:{val}")
                        else:
                            result.append(key or val)
                else:
                    result.append(str(item))
        else:
            result.append(str(value))
        return result

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "Event":
        # The raw format contains "date" as [start_ms, end_ms]
        start_time: Optional[datetime] = None
        end_time: Optional[datetime] = None
        date_field = raw.get("date")
        if isinstance(date_field, list) and len(date_field) == 2:
            try:
                start_time = cls._epoch_ms_to_datetime(int(date_field[0]))
                end_time = cls._epoch_ms_to_datetime(int(date_field[1]))
            except Exception:
                start_time, end_time = None, None

        # Build model with normalized keys
        return cls(
            name=raw.get("name", ""),
            city=raw.get("city"),
            country=raw.get("country"),
            location=raw.get("location"),
            hyperlink=raw.get("hyperlink"),
            tags=cls._normalize_tags(raw.get("tags")),
            misc=raw.get("misc"),
            cfp=raw.get("cfp") or {},
            closed_captions=bool(raw.get("closedCaptions", False)),
            scholarship=bool(raw.get("scholarship", False)),
            status=raw.get("status"),
            start_time=start_time,
            end_time=end_time,
        )

    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "hyperlink": self.hyperlink,
            "location": self.location,
            "city": self.city,
            "country": self.country,
            "tags": self.tags,
            "status": self.status,
            "closedCaptions": self.closed_captions,
            "scholarship": self.scholarship,
            "start": self.start_time.isoformat() if self.start_time else None,
            "end": self.end_time.isoformat() if self.end_time else None,
        }
