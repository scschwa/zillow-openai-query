# Zillow rental-status query with OpenAI

This example uses the OpenAI Responses API, GPT-5.6 Luna, and the built-in
web-search tool to inspect Zillow for a specific property's current rental
status and visible rental-listing events in its Price History.

The search tool is restricted to `zillow.com`. The response uses a strict JSON
schema and allows `unknown` when Zillow or the Price History cannot be accessed
reliably, avoiding a false negative based only on missing search results.

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
  "checked_at_utc": "2026-09-22T12:04:50.134691+00:00",
  "zillow_property_url": "https://www.zillow.com/homedetails/3726-Harrison-St-NW-Washington-DC-20015/449397_zpid/",
  "current_status": "listed_for_rent",
  "current_status_explanation": "Yes. Zillow's exact property page identifies the home as \"House for rent,\" shows an active rent of $2,000/month, and says it is available now. ([zillow.com](https://www.zillow.com/homedetails/3726-Harrison-St-NW-Washington-DC-20015/449397_zpid/))",
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
  "limitations": "The exact Zillow property-detail page and its Price history section were accessible. The visible Price history also includes a non-listing event, \"Listing removed\" on 10/7/2024, which is not included above because the requested rental-listing events are the rows explicitly worded \"Listed for rent.\" ([zillow.com](https://www.zillow.com/homedetails/3726-Harrison-St-NW-Washington-DC-20015/449397_zpid/))"
}

Zillow sources consulted:
- https://www.zillow.com/b/3726-brandywine-st-nw-washington-dc-9PbhNk/
- https://www.zillow.com/browse/homes/dc/district-of-columbia/20015/6/
- https://www.zillow.com/homedetails/3726-Harrison-St-NW-Washington-DC-20015/449397_zpid/
- https://www.zillow.com/homedetails/3726-Jenifer-St-NW-Washington-DC-20015/449315_zpid/
- https://www.zillow.com/homedetails/3726-Jocelyn-St-NW-Washington-DC-20015/449150_zpid/
- https://www.zillow.com/homedetails/3726-Military-Rd-NW-Washington-DC-20015/449080_zpid/
- https://www.zillow.com/homedetails/3726-Northampton-St-NW-Washington-DC-20015/448925_zpid/
- https://www.zillow.com/homedetails/3728-Harrison-St-NW-Washington-DC-20015/449396_zpid/
- https://www.zillow.com/washington-dc-20015/
- https://www.zillow.com/washington-dc-20015/houses/
- https://www.zillow.com/washington-dc-20015/luxury-homes/
- https://www.zillow.com/washington-dc-20015/sold/3_p/
```

## Result summary

At the test time, the exact Zillow property page reported the property as an
active rental at $2,000 per month and available immediately. Its visible Price
History contained two `Listed for rent` events:

- June 2, 2026 at $2,000
- August 26, 2024 at $2,000

The Price History also included a `Listing removed` event dated October 7, 2024.

