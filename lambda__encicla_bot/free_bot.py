from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import re
import logging

load_dotenv()

encicla_page = 'https://encicla.metropol.gov.co/Paginas/Autenticacion.aspx'
ENCICLA_USER_ID = os.environ.get("ENCICLA_USER_ID")
ENCICLA_PIN_CODE = os.environ.get("ENCICLA_PIN_CODE")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def encicla_bot():
    with sync_playwright() as p:
        try:
            logging.info("STARTING ACCESS TO THE PAGE AND FILLING IN DATA TO LOG IN")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(90000)
            page.goto(encicla_page)
            page.select_option("#DdlTipoDocumento", "CE")
            page.fill("#TxtNumeroDocumento", ENCICLA_USER_ID)
            page.fill("#TxtClave", ENCICLA_PIN_CODE)

            logging.info("LOGIN PROCESS STARTED")
            page.click('#BtnConsultar')
            page.wait_for_load_state('networkidle')

            logging.info("STARTED RELOAD PROCESS IN CASE OF TIMEOUT 504")
            number_of_reloads = 0
            max_reloads = 10
            while number_of_reloads < max_reloads:
                page.wait_for_load_state('networkidle')
                content = page.content()
                if '504 Gateway Time-out' in content:
                    logging.warning(f'504 Gateway Time-out received. Reloading page. Attempt number {number_of_reloads + 1}')
                    page.reload()
                    number_of_reloads += 1
                else:
                    break

            if number_of_reloads >= max_reloads:
                logging.error('The maximum number of unsuccessful reloads has been reached')
                browser.close()
                logging.info('BROWSER CLOSED')
                return
            elif 'Arnaldo José Cisneros Zambrano' in content:
                logging.info('Page loaded successfully')

            logging.info("SUCCESSFUL ACCESS. STARTED PROCESS OF FILLING IN DATA TO UPDATE")
            page.click('#lnkActualiza')
            page.wait_for_load_state('networkidle')
            page.fill("#TxtClaveVieja", ENCICLA_PIN_CODE)
            page.fill("#TxtClaveNueva", ENCICLA_PIN_CODE)

            if not page.is_checked("#chkTerminosCondiciones"):
                page.check("#chkTerminosCondiciones")

            logging.info("STARTING DATA UPDATE PROCESS")
            page.click('#btnActualizar')
            page.wait_for_load_state('networkidle')

            number_of_reloads = 0
            while number_of_reloads < max_reloads:
                page.wait_for_load_state('networkidle')
                content = page.content()
                if 'Se ha actualizado correctamente la información' in content:
                    logging.info("DATA UPDATED SUCCESSFULLY")
                    page.reload()
                    break
                else:
                    logging.warning('UNKNOWN ERROR. CONFIRMATION PAGE NOT FOUND')
                    number_of_reloads += 1
                    page.reload()

            logging.info("STARTING RESULT VALIDATION PROCESS")
            page.wait_for_load_state('networkidle')
            content = page.content()
            number_of_reloads = 0
            while number_of_reloads < max_reloads:
                page.wait_for_load_state('networkidle')
                content = page.content()
                if '504 Gateway Time-out' in content:
                    logging.warning(f'504 Gateway Time-out received. Reloading page. Attempt number {number_of_reloads + 1}')
                    page.reload()
                    number_of_reloads += 1
                elif '6 días' in content:
                    logging.info("VALIDATION ACHIEVED. WORK COMPLETED SUCCESSFULLY")
                    break
                else:
                    logging.warning('UNKNOWN ERROR. VALIDATION MARK NOT FOUND. CHECK RESULT MANUALLY.')
                    break

        except Exception as e:
            logging.error(f'AN EXCEPTION OCCURRED: {e}')
        finally:
            browser.close()
            logging.info('BROWSER CLOSED')

encicla_bot()