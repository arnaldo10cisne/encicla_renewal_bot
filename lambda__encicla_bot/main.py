import os
import re
from playwright.sync_api import Page

encicla_page = 'https://encicla.metropol.gov.co/Paginas/Autenticacion.aspx'
ENCICLA_USER_ID = os.environ.get("ENCICLA_USER_ID")
ENCICLA_PIN_CODE = os.environ.get("ENCICLA_PIN_CODE")

def lambda_handler():
  page.goto(encicla_page)
  page.select_option("#DdlTipoDocumento", "CE")
  page.fill("#TxtNumeroDocumento", ENCICLA_USER_ID)
  page.fill("#TxtClave", ENCICLA_PIN_CODE)
  print(page.content())