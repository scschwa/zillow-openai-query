# Zillow rental-status query with OpenAI

This example uses the OpenAI Responses API, GPT-5.6 Luna, and the built-in
web-search tool to inspect three Zillow properties. Each address is submitted
in a separate API request.

For each property, the script checks:

1. Whether Zillow currently lists it for rent.
2. Whether the accessible Zillow Price History shows that it was ever listed
   for rent, including visible dates and prices.
3. Whether the rental listing appears to cover the full house or condo, or a
   unit within the property such as a room, basement, floor, or ADU.

The web search is restricted to `zillow.com`. Results use a strict JSON schema
with explicit `unknown` and `unclear` states so inaccessible or conflicting
Zillow evidence is not converted into a false conclusion.

OpenAI documentation:

- [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [Web search](https://developers.openai.com/api/docs/guides/tools-web-search)
- [Responses API](https://developers.openai.com/api/reference/python/resources/responses)

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

## Run

```powershell
python .\zillow_rental_check.py
```

The script makes one billable, web-search-enabled API request per address. It
prints each structured result and writes the full SDK response object to a
deterministic JSON file under `outputs/`. A later run replaces the corresponding
file for that address.

To check different properties, edit the `ADDRESSES` list in
`zillow_rental_check.py`.

## Included test cases and latest results

These results were generated on September 22, 2026 using Python 3.12.10 and
OpenAI Python SDK 3.3.1.

| Address | Current Zillow status | Rental history | Listing scope |
| --- | --- | --- | --- |
| 3726 Harrison St NW, Washington, DC 20015 | Listed for rent at $2,000/month | Yes | Unit within property |
| 4218 38th St NW, Washington, DC 20016 | Listed for rent at $6,100/month | Yes | Entire house or condo |
| 3715 Fessenden St NW, Washington, DC 20016 | Not listed for rent | Unknown | Unclear |

### 3726 Harrison St NW

Zillow showed an active $2,000-per-month rental. The visible Price History
contained `Listed for rent` events dated June 2, 2026 and August 26, 2024, both
at $2,000.

The scope classifier returned `unit_within_property`. Although Zillow used the
generic label `House for rent`, the description advertised a roughly
950-square-foot English basement with a separate entrance, private laundry,
and a full kitchen.

[View the full raw response](outputs/3726-harrison-st-nw-washington-dc-20015-response.json)

### 4218 38th St NW

Zillow rental-search results showed the exact address as a current
$6,100-per-month rental with 3 bedrooms, 3.5 bathrooms, and 2,346 square feet.
The visible Price History contained `Listed for rent` events dated June 10,
2022 at $5,500 and May 25, 2017 at $4,500.

The scope classifier returned `entire_house_or_condo`. The listing presented a
3-bedroom house without a unit, room, basement, floor, or shared-space
identifier, and the matching property page described a single-family home.

There is an important current-status caveat: Zillow's rental-search results
showed an active listing, while the matching property-detail page displayed
`Off market`. The model favored the newer rental-search evidence but preserved
the conflict in the response limitations.

[View the full raw response](outputs/4218-38th-st-nw-washington-dc-20016-response.json)

### 3715 Fessenden St NW

The exact Zillow page stated that the property was off market and not currently
for sale or rent. Its displayed Rent Zestimate was correctly treated as an
estimate rather than an active rental listing.

The historical answer is `unknown`, not `no`. Zillow's Price History remained
in a loading state during the test, so the model could not verify whether a
`Listed for rent` event has ever appeared. This result does not establish that
the property was previously rented or that it was never rented.

The scope is also `unclear` because there is no active or historical rental
description from which to determine whether a hypothetical listing covered the
full house or only a unit.

[View the full raw response](outputs/3715-fessenden-st-nw-washington-dc-20016-response.json)

## Raw response files

The committed JSON files contain the full response objects returned by the
OpenAI Python SDK, including response metadata, web-search actions and source
URLs, the structured model output, and token usage. They do not contain the
OpenAI API key.

- [3726 Harrison Street response](outputs/3726-harrison-st-nw-washington-dc-20015-response.json)
- [4218 38th Street response](outputs/4218-38th-st-nw-washington-dc-20016-response.json)
- [3715 Fessenden Street response](outputs/3715-fessenden-st-nw-washington-dc-20016-response.json)

Zillow content and listing availability can change over time. Re-run the script
when a current answer is required.
