from __future__ import annotations

from dataclasses import dataclass

from ..utils.human import human_delay
from .base import AgentContext, SiteStrategy


@dataclass
class JuiceShopProfile:
    email: str
    password: str
    security_answer: str


class JuiceShopStrategy(SiteStrategy):
    """Minimal scripted interactions for OWASP Juice Shop."""

    def __init__(
        self,
        browser: BrowserSession,
        context: AgentContext,
        profile: JuiceShopProfile,
    ) -> None:
        super().__init__(browser, context)
        self.profile = profile

    def _random_delay(self) -> int:
        return int(human_delay(0.6, 0.8) * 1000)

    def _dismiss_banners(self) -> None:
        page = self.browser.page
        for text in ["Dismiss", "Me want it!", "Accept"]:
            try:
                button = page.get_by_text(text, exact=False)
                if button.is_visible():
                    button.click(delay=self._random_delay())
                    self.context.action_logger.record("dismiss", page.url, label=text)
            except Exception:
                continue

    def _register(self) -> None:
        page = self.browser.page
        page.get_by_label("Email", exact=False).fill(self.profile.email)
        page.get_by_label("Password", exact=False).fill(self.profile.password)
        page.get_by_label("Repeat Password", exact=False).fill(self.profile.password)
        page.get_by_text("Security Question", exact=False).click()
        page.get_by_text("Your eldest siblings middle name", exact=False).first.click()
        page.get_by_placeholder("Answer", exact=False).fill(self.profile.security_answer)
        page.get_by_role("button", name="Register").click()
        self.context.action_logger.record("register", page.url, email=self.profile.email)

    def _login(self) -> None:
        page = self.browser.page
        page.get_by_label("Email", exact=False).fill(self.profile.email)
        page.get_by_label("Password", exact=False).fill(self.profile.password)
        page.get_by_role("button", name="Log in").click()
        self.context.action_logger.record("login", page.url, email=self.profile.email)

    def _add_item_to_basket(self) -> None:
        page = self.browser.page
        cards = page.locator("mat-card")
        cards.nth(0).get_by_role("button", name="Add to Basket").click(delay=self._random_delay())
        self.context.action_logger.record("add_to_cart", page.url)

    def _checkout(self) -> None:
        page = self.browser.page
        page.get_by_label("Show the shopping cart").click()
        page.get_by_role("button", name="Checkout").click()
        if page.get_by_role("button", name="Add New Address").is_visible():
            page.get_by_role("button", name="Add New Address").click()
            page.get_by_placeholder("Please provide a country.").fill("USA")
            page.get_by_placeholder("Please provide a name.").fill("Agent User")
            page.get_by_placeholder("Please provide a mobile number.").fill("5551234567")
            page.get_by_placeholder("Please provide a ZIP code.").fill("12345")
            page.get_by_placeholder("Please provide an address.").fill("123 Test Lane")
            page.get_by_placeholder("Please provide a city.").fill("Testville")
            page.get_by_placeholder("Please provide a state.").fill("CA")
            page.get_by_role("button", name="Submit").click()
            self.context.action_logger.record("add_address", page.url)
        page.get_by_role("radio", name="Home").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("radio").nth(0).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("checkbox", name="Pay with wallet").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("button", name="Place your order and pay").click()
        self.context.action_logger.record("checkout", page.url)

    def _view_orders(self) -> None:
        page = self.browser.page
        page.get_by_label("Show Orders and Payment Menu").click()
        page.get_by_role("button", name="Order History").click()
        self.context.action_logger.record("orders", page.url)

    def run(self) -> None:  # pragma: no cover - orchestrated behavior
        with self.browser.session():
            self.browser.goto(self.context.base_url)
            self._dismiss_banners()
            page = self.browser.page
            page.get_by_label("Open Sidenav").click()
            page.get_by_text("Login").click()
            self._dismiss_banners()
            page.get_by_text("Not yet a customer?").click()
            self._register()
            page.get_by_label("Open Sidenav").click()
            page.get_by_text("Login").click()
            self._login()
            self.browser.snapshot_dom("post_login")
            self._add_item_to_basket()
            self._checkout()
            self._view_orders()
            self.browser.snapshot_dom("orders")
