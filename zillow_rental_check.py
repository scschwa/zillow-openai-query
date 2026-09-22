import json
import re
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI


ADDRESSES = [
    "3726 Harrison St NW, Washington, DC 20015",
    "4218 38th St NW, Washington, DC 20016",
    "3715 Fessenden St NW, Washington, DC 20016",
]

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = PROJECT_DIR / "outputs"

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "address": {"type": "string"},
        "checked_at_utc": {"type": "string"},
        "zillow_property_url": {"type": "string"},
        "current_status": {
            "type": "string",
            "enum": [
                "listed_for_rent",
                "not_listed_for_rent",
                "unknown",
            ],
        },
        "current_status_explanation": {"type": "string"},
        "ever_listed_for_rent": {
            "type": "string",
            "enum": ["yes", "no", "unknown"],
        },
        "rental_history": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date_as_displayed": {"type": "string"},
                    "event_as_displayed": {"type": "string"},
                    "price_as_displayed": {"type": "string"},
                },
                "required": [
                    "date_as_displayed",
                    "event_as_displayed",
                    "price_as_displayed",
                ],
                "additionalProperties": False,
            },
        },
        "listing_scope": {
            "type": "string",
            "enum": [
                "entire_house_or_condo",
                "unit_within_property",
                "unclear",
            ],
        },
        "listing_scope_explanation": {"type": "string"},
        "limitations": {"type": "string"},
    },
    "required": [
        "address",
        "checked_at_utc",
        "zillow_property_url",
        "current_status",
        "current_status_explanation",
        "ever_listed_for_rent",
        "rental_history",
        "listing_scope",
        "listing_scope_explanation",
        "limitations",
    ],
    "additionalProperties": False,
}


def slugify(address):
    return re.sub(r"[^a-z0-9]+", "-", address.lower()).strip("-")


def build_prompt(address, checked_at):
    return f"""
Check Zillow for this exact property:

{address}

The check is being performed at {checked_at} UTC.

Answer these three questions:

1. Is the property currently listed for rent on Zillow?
2. In Zillow's "Price history" section, has the property ever been
   listed for rent? If so, return every visible rental-listing event,
   including its date, event wording, and price.
3. Based on the listing details, does the rental appear to cover the entire
   house or condo at this address, or a unit within the property, such as a
   room, basement, floor, accessory dwelling unit, or in-law suite?

Important rules:

- Search for and open the best-matching Zillow property-detail page.
- Use only Zillow evidence.
- Match the complete street address, city, state, and ZIP code.
- "Listed for rent" means an active Zillow rental listing. Do not treat
  a Rent Zestimate, estimated monthly rent, or other valuation as a
  rental listing.
- For historical events, look specifically for wording such as
  "Listed for rent" in the Price history table.
- Do not infer "not listed" merely because no search result was found.
- If the property page or Price history cannot be accessed reliably,
  return "unknown" for the affected answer and explain why.
- Use "no" for ever_listed_for_rent only if you inspected the accessible
  Price history and it contains no rental-listing event.
- For listing_scope, use listing details such as the description, title,
  property type, bedroom/bathroom count, square footage, unit identifiers,
  separate or shared entrances, shared spaces, and references to an owner or
  other occupants. Explain the specific evidence supporting the classification.
- Use "entire_house_or_condo" when the listing appears to advertise the full
  residence, "unit_within_property" when it advertises only part of the
  property, and "unclear" when the accessible evidence is insufficient or
  conflicting.
- Do not treat Zillow's generic property-type label, such as "House for rent,"
  as conclusive when the description or other listing details indicate that
  only part of the property is being offered.
"""


def check_address(client, address):
    checked_at = datetime.now(timezone.utc).isoformat()

    return client.responses.create(
        model="gpt-5.6-luna",
        reasoning={"effort": "high"},
        tools=[
            {
                "type": "web_search",
                "search_context_size": "high",
                "filters": {"allowed_domains": ["zillow.com"]},
                "user_location": {
                    "type": "approximate",
                    "country": "US",
                    "region": "District of Columbia",
                    "city": "Washington",
                    "timezone": "America/New_York",
                },
            }
        ],
        tool_choice="required",
        include=["web_search_call.action.sources"],
        text={
            "format": {
                "type": "json_schema",
                "name": "zillow_rental_check",
                "strict": True,
                "schema": RESPONSE_SCHEMA,
            }
        },
        input=build_prompt(address, checked_at),
    )


def main():
    client = OpenAI()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    for index, address in enumerate(ADDRESSES, start=1):
        print(f"\n[{index}/{len(ADDRESSES)}] Checking {address}")
        response = check_address(client, address)

        output_path = OUTPUTS_DIR / f"{slugify(address)}-response.json"
        output_path.write_text(response.model_dump_json(indent=2), encoding="utf-8")

        result = json.loads(response.output_text)
        print(json.dumps(result, indent=2))
        print(f"Raw API response saved to: {output_path.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
