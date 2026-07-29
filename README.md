# Shop-floor Excel importer

This command-line tool validates an Excel workbook, previews its mapped payloads,
and—only after explicit confirmation—submits each valid, previously unsubmitted
row. Because the website has no API, all submissions use Playwright browser
automation.

## Target website and integration decision

The supplied main site is `https://cpna_sfol.berryplastics.com/`, recorded in
`config/measurement-browser.yaml`. An unauthenticated probe was rejected, so the
site is protected, but the URL alone does not establish whether it uses a login
form, HTTP authentication, or organization SSO. The measurement config therefore
uses `authentication: pending` and submission deliberately stops until that value
and the login flow are confirmed. The measurement-page route and stable DOM
identifiers also remain to be collected from the authenticated page. The integration
is fixed to `integration: browser`; API submission is intentionally not implemented.

If the authenticated page proves that the site has a conventional login form, set
`authentication: form` and the verified `form_url`. Every field `target` must be a
stable CSS selector supplied by the application, preferably `[data-testid="..."]`,
`#permanent-id`, or `[name="machine_field_name"]`. Do not use translated visible
labels, generated CSS classes, DOM positions, or screen coordinates. Also configure
stable `submit_selector` and `success_selector`. Browser credentials are read from
`SHOPFLOOR_USERNAME` and `SHOPFLOOR_PASSWORD`. The bundled form-login selectors are
`[name="username"]`, `[name="password"]`, and `[type="submit"]`; adjust the adapter
for the site's documented SSO flow rather than storing credentials.

For fields that are disabled until an adjacent checkbox is selected, add an
`enable_selector` to that field. The browser adapter checks that stable checkbox,
waits for the input to become visible, verifies that it is enabled, and only then
fills it. `config/browser-example.yaml` demonstrates this for the `T 90`, `T PL`,
`E`, and `Weight` boxes. Its selectors are safe examples—not inferred production
selectors—and must be replaced with identifiers verified on the real page.

## Workbook field map

Run `python examples/generate_workbooks.py` to create the anonymized
`examples/anonymized_work_orders.xlsx` locally from the reviewed text source. The
generated workbook contains fictional values and is ignored by Git so that the
repository contains no binary files.
The mapping below is implemented in `config/example.yaml`; identifiers remain
examples until checked against the real site.

| Excel column | Required | Type/rule | Destination stable identifier |
|---|---:|---|---|
| `Record Ref` | yes | text | `[name="externalReference"]` |
| `Item Ref` | yes | text | `[name="itemCode"]` |
| `Planned Units` | yes | whole number | `[name="plannedQuantity"]` |
| `Due On` | yes | ISO date | `[name="dueDate"]` |
| `Work Area` | yes | text | `[name="workCenterCode"]` |
| `Urgency` | no | `LOW`, `NORMAL`, `HIGH` | `[name="priorityCode"]` |
| `Operator Note` | no | text | `[name="notes"]` |
| `T 90` | yes | number | `[name="t90"]` |
| `T PL` | yes | number | `[name="tPl"]` |
| `E` | yes | number | `[name="e"]` |
| `Weight` | yes | number | `[name="weight"]` |

Unknown spreadsheet columns are ignored. Missing required headers stop the import;
invalid or missing cell values produce row-numbered errors while other rows continue.

### Measurement report shown in the screenshots

Use `config/measurement-browser.yaml` with
`examples/anonymized_measurement_report.xlsx`. The report's actual headings are on
Excel row 20, so this configuration sets `header_row: 20`; data begins on row 21.
`Cav #` selects website row `C` 1–8 and is not typed into a measurement box. The
source-to-website mapping is:

| Excel heading | Website grid heading |
|---|---|
| `Cav #` | `C` (row selector) |
| `T @ 90` | `T at 90` |
| `T @ 10` | `T at PL` |
| `T avg` | `T Avg` |
| `T ovality` | `T Ovality` |
| `E @ 90` | `E AT 90` |
| `E @ 10` | `E AT PL` |
| `E avg` | `E AVG` |
| `E ovality` | `E OVALITY` |
| `Weight` | `Weight` |

The interpretation of the report's `@ 10` columns as the website's `at PL`
columns is based on the supplied screenshots and must be confirmed by the process
owner before submission. The screenshots do not reveal DOM attributes, so the
checked-in `data-testid` selectors are explicit placeholders, not claims about the
live page. Inspect the page and replace them with its real stable `id`, `name`, or
`data-testid` values. The `{row}` token is replaced with cavity number 1–8. Each
target is checked for visibility and enabled state before it is filled.

The current measurement configuration is intentionally preview-only in practice:
even with `--submit --confirm SUBMIT`, `authentication: pending` produces a row
failure without opening or modifying the website. Supply the authentication details
and an authenticated screenshot or DOM inspection of the measurement page before
changing it.

## Installation and usage

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
python examples/generate_workbooks.py

# Preview only (the default); creates a per-row CSV report.
shopfloor-import examples/anonymized_work_orders.xlsx --config config/example.yaml

# Preview the screenshot-shaped measurement report (no website writes).
shopfloor-import examples/anonymized_measurement_report.xlsx \
  --config config/measurement-browser.yaml

# After reviewing preview, supply browser credentials and explicitly authorize writes.
export SHOPFLOOR_USERNAME='service-account'
export SHOPFLOOR_PASSWORD='retrieve-this-from-a-secret-manager'
shopfloor-import input.xlsx --config config/measurement-browser.yaml \
  --submit --confirm SUBMIT
```

Install the browser with `playwright install chromium`. Use a dedicated
least-privilege service account. Keep production config
outside the repository if it contains sensitive tenant metadata (it must never
contain a password or token).

Every run writes `row,status,detail` to a timestamped file in `results/`. Validation
failures and transport failures are reported independently for every row. Successful
payloads are SHA-256 fingerprinted in `state/submitted.json`; later identical rows
are marked `duplicate` and not sent. The ledger contains hashes, not spreadsheet
values, but it should be persisted and access-controlled. Removing it disables
cross-run duplicate protection. A website-side unique constraint is also recommended
to cover crashes between remote acceptance and local ledger write.

## Security and operational checklist

1. Confirm the URL, TLS certificate, form field identifiers, and
   authentication with the system owner; do not submit using the example config.
2. Give the account only create access to the required record type and source
   secrets from an environment injector or secret manager.
3. Run preview, review every row and the generated payloads, retain the CSV report,
   then use the exact confirmation phrase.
4. Protect workbooks and result reports: failure messages and preview payloads may
   contain operational data. Rotate reports per the organization's retention policy.
5. Back up the duplicate ledger and use website-side uniqueness where available.
