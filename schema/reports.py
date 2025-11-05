from pydantic import BaseModel
from typing import List, Optional


class YearWiseCategoryReportSchema(BaseModel):
    year: int
    exclude: Optional[List[str]] = None
