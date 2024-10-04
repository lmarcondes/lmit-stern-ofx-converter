
from datetime import datetime


def to_ofx_time(dt: datetime) -> str:
    timestamp_format = "%Y%m%d%H%M%S"
    converted = dt.strftime(timestamp_format)
    offset = dt.utcoffset()
    if offset is None:
        offset_str = "[0:GMT]"
    else:
        offset_hours = int(offset.total_seconds() / 3600)
        offset_str = f"[{offset_hours}]"
    final = f"{converted}{offset_str}"
    return final
