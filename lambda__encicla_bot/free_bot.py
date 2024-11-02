from playwright.sync_api import sync_playwright
import os
import re

encicla_page = 'https://encicla.metropol.gov.co/Paginas/Autenticacion.aspx'
ENCICLA_USER_ID = os.environ.get("ENCICLA_USER_ID")
ENCICLA_PIN_CODE = os.environ.get("ENCICLA_PIN_CODE")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(encicla_page)
    page.set_default_timeout(90000)
    print("Página accedida")
    page.select_option("#DdlTipoDocumento", "CE")
    page.fill("#TxtNumeroDocumento", ENCICLA_USER_ID)
    page.fill("#TxtClave", ENCICLA_PIN_CODE)
    print("Datos rellenados")
    print("Botón presionado")

    page.click('#BtnConsultar')
    page.wait_for_load_state('networkidle')
    print('Cargando página')

    number_of_reloads = 0
    max_reloads = 10

    while number_of_reloads < max_reloads:
        page.wait_for_load_state('networkidle')
        content = page.content()
        if '504 Gateway Time-out' in content:
            print('Se recibió 504 Gateway Time-out. Recargando página. Intento numero ', number_of_reloads+1)
            page.reload()
            number_of_reloads += 1
        else:
            break

    if number_of_reloads >= max_reloads:
        print('Se alcanzó el número máximo de recargas sin éxito')
        browser.close()
    elif 'Arnaldo José Cisneros Zambrano' in content:
        print('Página cargada exitosamente')
        
    print('Procedo a hacer clic en el boton de actualizar datos')

    page.click('#lnkActualiza')
    page.wait_for_load_state('networkidle')


    print('Procedo a rellenar datos de actualizacion')
    # content = page.content()
    # print(content)

    page.fill("#TxtClaveVieja", ENCICLA_PIN_CODE)
    page.fill("#TxtClaveNueva", ENCICLA_PIN_CODE)
    
    if not page.is_checked("#chkTerminosCondiciones"):
        page.check("#chkTerminosCondiciones")
        print("Checkbox T&C marcado.")
    else:
        print("El checkbox de Terminos y Condiciones ya está marcado.")

    print('Voy a hacer clic en el boton de actualizar')
    page.click('#btnActualizar')
    page.wait_for_load_state('networkidle')
    
    number_of_reloads = 0
    while number_of_reloads < max_reloads:
        page.wait_for_load_state('networkidle')
        content = page.content()
        if 'Se ha actualizado correctamente la información' in content:
            print('Datos actualizados exitosamente')
            page.reload()
            break
        else:
            print('Ocurrio un error')
            print(content)
            number_of_reloads += 1
            page.reload()

    page.wait_for_load_state('networkidle')
    content = page.content()
    if '6 días' in content:
      print('Trabajo terminado')
    else:
      print('Marca de 6 dias no encontrada')

    browser.close()
