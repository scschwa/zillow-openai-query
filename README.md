# Zillow rental-status query with OpenAI

This example uses the OpenAI Responses API, GPT-5.6 Luna, and the built-in
web-search tool to inspect Zillow for a specific property's current rental
status, visible rental-listing events in its Price History, and whether the
listing covers the full residence or a unit within the property.

The search tool is restricted to `zillow.com`. The response uses a strict JSON
schema and allows `unknown` or `unclear` when Zillow, the Price History, or the
relevant listing details cannot be accessed reliably.

OpenAI documentation:

- [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [Web search](https://developers.openai.com/api/docs/guides/tools-web-search)

## Setup

Requirements:

- Python 3.10 or later
- An OpenAI API key with API billing and model access

Create and activate a virtual environment, then install the dependency:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set `OPENAI_API_KEY` in the environment. The SDK reads this variable
automatically:

```powershell
$env:OPENAI_API_KEY = "your-api-key"
```

Do not commit the API key or store it directly in the script.

Run the example:

```powershell
python .\zillow_rental_check.py
```

Each run performs a billable API request and may incur a web-search tool charge.
Results can change as Zillow updates the listing or restricts page access.

## Test execution

The script was tested successfully on September 22, 2026 using Python 3.12.10
and OpenAI Python SDK 3.3.1. The API returned the following exact console output:

```text
{
  "address": "3726 Harrison St NW, Washington, DC 20015",
  "checked_at_utc": "2026-09-22T12:19:37.566629+00:00",
  "zillow_property_url": "https://www.zillow.com/homedetails/3726-Harrison-St-NW-Washington-DC-20015/449397_zpid/",
  "current_status": "listed_for_rent",
  "current_status_explanation": "Yes. Zillow's exact-address property page shows \u201cHouse for rent,\u201d $2,000/mo, \u201cAvailable now,\u201d and an active application/listing interface. ([zillow.com](https://www.zillow.com/homedetails/3726-Harrison-St-NW-Washington-DC-20015/449397_zpid/))",
  "ever_listed_for_rent": "yes",
  "rental_history": [
    {
      "date_as_displayed": "6/2/2026",
      "event_as_displayed": "Listed for rent",
      "price_as_displayed": "$2,000$2/sqft"
    },
    {
      "date_as_displayed": "8/26/2024",
      "event_as_displayed": "Listed for rent",
      "price_as_displayed": "$2,000$2/sqft"
    }
  ],
  "listing_scope": "unit_within_property",
  "listing_scope_explanation": "The listing describes the offering as a \u201cBright Spacious English Basement,\u201d approximately 950 sq ft, with a private washer-dryer, private/separate central AC/heat, and a separate/private entrance. Those details indicate that only a basement unit within the single-family property is being rented, not the entire house. ([zillow.com](https://www.zillow.com/homedetails/3726-Harrison-St-NW-Washington-DC-20015/449397_zpid/))",
  "limitations": "Assessment is based solely on the accessible Zillow property-detail page and its visible Price history section. Zillow's page identifies the property as a single-family residence, but the rental description specifically advertises the English-basement unit."
}

Zillow sources consulted:
- https://www.zillow.com/b/3726-brandywine-st-nw-washington-dc-9PbhNk/
- https://www.zillow.com/homedetails/3718-Harrison-St-NW-Washington-DC-20015/449404_zpid/
- https://www.zillow.com/homedetails/3723-Harrison-St-NW-Washington-DC-20015/35725302_zpid/
- https://www.zillow.com/homedetails/3726-Harrison-St-NW-Washington-DC-20015/449397_zpid/
- https://www.zillow.com/homedetails/3726-Jenifer-St-NW-Washington-DC-20015/449315_zpid/
- https://www.zillow.com/homedetails/3726-Jocelyn-St-NW-Washington-DC-20015/449150_zpid/
- https://www.zillow.com/homedetails/3726-Military-Rd-NW-Washington-DC-20015/449080_zpid/
- https://www.zillow.com/homedetails/3726-Northampton-St-NW-Washington-DC-20015/448925_zpid/
- https://www.zillow.com/homedetails/3726-Warren-St-NW-Washington-DC-20016/449748_zpid/
- https://www.zillow.com/homedetails/3728-Harrison-St-NW-Washington-DC-20015/449396_zpid/
- https://www.zillow.com/homedetails/3731-Harrison-St-NW-Washington-DC-20015/449374_zpid/
- https://www.zillow.com/washington-dc-20015/sold/2_p/
```

## Result summary

At the test time, the exact Zillow property page reported the property as an
active rental at $2,000 per month and available immediately. Its visible Price
History contained two `Listed for rent` events:

- June 2, 2026 at $2,000
- August 26, 2024 at $2,000

The listing was classified as `unit_within_property`. Its description advertises
a roughly 950-square-foot English basement with a separate entrance, private
laundry, and separate heating and air conditioning, rather than the full house.
