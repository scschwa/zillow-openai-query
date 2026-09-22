import json
from datetime import datetime, timezone

from openai import OpenAI


ADDRESS = "3726 Harrison St NW, Washington, DC 20015"

client = OpenAI()
checked_at = datetime.now(timezone.utc).isoformat()

response = client.responses.create(
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
            "schema": {
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
                    "limitations",
                ],
                "additionalProperties": False,
            },
        }
    },
    input=f"""
Check Zillow for this exact property:

{ADDRESS}

The check is being performed at {checked_at} UTC.

Answer these two questions:

1. Is the property currently listed for rent on Zillow?
2. In Zillow's "Price history" section, has the property ever been
   listed for rent? If so, return every visible rental-listing event,
   including its date, event wording, and price.

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
""",
)

result = json.loads(response.output_text)
print(json.dumps(result, indent=2))


def collect_urls(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "url" and isinstance(child, str):
                yield child
            else:
                yield from collect_urls(child)
    elif isinstance(value, list):
        for child in value:
            yield from collect_urls(child)


all_urls = sorted(
    {
        url
        for url in collect_urls(response.model_dump())
        if "zillow.com" in url.lower()
    }
)

print("\nZillow sources consulted:")
for url in all_urls:
    print(f"- {url}")

