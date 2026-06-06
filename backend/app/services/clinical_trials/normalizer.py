"""Normalize ClinicalTrials.gov v2 studies into internal records."""

from datetime import date
from typing import Any

from app.schemas.clinical_trials import NormalizedTrialRecord, SourceField, TrialLocation


def normalize_study(study: dict[str, Any]) -> NormalizedTrialRecord | None:
    protocol = _dict_at(study, "protocolSection")
    identification = _dict_at(protocol, "identificationModule")
    nct_id = _str_at(identification, "nctId")
    if nct_id is None:
        return None

    status = _dict_at(protocol, "statusModule")
    design = _dict_at(protocol, "designModule")
    conditions = _dict_at(protocol, "conditionsModule")
    arms = _dict_at(protocol, "armsInterventionsModule")
    sponsors = _dict_at(protocol, "sponsorCollaboratorsModule")
    locations = _dict_at(protocol, "contactsLocationsModule")
    lead_sponsor = _dict_at(sponsors, "leadSponsor")
    start_date_value = _str_at(_dict_at(status, "startDateStruct"), "date")

    normalized_locations = [
        TrialLocation(
            facility=_str_at(location, "facility"),
            city=_str_at(location, "city"),
            state=_str_at(location, "state"),
            country=_str_at(location, "country"),
        )
        for location in _list_of_dicts(_value_at(locations, "locations"))
    ]

    countries = sorted(
        {
            location.country
            for location in normalized_locations
            if location.country is not None and location.country
        }
    )

    source_fields = _source_fields(
        {
            "nct_id": (
                "protocolSection.identificationModule.nctId",
                nct_id,
            ),
            "brief_title": (
                "protocolSection.identificationModule.briefTitle",
                _str_at(identification, "briefTitle"),
            ),
            "official_title": (
                "protocolSection.identificationModule.officialTitle",
                _str_at(identification, "officialTitle"),
            ),
            "overall_status": (
                "protocolSection.statusModule.overallStatus",
                _str_at(status, "overallStatus"),
            ),
            "phases": (
                "protocolSection.designModule.phases",
                _list_of_strings(_value_at(design, "phases")),
            ),
            "study_type": (
                "protocolSection.designModule.studyType",
                _str_at(design, "studyType"),
            ),
            "start_date": (
                "protocolSection.statusModule.startDateStruct.date",
                start_date_value,
            ),
            "conditions": (
                "protocolSection.conditionsModule.conditions",
                _list_of_strings(_value_at(conditions, "conditions")),
            ),
            "interventions": (
                "protocolSection.armsInterventionsModule.interventions.name",
                _intervention_names(arms),
            ),
            "lead_sponsor": (
                "protocolSection.sponsorCollaboratorsModule.leadSponsor.name",
                _str_at(lead_sponsor, "name"),
            ),
            "sponsor_class": (
                "protocolSection.sponsorCollaboratorsModule.leadSponsor.class",
                _str_at(lead_sponsor, "class"),
            ),
            "locations": (
                "protocolSection.contactsLocationsModule.locations",
                _value_at(locations, "locations"),
            ),
            "countries": (
                "protocolSection.contactsLocationsModule.locations.country",
                countries,
            ),
        }
    )

    return NormalizedTrialRecord(
        nct_id=nct_id,
        brief_title=_str_at(identification, "briefTitle"),
        official_title=_str_at(identification, "officialTitle"),
        overall_status=_str_at(status, "overallStatus"),
        phases=_list_of_strings(_value_at(design, "phases")),
        study_type=_str_at(design, "studyType"),
        start_date=_parse_full_date(start_date_value),
        conditions=_list_of_strings(_value_at(conditions, "conditions")),
        interventions=_intervention_names(arms),
        lead_sponsor=_str_at(lead_sponsor, "name"),
        sponsor_class=_str_at(lead_sponsor, "class"),
        locations=normalized_locations,
        countries=countries,
        source_fields=source_fields,
    )


def _intervention_names(arms_module: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for intervention in _list_of_dicts(_value_at(arms_module, "interventions")):
        name = _str_at(intervention, "name")
        if name is not None:
            names.append(name)
    return names


def _source_fields(values: dict[str, tuple[str, Any]]) -> dict[str, SourceField]:
    return {
        key: SourceField(path=path, value=value)
        for key, (path, value) in values.items()
        if value not in (None, [], {})
    }


def _parse_full_date(value: str | None) -> date | None:
    if value is None or len(value) != 10:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _dict_at(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if isinstance(value, dict):
        return value
    return {}


def _value_at(parent: dict[str, Any], key: str) -> Any:
    return parent.get(key)


def _str_at(parent: dict[str, Any], key: str) -> str | None:
    value = parent.get(key)
    if isinstance(value, str) and value:
        return value
    return None


def _list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
