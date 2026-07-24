import os
from typing import Any
from urllib.parse import urljoin

from .config import Config


def fill_enabled_field(page: Any, selector: str, value: Any, enable_selector: str | None = None) -> None:
    """Enable an optional field group and fill its stable target selector."""
    field = page.locator(selector)
    if enable_selector:
        toggle = page.locator(enable_selector)
        if not toggle.is_checked():
            toggle.check()
    field.wait_for(state="visible")
    if not field.is_enabled():
        raise RuntimeError(f"field {selector!r} is disabled after enabling its control")
    if isinstance(value, bool):
        field.set_checked(value)
    else:
        field.fill(str(value))


def submit_browser(config: Config, values: dict[str, Any]) -> str:
    if config.auth == "pending":
        raise RuntimeError(
            "website authentication is not configured; confirm whether the site uses "
            "a login form, SSO, or HTTP authentication before submitting"
        )
    if config.auth not in {"form", "none"}:
        raise RuntimeError(f"unsupported browser authentication method: {config.auth!r}")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError("install browser support: pip install . && playwright install chromium") from error
    username = os.environ.get("SHOPFLOOR_USERNAME")
    password = os.environ.get("SHOPFLOOR_PASSWORD")
    if config.auth == "form" and (not username or not password):
        raise RuntimeError("SHOPFLOOR_USERNAME and SHOPFLOOR_PASSWORD are required")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(config.website_url)
        if config.auth == "form":
            page.locator('[name="username"]').fill(username)
            page.locator('[name="password"]').fill(password)
            page.locator('[type="submit"]').click()
        page.goto(urljoin(config.website_url + "/", (config.form_url or "").lstrip("/")))
        specs_by_target = {field.target: field for field in config.fields}
        row_target = None
        if config.row_key_column:
            row_spec = next(
                (field for field in config.fields if field.column == config.row_key_column), None
            )
            if row_spec is None or row_spec.target not in values:
                raise RuntimeError(f"row key {config.row_key_column!r} is not mapped")
            row_target = row_spec.target
        row_value = values.get(row_target) if row_target else None
        for selector, value in values.items():
            if selector == row_target:
                continue
            target_selector = selector.replace("{row}", str(row_value))
            enable_selector = specs_by_target[selector].enable_selector
            if enable_selector:
                enable_selector = enable_selector.replace("{row}", str(row_value))
            fill_enabled_field(page, target_selector, value, enable_selector)
        page.locator(config.submit_selector or '[type="submit"]').click()
        if config.success_selector:
            page.locator(config.success_selector).wait_for(state="visible")
        browser.close()
    return "submitted"


def submit(config: Config, values: dict[str, Any]) -> str:
    if config.integration == "browser":
        return submit_browser(config, values)
    raise ValueError("this website has no API; integration must be 'browser'")
