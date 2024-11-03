from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import re

load_dotenv()

encicla_page = 'https://encicla.metropol.gov.co/Paginas/Autenticacion.aspx'
ENCICLA_USER_ID = os.environ.get("ENCICLA_USER_ID")
ENCICLA_PIN_CODE = os.environ.get("ENCICLA_PIN_CODE")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def lambda_handler():
    try:
        with sync_playwright() as p:

            logging.info("INICIANDO ACCESO A LA PAGINA Y LLENADO DE DATOS PARA INICIAR SESION")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(90000)
            page.goto(encicla_page)
            page.select_option("#DdlTipoDocumento", "CE")
            page.fill("#TxtNumeroDocumento", ENCICLA_USER_ID)
            page.fill("#TxtClave", ENCICLA_PIN_CODE)

            logging.info("INICIADO PROCESO DE INICIO DE SESION")
            page.click('#BtnConsultar')
            page.wait_for_load_state('networkidle')

            logging.info("INICIADO PROCESO DE RECARGA EN CASO DE TIMEOUT 504")
            number_of_reloads = 0
            max_reloads = 10
            while number_of_reloads < max_reloads:
                page.wait_for_load_state('networkidle')
                content = page.content()
                if '504 Gateway Time-out' in content:
                    logging.warning(f'Se recibió 504 Gateway Time-out. Recargando página. Intento número {number_of_reloads + 1}')
                    page.reload()
                    number_of_reloads += 1
                else:
                    break

            if number_of_reloads >= max_reloads:
                logging.error('Se alcanzó el número máximo de recargas sin éxito')
                browser.close()
                logging.info('NAVEGADOR CERRADO')
                return
            elif 'Arnaldo José Cisneros Zambrano' in content:
                logging.info('Página cargada exitosamente')

            logging.info("ACCESO EXITOSO. INICIADO PROCESO DE LLENADO DE DATOS PARA ACTUALIZAR")
            page.click('#lnkActualiza')
            page.wait_for_load_state('networkidle')
            page.fill("#TxtClaveVieja", ENCICLA_PIN_CODE)
            page.fill("#TxtClaveNueva", ENCICLA_PIN_CODE)

            if not page.is_checked("#chkTerminosCondiciones"):
                page.check("#chkTerminosCondiciones")

            logging.info("INICIANDO PROCESO DE ACTUALIZACION DE DATOS")
            page.click('#btnActualizar')
            page.wait_for_load_state('networkidle')

            number_of_reloads = 0
            while number_of_reloads < max_reloads:
                page.wait_for_load_state('networkidle')
                content = page.content()
                if 'Se ha actualizado correctamente la información' in content:
                    logging.info("DATOS ACTUALIZADOS EXITOSAMENTE")
                    page.reload()
                    break
                else:
                    logging.warning('ERROR DESCONOCIDO. PAGINA DE CONFIRMACION NO ENCONTRADA')
                    number_of_reloads += 1
                    page.reload()

            logging.info("INICIANDO VALIDACION")
            page.wait_for_load_state('networkidle')
            content = page.content()
            if '6 días' in content:
                logging.info("VALIDACION LOGRADA. TRABAJO TERMINADO CON EXITO")
            else:
                logging.warning('ERROR DESCONOCIDO. MARCA DE VALIDACION NO ENCONTRADA')

    except Exception as e:
        logging.error(f'OCURRIO UNA EXCEPCION: {e}')
    finally:
        browser.close()
        logging.info('NAVEGADOR CERRADO')