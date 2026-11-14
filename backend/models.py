"""Typed transport boundary over the existing profile/backup validation."""
from copy import deepcopy
from datetime import date
from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, SecretStr, field_validator, model_validator
import profile_backup


def iso_date(value):
    if value is None or type(value) is date:
        return value
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError('Use an ISO calendar date')
    return date.fromisoformat(value)


CalendarDate = Annotated[date, BeforeValidator(iso_date)]
Count = Annotated[int, Field(strict=True, ge=0)]


class Model(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)


class Promotion(Model):
    rank: str
    date: CalendarDate

    @field_validator('rank')
    @classmethod
    def valid_rank(cls, value):
        if value not in profile_backup.CHOICES['rank']:
            raise ValueError('Unsupported rank')
        return value


class ServiceProfile(Model):
    service: str
    rank: str
    employment_type: str = 'Not specified'
    report: str = 'SJAR'
    transfer_history: str = 'None / not recorded'
    posting: str = 'Not specified'
    family: str = 'Not specified'
    accommodation_type: str = 'Not specified'
    years: Annotated[Count, Field(le=45)] = 0
    dependent_count: Annotated[Count, Field(le=12)] = 0
    pay_supplement: Annotated[Count, Field(le=4)] | None = None
    pay_increment: Annotated[Count, Field(le=20)] | None = None
    verified_pensionable_salary: Annotated[float, Field(strict=True, gt=0, le=300000)] | None = None
    salary_verified: bool = Field(default=False, strict=True)
    join_date: CalendarDate | None = None
    dob: CalendarDate | None = None
    planned_exit: CalendarDate | None = None
    join_date_set: bool = Field(default=False, strict=True)
    dob_set: bool = Field(default=False, strict=True)
    planned_exit_set: bool = Field(default=False, strict=True)
    pension_schemes: list[str] = Field(default_factory=lambda: ['Not sure'], max_length=4)
    rank_history: list[Promotion] = Field(default_factory=list, max_length=300)

    @field_validator(*profile_backup.CHOICES.keys())
    @classmethod
    def supported_choice(cls, value, info):
        if value not in profile_backup.CHOICES[info.field_name]:
            raise ValueError('Unsupported profile choice')
        return value

    @model_validator(mode='after')
    def coherent_flags(self):
        for field in ('join_date', 'dob', 'planned_exit'):
            if getattr(self, field + '_set') and getattr(self, field) is None:
                raise ValueError('A selected date is required')
            setattr(self, field + '_set', getattr(self, field) is not None)
        if self.salary_verified and self.verified_pensionable_salary is None:
            raise ValueError('Confirmed salary needs an amount')
        if self.dependent_count > 0:
            self.family = 'Dependants / children'
        return self


class Milestone(Model):
    label: str
    date: CalendarDate

    @field_validator('label')
    @classmethod
    def supported_label(cls, value):
        if value not in profile_backup.EVENT_LABELS:
            raise ValueError('Unsupported milestone')
        return value


class ProfileDocument(Model):
    version: Annotated[int, Field(strict=True, ge=1, le=1)] = 1
    profile: ServiceProfile
    events: list[Milestone] = Field(default_factory=list, max_length=300)
    benefits: dict[str, Any] | None = None

    @model_validator(mode='after')
    def existing_validation(self):
        # The exact same policy-free profile and benefit checks used by Streamlit.
        checked = profile_backup.validate(deepcopy(self.model_dump(mode='json')))
        self.benefits = checked['benefits']
        return self


class ExportRequest(Model):
    document: ProfileDocument
    passphrase: SecretStr = Field(min_length=12, max_length=512)


class RestoreRequest(Model):
    encrypted_file: str = Field(min_length=1, max_length=175000)
    passphrase: SecretStr = Field(min_length=1, max_length=512)


class Provenance(Model):
    profile: Literal['user_confirmed']
    salary: Literal['user_attested', 'not_confirmed']
    policy: Literal['not_assessed']


class SummaryMilestone(Model):
    label: str
    date: CalendarDate


class Summary(Model):
    service: str
    rank: str
    employment_type: str
    milestones: list[SummaryMilestone]


class ProfileResponse(Model):
    schema_version: Literal['1']
    document: ProfileDocument
    provenance: Provenance
    storage: Literal['browser_memory_with_explicit_encrypted_backup']
    summary: Summary
