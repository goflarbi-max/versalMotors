"""Validated Management Brief request contract."""

from datetime import date

from pydantic import BaseModel, model_validator


class BriefRequest(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def dates_in_order(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self
