import re
from playwright.sync_api import Page, expect

# def test_has_title__default(page: Page):
#     page.goto("https://playwright.dev/")

#     # Expect a title "to contain" a substring.
#     expect(page).to_have_title(re.compile("Playwright"))

# def test_get_started_link__default(page: Page):
#     page.goto("https://playwright.dev/")

#     # Click the get started link.
#     page.get_by_role("link", name="Get started").click()

#     # Expects page to have a heading with the name of Installation.
#     expect(page.get_by_role("heading", name="Installation")).to_be_visible()

encicla_page = 'https://encicla.metropol.gov.co/Paginas/Autenticacion.aspx'

def test_has_title(page: Page):
  page.goto(encicla_page)
  
  expect(page).to_have_title(re.compile("Mi Cuenta - EnCicla"))
  
  page.select_option("#DdlTipoDocumento", "CE")
  page.fill("#TxtNumeroDocumento", "144897812")
  page.fill("#TxtClave", "2401")

  page.click('#BtnConsultar')