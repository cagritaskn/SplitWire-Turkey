<p align="center">
  <img width="auto" height="128" src="https://github.com/cagritaskn/SplitWire-Turkey/blob/main/src/SplitWireTurkey/Resources/splitwire-logo-128.png">
</p>

# <p align="center"><strong>SplitWire-Turkey</strong></p>

<div align="center">

<strong>README Multilingüe (TR/EN/RU/ES)</strong>

[![TR](https://img.shields.io/badge/README-TR-blue.svg)](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/README.md)
[![EN](https://img.shields.io/badge/README-EN-blue.svg)](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_EN.md)
[![RU](https://img.shields.io/badge/README-RU-blue.svg)](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_RU.md)
[![ES](https://img.shields.io/badge/README-ES-blue.svg)](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_ES.md)

</div>

# SplitWire-Turkey

**SplitWire-Turkey** es un proyecto de automatización de bypass DPI y túnel diseñado específicamente para usuarios de internet en Turquía. Es una aplicación de Windows de código abierto que ayuda a eludir restricciones sin afectar la velocidad de su conexión a internet. Esta herramienta le permite instalar y administrar automáticamente muchos métodos de bypass desde una sola interfaz. Dado que realiza la instalación de servicios, no necesita realizar ninguna operación adicional para acceder a las aplicaciones relevantes cuando reinicia su computadora. El código fuente de esta aplicación completamente de código abierto está disponible en la carpeta /src en el repositorio.

---

## Guía de Usuario en Video

**Puede seguir las instrucciones de instalación y uso de la guía en video preparada por Recep Baltaş a continuación:**

<a href="https://www.youtube.com/watch?v=LtwsTy568rw"> <img src="https://img.youtube.com/vi/LtwsTy568rw/maxresdefault.jpg" width="310"> </a> <br> <a href="https://www.youtube.com/watch?v=LtwsTy568rw"> <strong>Guía de Usuario en Video de SplitWire-Turkey</strong> </a>

---

# Descarga e Instalación

## Instalación con Archivo Setup (Recomendado) [![Download Setup](https://img.shields.io/badge/Download-Setup-blue?logo=windows)](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.6/SplitWire-Turkey-Setup-Windows-1.5.6.exe)
- Descargue el paquete de instalación **[SplitWire-Turkey Setup](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.6/SplitWire-Turkey-Setup-Windows-1.5.6.exe)** y realice la instalación de SplitWire-Turkey. (Si recibe una advertencia de SmartScreen "Windows protegió su computadora personal", haga clic en "Más información" y luego haga clic en "Ejecutar de todos modos", la información sobre el escaneo de virus y esta advertencia se proporciona a continuación)
- Abra la aplicación **SplitWire-Turkey**.
- Siga la sección **Guías de Uso** para usar la aplicación.

## Uso con Archivo ZIP (No Recomendado) [![Download ZIP](https://img.shields.io/badge/Download-ZIP-blue?logo=windows)](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.6/SplitWire-Turkey-ZIP-Windows-1.5.6.zip)
- Descargue el archivo **[SplitWire-Turkey ZIP](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.6/SplitWire-Turkey-ZIP-Windows-1.5.6.zip)** y extráigalo en una carpeta.
- Abra la aplicación **SplitWire-Turkey.exe** en la carpeta donde extrajo el archivo ZIP. (Si recibe una advertencia de SmartScreen "Windows protegió su computadora personal", haga clic en "Más información" y luego haga clic en "Ejecutar de todos modos", la información sobre el escaneo de virus y esta advertencia se proporciona a continuación)
- Siga la sección **Guías de Uso** para usar la aplicación.

---

# Guías de Uso

## Uso de WireSock

**Nota:** Las instalaciones en esta sección funcionan solo para la aplicación Discord (los navegadores también están incluidos si ha habilitado el túnel de navegadores). Después de realizar estas instalaciones, el método relevante comenzará a funcionar automáticamente cada vez que reinicie su sistema.

- **Instalación Estándar WS:** Instala WireSock 3.4.8.1 junto con ByeDPI-Drover; los canales de texto pasan por ByeDPI, los de voz por WireSock. (Si la opción "Túnel también para navegadores" está habilitada, también se realiza túnel para navegadores de internet)

- **Instalación Alternativa WS:** Instala solo WireSock 3.4.8.1 independiente (sin ByeDPI ni Drover); todo el tráfico se tuneliza directamente a través de WireSock. (Si la opción "Túnel también para navegadores" está habilitada, también se realiza túnel para navegadores de internet)

- **Túnel también para navegadores:** Además de la aplicación Discord; se realiza túnel para navegadores de internet populares como Chrome, Firefox, Opera, OperaGX, Brave, Vivaldi, Zen, Chromium y Edge.

- **Instalar repetidor WireSock:** Crea una tarea WTS que reinicia WireSock a intervalos regulares. Solo active e instale si experimenta problemas. Esta tarea de Windows Task Scheduler reinicia el servicio WireSock a intervalos regulares.

- **Personalizar lista de carpetas:** Puede usar esta sección si desea realizar túnel para una aplicación que no sea Discord.
  - **Agregar Carpeta:** Selecciona la carpeta donde se encuentra la aplicación que desea tunelizar y la agrega a la lista.
  - **Limpiar Lista:** Limpia la lista de carpetas.
  - **Instalación Personalizada:** Realiza la instalación usando Wgcf y WireSock para su lista de carpetas preparada.
  - **Crear Config Personalizado:** Crea un archivo de configuración para su lista de carpetas preparada.

- **Salir:** Cierra el programa.

**Nota 2:** Si la aplicación Discord se queda atascada en la pantalla "Checking for updates…", apague su módem, espere 15 segundos, luego enciéndalo nuevamente y reinicie su computadora.

---

## Uso de la Página ByeDPI

**Nota:** Las instalaciones en esta sección funcionan solo para la aplicación Discord (los navegadores también están incluidos si ha habilitado el túnel de navegadores). Después de realizar estas instalaciones, el método relevante comenzará a funcionar automáticamente cada vez que reinicie su sistema.

- **Instalación ByeDPI Split Tunneling:** Realiza bypass DPI solo para la aplicación Discord usando las herramientas ByeDPI y ProxiFyre. (Si la opción "Túnel también para navegadores" está habilitada, también se realiza bypass DPI para navegadores de internet)

- **Túnel también para navegadores:** Además de la aplicación Discord; se realiza bypass DPI para navegadores de internet populares como Chrome, Firefox, Opera, OperaGX, Brave, Vivaldi y Edge. Para cambiar la opción de túnel de navegadores y realizar la instalación nuevamente, primero debe eliminar ByeDPI haciendo clic en el botón Eliminar ByeDPI.

- **Instalación ByeDPI DLL:** Realiza bypass DPI para **SOLO** la aplicación Discord usando ByeDPI y drover (método de DLL hijacking). Este método solo funciona para la aplicación Discord, no funciona para navegadores u otros programas.

- **Eliminar ByeDPI:** Elimina ByeDPI y elimina los archivos drover.

**Nota 2:** Si la aplicación Discord se queda atascada en la pantalla "Checking for updates…", apague su módem, espere 15 segundos, luego enciéndalo nuevamente y reinicie su computadora.

---

## Uso de la Página Zapret

**Nota:** Las instalaciones en esta sección funcionan a nivel del sistema. Aunque no causan pérdida de velocidad, pueden causar problemas de conexión en algunos sitios web y aplicaciones. Después de realizar estas instalaciones, el método relevante comenzará a funcionar automáticamente cada vez que reinicie su sistema.

- **Instalación Automática Zapret:** Se encuentran parámetros ideales para su sistema y proveedor de servicios de internet usando el software de búsqueda de estrategias blockcheck de Zapret, y se proporciona bypass DPI instalando Zapret con estos parámetros.

- **Escaneo:** Selecciona la velocidad del escaneo realizado para encontrar parámetros ideales.
  - **Rápido:** Puede tomar de 2 a 10 minutos.
  - **Estándar:** Puede tomar de 5 a 30 minutos.
  - **Completo:** Puede tomar de 10 a 50 minutos.

> Estos tiempos son tiempos estimados. Pueden variar según su sistema y las políticas de inspección de paquetes de su proveedor de internet.

- **Configuración Lista:** Selecciona uno de los parámetros predeterminados para Zapret. (Gracias a Bal Porsuğu por las configuraciones listas)

- **Editar Configuración Lista:** Abre un cuadro de texto que le permite ajustar o modificar la configuración lista que seleccionó. Después de hacer ediciones en este cuadro, puede instalar o ejecutar una vez usando los parámetros en el cuadro con los botones a continuación.

- **Instalar Servicio Preconfigurado:** Instala el servicio Zapret con su configuración lista seleccionada (o la versión editada si hizo ediciones).

- **Preconfigurado Una Vez:** Ejecuta Zapret una vez con su configuración lista seleccionada (o la versión editada si hizo ediciones). Cuando cierre la ventana de consola abierta, Zapret deja de ejecutarse.

- **Eliminar Zapret:** Elimina Zapret.

**Nota 2:** Si la aplicación Discord se queda atascada en la pantalla "Checking for updates…", apague su módem, espere 15 segundos, luego enciéndalo nuevamente y reinicie su computadora.

---

## Uso de la Página Zapret2

**Nota:** Las instalaciones en esta sección funcionan a nivel del sistema. Aunque no causan pérdida de velocidad, pueden causar problemas de conexión en algunos sitios web y aplicaciones. Después de realizar estas instalaciones, el método relevante comenzará a funcionar automáticamente cada vez que reinicie su sistema.

- **Instalación Automática Zapret2:** Se encuentran parámetros ideales para su sistema y proveedor de servicios de internet usando el software de búsqueda de estrategias blockcheck de Zapret2, y se proporciona bypass DPI instalando Zapret2 con estos parámetros.

- **Escaneo:** Selecciona la velocidad del escaneo realizado para encontrar parámetros ideales.
  - **Rápido:** Puede tomar de 2 a 10 minutos.
  - **Estándar:** Puede tomar de 5 a 30 minutos.
  - **Completo:** Puede tomar de 10 a 50 minutos.

> Estos tiempos son tiempos estimados. Pueden variar según su sistema y las políticas de inspección de paquetes de su proveedor de internet.

- **Configuración Lista:** Selecciona uno de los parámetros predeterminados para Zapret2. Incluye configuraciones para Türk Telekom, Superonline, Vodafone, Türksat Kablonet, Telekom Mobil, Turkcell Mobil y Vodafone Mobil; estas también se prueban automáticamente antes de un escaneo completo en la Instalación Automática. (Gracias a Bal Porsuğu por las configuraciones listas)

- **Editar Configuración Lista:** Abre un cuadro de texto que le permite ajustar o modificar la configuración lista que seleccionó. Después de hacer ediciones en este cuadro, puede instalar o ejecutar una vez usando los parámetros en el cuadro con los botones a continuación.

- **Usar Lista de Exclusión:** Usa una lista de dominios a los que Zapret2 no aplicará bypass DPI (no los tocará). Si la desactiva, la lista se vacía temporalmente (no es necesario reiniciar Zapret2, el cambio se aplica automáticamente); al volver a activarla, la misma lista regresa.

- **Editar Lista de Exclusión:** Abre un cuadro de texto donde puede editar los dominios de la lista de exclusión. Después de editar, puede guardar los cambios haciendo clic en el botón Guardar.

- **Instalar Servicio Preconfigurado:** Instala el servicio Zapret2 con su configuración lista seleccionada (o la versión editada si hizo ediciones).

- **Preconfigurado Una Vez:** Ejecuta Zapret2 una vez con su configuración lista seleccionada (o la versión editada si hizo ediciones). Cuando cierre la ventana de consola abierta, Zapret2 deja de ejecutarse.

- **Eliminar Zapret2:** Elimina Zapret2.

**Nota 2:** Si la aplicación Discord se queda atascada en la pantalla "Checking for updates…", apague su módem, espere 15 segundos, luego enciéndalo nuevamente y reinicie su computadora.

---

## Uso de la Página GoodbyeDPI

**Nota:** La instalación en esta sección funciona a nivel del sistema. Aunque no causa pérdida de velocidad, puede causar problemas de conexión en algunos sitios web y aplicaciones. Para prevenir tales problemas, puede activar la opción "Usar lista negra". Después de realizar esta instalación, el método relevante comenzará a funcionar automáticamente cada vez que reinicie su sistema.

- **Configuración Lista:** Selecciona uno de los parámetros predeterminados para GoodbyeDPI.

- **Editar Configuración Lista:** Abre un cuadro de texto que le permite ajustar o modificar la configuración lista que seleccionó. Después de hacer ediciones en este cuadro, puede instalar o ejecutar una vez usando los parámetros en el cuadro con los botones a continuación.

- **Usar Lista Negra:** Ejecuta GoodbyeDPI solo para dominios preferidos. Por defecto, se usa lista negra para Discord, Roblox y Wattpad.

- **Editar Lista Negra:** Abre un cuadro de texto donde puede editar la lista de dominios en los que GoodbyeDPI tendrá efecto. Después de hacer la edición, puede guardar los cambios haciendo clic en el botón Guardar.

- **Instalar Servicio:** Instala el servicio GoodbyeDPI según sus preferencias especificadas arriba (Configuraciones listas y preferencias de lista negra).

- **Una Vez:** Ejecuta GoodbyeDPI una vez según sus preferencias especificadas arriba (Configuraciones listas y preferencias de lista negra). Cuando cierre la ventana de consola abierta, GoodbyeDPI deja de ejecutarse.

- **Eliminar GoodbyeDPI:** Elimina GoodbyeDPI.

**Nota 2:** Si la aplicación Discord se queda atascada en la pantalla "Checking for updates…", apague su módem, espere 15 segundos, luego enciéndalo nuevamente y reinicie su computadora.

---

## Uso de la Página de Reparación

**Nota:** Puede intentar resolver los problemas de Discord que se quedan atascados en las pantallas "Checking for updates…" y "Starting…" usando los botones en esta página. Primero, intente reparar la versión estándar de Discord instalada en su sistema usando el botón Reparar Discord, si esto falla, intente resolver su problema descargando la versión alternativa "Public Test Build" usando el botón Instalar Discord PTB. La versión Discord PTB es una variante oficial de Discord que difiere de la versión estándar de Discord distribuida desde el canal general estable en términos de rutas de actualización y descarga.

- **Reparar Discord:** Elimina completamente Discord, limpia la caché de Discord (cierra sesión de su cuenta), realiza la instalación de ByeDPI y descarga e instala Discord desde el sitio oficial de Discord nuevamente.

- **Instalar Discord PTB:** Si la versión Discord PTB está instalada, la elimina y descarga e instala la versión Discord PTB desde el sitio oficial de Discord.

- **Realizar instalación limpia para Discord PTB:** Si esta opción está activa cuando se hace clic en el botón Instalar Discord PTB, elimina el Discord estándar mientras instala Discord PTB.

- **Controles de Estado:** Muestra las versiones de Discord instaladas y realiza operaciones de instalación/eliminación y ejecución.

**Nota 2:** Si aún experimenta problemas después de la reparación, puede probar si el problema se resuelve apagando su módem, esperando 15 segundos, luego encendiéndolo nuevamente. Si su problema continúa, puede crear un informe de error desde la sección Issues de la página de Github. El enlace a la página de Github está disponible en la sección Acerca de arriba.

---

## Uso de la Página Avanzada

- **Servicios:** Muestra la lista de servicios relacionados con bypass DPI y túnel instalados por SplitWire-Turkey o por el usuario.

- **Aplicar configuraciones DNS y DoH en cada instalación:** En todas las instalaciones de métodos de bypass que se pueden realizar dentro de SplitWire-Turkey se aplica automáticamente una configuración DNS a nivel de sistema. El método que se utiliza (DnsCrypt-Proxy o Google DNS/Quad9 con DoH) se determina mediante el interruptor **Método DNS** que se encuentra justo debajo. Puede desactivar por completo la configuración automática de DNS y DoH (y, por lo tanto, la instalación de DnsCrypt-Proxy) desactivando este interruptor.

- **Método DNS (DnsCrypt-Proxy / Windows DoH):** Cuando está habilitado (y el interruptor de DNS de arriba está activado), DnsCrypt-Proxy (DNS cifrado) se instala y se inicia automáticamente en cada instalación/ejecución única/blockcheck; su servidor DNS se apunta a 127.0.0.1 y ::1 (evitando fugas de texto plano). Si ya está instalado, no se vuelve a instalar. Si se desactiva, se utiliza en su lugar el método nativo Windows DoH (Google DNS y Quad9). Los dos métodos nunca se usan al mismo tiempo.

- **Eliminar Todos los Servicios:** Elimina todos los servicios en la lista en el orden correcto, elimina los archivos drover en la carpeta de Discord y elimina la tarea WireSock Refresh Task Scheduler.

- **Revertir Configuraciones DNS y DoH:** Restablece las configuraciones DNS y DoH realizadas cuando se realiza cualquier instalación en SplitWire-Turkey, estableciendo la configuración DNS en "Automático (DHCP)" y la configuración DoH en "Desactivado".

- **Eliminar SplitWire-Turkey:** Revierte todos los cambios realizados por SplitWire-Turkey y devuelve su sistema a su estado anterior, luego inicia la herramienta de eliminación de SplitWire-Turkey.

**Nota:** El servicio WinDivert no se puede eliminar sin detener los servicios Zapret o GoodbyeDPI. Por lo tanto, se pueden solicitar múltiples confirmaciones.

---

## Opciones de Idioma / Dil Seçenekleri / Language Options / Варианты языка

- Al ejecutar SplitWire-Turkey, puede ver las opciones de idioma y cambiar el idioma del programa usando el botón del menú de idioma ubicado debajo del logotipo de SplitWire-Turkey. Actualmente, están disponibles los idiomas turco, inglés, ruso y español. [Haga clic aquí para abrir el archivo README en español.](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_ES.md)

- SplitWire-Turkey'i çalıştırdığınızda SplitWire-Turkey logosunun altında bulunan dil menüsü butonu ile dil seçeneklerini görüp programın dilini dğeiştirebilirsiniz. Şuan için Türkçe, English, Русский ve Español dilleri mevcut. [Türkçe README dosyasını açmak için buraya tıklayın](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/README.md)

- When you run SplitWire-Turkey, you can view language options and change the program's language using the language menu button located below the SplitWire-Turkey logo. Currently, Turkish, English, Русский and Español languages are available. [Click here to open English README file.](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_EN.md)

- При запуске SplitWire-Turkey вы можете просматривать языковые опции и изменять язык программы с помощью кнопки языкового меню, расположенной под логотипом SplitWire-Turkey. В настоящее время доступны турецкий, английский, русский и испанский языки. [Нажмите здесь, чтобы открыть файл README на русском языке.](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_RU.md)

---

## Notas Importantes

> [!CAUTION]
> Si está usando un software antivirus que no sea Windows Defender, es posible que necesite agregar manualmente reglas en el firewall del software antivirus relevante para permitir los archivos ejecutables llamados "Program Files\SplitWire-Turkey\res\byedpi\ciadpi.exe" y "Program Files\SplitWire-Turkey\res\proxifyre\ProxiFyre.exe". Para Windows Defender, las reglas del firewall se agregan automáticamente, no necesita realizar ninguna operación adicional. **Si el software antivirus que usa no tiene su propia función de firewall de red o si no está usando un software antivirus que no sea Windows Defender, puede ignorar esta advertencia.**

> [!NOTE]
> Dado que el uso de archivos WinDivert está bloqueado por el software antivirus llamado Kaspersky, no puede usar las pestañas GoodbyeDPI y Zapret mientras Kaspersky esté instalado en su sistema. Después de eliminar completamente Kaspersky de su sistema, descargue el archivo **[SplitWire-Turkey Setup](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.6/SplitWire-Turkey-Setup-Windows-1.5.6.exe)** y realice la instalación nuevamente, estas pestañas se activarán. También puede intentar resolver este problema agregando las carpetas C:\Program Files\SplitWire-Turkey y C:\Users\-Nombre de Usuario-\AppData\Local\SplitWire-Turkey a las excepciones de Kaspersky y descargando e instalando SplitWire-Turkey nuevamente.

> [!NOTE]
> Si experimenta problemas con los archivos WinDivert en SplitWire-Turkey v1.5 y versiones posteriores por cualquier razón, puede descargar y usar la versión anterior desde [SplitWire-Turkey Release 1.0.0](https://github.com/cagritaskn/SplitWire-Turkey/releases/tag/1.0.0).

> [!NOTE]
> También puede consultar nuestro nuevo proyecto, **[SplitCord-Turkey](https://github.com/cagritaskn/SplitCord-Turkey)**.

---

## Versión SplitWire-Turkey macOS

SplitWire-Turkey actualmente solo es compatible con el sistema operativo Windows. Para el sistema operativo macOS, puede usar la aplicación [SplitWire-Turkey-macOS](https://github.com/a-mertdincer/SplitWire-Turkey-macOS) compartida por [a-mertdincer](https://github.com/a-mertdincer).

---

## Problemas Posibles y Reporte de Errores
- Error "Register failed"/"Archivo de configuración no encontrado": Algunos proveedores de internet o el propio CloudFlare pueden bloquear el uso de su API gratuita por varias razones. La razón más común para esto es el abuso de uso excesivo regional definido como "abusive usage". Por esta razón, wgcf no puede registrarse y crear un archivo de configuración, y como resultado, se recibe el error "La operación de registro falló. Código de retorno: 1". En tal caso, desafortunadamente, los métodos de Instalación Estándar, Instalación Alternativa e Instalación Personalizada no pueden cumplir su función y no se puede crear el archivo de configuración necesario. Incluso si esta prohibición se puede eludir temporalmente usando una VPN o proxy; la clave privada y el archivo de configuración creados temporalmente tunelizados desde la API de Cloudflare solo serán válidos para la máquina tunelizada, por lo que aún impedirá el uso. Si recibe este error, puede intentar usar otros métodos.

- Error durante las instalaciones de servicios: No use esta aplicación mientras la ventana de Servicios esté abierta.

- Quedarse atascado en la pantalla "Checking for updates": Apague su módem, espere entre 15 y 30 segundos, luego reinícielo. Luego reinicie su computadora y pruebe si el problema se resuelve. Si no se resuelve, ejecute SplitWire-Turkey, abra la pestaña Reparación y haga clic en el botón Reparar Discord. Después de reiniciar su computadora, verifique si el problema se resuelve. Si aún no puede obtener resultados, ejecute SplitWire-Turkey, abra la pestaña Reparación y haga clic en el botón Instalar Discord PTB, luego después de que se complete la instalación, ejecute Discord PTB a través de Inicio > Discord PTB y verifique si el problema se resuelve.

- Quedarse atascado en la pantalla "Starting...": Ejecute SplitWire-Turkey, abra la pestaña Reparación y haga clic en el botón Reparar Discord. Después de reiniciar su computadora, verifique si el problema se resuelve. Si aún no puede obtener resultados, ejecute SplitWire-Turkey, abra la pestaña Reparación y haga clic en el botón Instalar Discord PTB, luego después de que se complete la instalación, ejecute Discord PTB a través de Inicio > Discord PTB y verifique si el problema se resuelve. Si su problema aún no se resuelve, haga clic derecho en Update.exe en la ubicación C:\Users\-Nombre de Usuario-\AppData\Local\Discord\, seleccione Propiedades, vaya a la pestaña Compatibilidad en la ventana abierta, marque la casilla "Modo de compatibilidad para este programa:", seleccione Windows 8, luego haga clic en los botones Aplicar y Aceptar, reinicie su computadora y verifique si el problema se resuelve. Si su problema aún no se resuelve, aplique el mismo paso que antes, pero esta vez marque la casilla "Modo de compatibilidad para este programa:" y seleccione Windows 7, luego haga clic en los botones Aplicar y Aceptar, reinicie su computadora y verifique si el problema se resuelve.

- Error de Discord "No se pudieron cargar los mensajes": Este problema ocurre cuando Discord mismo detecta cambios sospechosos de IP o cuando Cloudflare WARP detecta abuso. Si experimenta este problema, apague su módem, espere entre 15 y 30 segundos, luego reinícielo. Luego reinicie su computadora y pruebe si el problema se resuelve. Si aún no puede alcanzar una solución de esta manera, puede intentar restablecer la caché de Discord eliminando la carpeta C:\Users\-Nombre de Usuario-\AppData\Roaming\discord. (Este método cerrará sesión de su cuenta de Discord, se le pedirá que inicie sesión nuevamente) Si aún no puede alcanzar una solución de esta manera, pruebe otros métodos.

- Crear informes de errores: Puede ir a la [página de Issues de SplitWire-Turkey](https://github.com/cagritaskn/SplitWire-Turkey/issues) y hacer clic en el botón **New Issue** en la parte superior derecha, e informar agregando los archivos .log en la carpeta AppData\Local\SplitWire-Turkey\Logs a su informe. Puede abrir la carpeta Logs usando el botón Abrir Carpeta de Logs en la parte inferior de la página Acerca de del programa SplitWire-Turkey.

- Si sigue teniendo problemas con el cliente de Discord en sí, puede probar nuestro proyecto alternativo, **[SplitCord-Turkey](https://github.com/cagritaskn/SplitCord-Turkey)**.

---

## Eliminar SplitWire-Turkey del Sistema y Revertir Todos los Cambios
Hay muchas formas de eliminar **SplitWire-Turkey** de su sistema. Estas se pueden enumerar como usar el botón **Eliminar SplitWire-Turkey** en la pestaña **Avanzada** dentro del programa, usar el paquete de eliminación **unins000.exe** en la ubicación donde está instalado el programa, o encontrar **SplitWire-Turkey** en la ventana Agregar o quitar programas de Windows y hacer clic en el botón Eliminar de las opciones a la derecha. Siguiendo cualquiera de estas rutas, puede revertir todos los cambios y eliminar completamente SplitWire-Turkey de su sistema.

> Si está usando descargando y extrayendo el archivo ZIP; Después de usar el botón **Eliminar SplitWire-Turkey** en la pestaña **Avanzada** en **SplitWire-Turkey**, puede revertir todos los cambios y eliminar completamente SplitWire-Turkey de su sistema usando la carpeta donde extrajo el archivo ZIP y la carpeta C:\Users\-Nombre de Usuario-\AppData\Local\SplitWire-Turkey.

---

## Advertencia de Virus y SmartScreen
Dado que el programa es de código abierto, puede ver y examinar todo el código. Todo el programa es de código abierto y el código fuente se puede examinar en la carpeta /src y recompilar si se desea. Los usuarios que no quieren usar el programa y no confían en él no están obligados a usar el programa, usar el programa es a discreción del usuario.
Si lo desea, puede escanear toda la carpeta, archivo de instalación, archivo .zip o códigos fuente en un sitio como [VirusTotal](https://www.virustotal.com/gui/home/upload) y examinar los resultados, o si conoce C# o tiene un conocido que lo conoce, puede consultar para entender qué está tratando de hacer el código.

> [!NOTE]
> La advertencia **SmartScreen "Windows protegió su computadora personal"** aparece antes de ejecutar todo el software no firmado. La razón de esto es que el software debe estar sujeto a certificados internacionales de firma de código. Sin embargo, dado que este proceso de firma requiere pagos regulares basados en el tipo de cambio y soy un desarrollador independiente que no obtiene ingresos, no puedo intentar firmar el software.

> [!NOTE]
> **[Resultados de VirusTotal del archivo Setup de SplitWire-Turkey](https://www.virustotal.com/gui/file-analysis/NmI3NGJkOWE2NzM4MDI5ZWEyMDRkNGI1NDMwMzZhZWU6MTc4OTQwMzEwMw==)** Se pueden detectar informes falsos positivos de virus o malware detectados por software antivirus utilizado por un pequeño segmento de usuarios en los archivos, pero estos son software con métodos de detección poco confiables. La razón de la detección es que SplitWire-Turkey instala múltiples aplicaciones desde un solo programa y realiza muchos cambios en el sistema. (Cambios de DNS, instalación y eliminación de servicios y paquetes de programas, etc.) Le recomiendo leer las notas dadas a continuación para sus preocupaciones sobre Kaspersky.

> [!NOTE]
> **[Resultados de VirusTotal del archivo ZIP de SplitWire-Turkey](https://www.virustotal.com/gui/file-analysis/ODAxOWVjNDNiOGViZGU5MDJiOWU4MDI0YTRjMDcwZGI6MTc4OTQwMzE2Ng==)** Se pueden detectar informes falsos positivos de virus o malware detectados por software antivirus utilizado por un pequeño segmento de usuarios en los archivos, pero estos son software con métodos de detección poco confiables. La razón de la detección es que SplitWire-Turkey instala múltiples aplicaciones desde un solo programa y realiza muchos cambios en el sistema. (Cambios de DNS, instalación y eliminación de servicios y paquetes de programas, etc.) Le recomiendo leer las notas dadas a continuación para sus preocupaciones sobre Kaspersky.

> [!NOTE]
> Los archivos **WinDivert** son detectados como RiskTool por Kaspersky y algunos software antivirus. Como se puede entender del nombre de advertencia **not-a-virus:HEUR:RiskTool.Multi.WinDivert.gen**, estos archivos son; **no un virus**, dice que es una herramienta que puede ser dañina cuando se usa con archivos descargados de fuentes incorrectas. Dado que SplitWire-Turkey y todos sus complementos son de código abierto, puede rastrear y entender cómo se usa la biblioteca WinDivert. Si mira las descripciones de detección, puede ver la palabra NotAVirus. Este tipo de detección se define como una herramienta de riesgo porque la biblioteca WinDivert de código abierto utilizada por GoodbyeDPI y Zapret manipula paquetes de red en Windows. Esta biblioteca es de código abierto y se puede acceder desde [WinDivert Github](https://github.com/basil00/WinDivert). Desafortunadamente, a pesar de todos los esfuerzos de los desarrolladores de software tanto rusos como turcos, Kaspersky, que es pro-gobierno ruso, y algunas compañías de software antivirus junto con él no aceptaron los informes y objeciones, por lo que no puede ejecutar métodos que usan WinDivert si el software antivirus relevante está instalado en su sistema. Puede eliminar Kaspersky y otro software antivirus de falsos positivos de su sistema y realizar la instalación nuevamente para ejecutar métodos WinDivert, o puede descargar y usar la versión anterior sin WinDivert desde [SplitWire-Turkey Release 1.0.0](https://github.com/cagritaskn/SplitWire-Turkey/releases/tag/1.0.0).

> [!NOTE]
> **Las advertencias Not-a-virus generalmente significan que una aplicación puede ser mal utilizada cuando se prefiere.**
La advertencia not-a-virus:HEUR:RiskTool.Multi.WinDivertTool es tal advertencia.
La biblioteca WinDivert es una biblioteca de código abierto para manipular paquetes de red en sistemas operativos Windows. Esta biblioteca obtiene funcionalidad con varios software. GoodbyeDPI es uno de ellos. El propósito de GoodbyeDPI al usar la biblioteca WinDivert es evitar que el proveedor de servicios examine correctamente haciendo pequeños cambios en los paquetes de red.
Sin embargo, también se puede escribir software que pueda usar WinDivert con fines maliciosos. Por ejemplo, se puede preparar software que realiza phishing, ataques MITM o grabación/envío de entradas de usuario cambiando completamente los paquetes. **Sin embargo, esto no hace que la biblioteca WinDivert sea maliciosa. El software que usa la biblioteca WinDivert con fines maliciosos la hace maliciosa.**
El software antivirus llamado Kaspersky, correcta o incorrectamente, advierte sobre esto, pero el problema principal proviene de su sumisión a las presiones del gobierno ruso. Como saben, hay una restricción de libertad de internet en Rusia. El gobierno ejerce presión sobre las empresas bajo su techo para bloquear los métodos de bypass tanto como sea posible. La compañía llamada Kaspersky no resiste estas presiones y las acepta. Intenta prevenir métodos que ayudan a eludir de muchas maneras.
**En resumen, siempre que descargue de la fuente correcta, SplitWire-Turkey no puede dañar su computadora. Cada vez que descargue, primero mire la barra de direcciones y preste atención a la URL. Descargue y use SplitWire-Turkey solo desde [esta página](https://github.com/cagritaskn/SplitWire-Turkey/releases/).**

---

## Agradecimientos y Atribuciones

- Me gustaría agradecer a **[Recep Baltaş](https://www.youtube.com/@Techolay/)**, fundador de **[Techolay.net](https://techolay.net/sosyal/)**, que contribuyó al desarrollo del software.
- Me gustaría agradecer mucho a **[Bal Porsuğu](https://www.youtube.com/@sauali)** por la guía del **[método ByeDPI Split Tunneling](https://www.youtube.com/watch?v=rkBL_kHBfm4)**, los presets de Zapret y todos sus esfuerzos.
- **[wgcf](https://github.com/ViRb3/wgcf)** por **[ViRb3](https://github.com/ViRb3)**
- **[ProxiFyre](https://github.com/wiresock/proxifyre)** por **[Vadim Smirnov](https://github.com/wiresock)**
- **[ByeDPI](https://github.com/hufrea/byedpi)** por **[hufrea](https://github.com/hufrea/)**
- **[WireSock](https://www.wiresock.net/)** por **[Vadim Smirnov](https://github.com/wiresock)**
- **[drover](https://github.com/hdrover/discord-drover)** por **[hdrover](https://github.com/hdrover)**
- **[GoodbyeDPI](https://github.com/ValdikSS/GoodbyeDPI)** por **[ValdikSS](https://github.com/ValdikSS)**
- **[zapret](https://github.com/bol-van/zapret)** por **[bol-van](https://github.com/bol-van)**
- **[zapret2](https://github.com/bol-van/zapret2)** por **[bol-van](https://github.com/bol-van)**
- **[WinDivert](https://github.com/basil00/WinDivert)** por **[basil00](https://github.com/basil00)**
- **[SplitWire-Turkey-macOS](https://github.com/a-mertdincer/SplitWire-Turkey-macOS)** por **[a-mertdincer](https://github.com/a-mertdincer)**
- **Me gustaría agradecer mucho a otras personas que contribuyeron al proyecto y a los patrocinadores de Patreon y Github**

---

## Cómo Funciona

- Instalación Estándar, Alternativa y Personalizada
Primero, se crea un archivo de perfil con wgcf y este archivo de perfil se usa con el cliente WireSock y se inicia túnel dividido solo para Discord.

- Instalación ByeDPI Split Tunneling y ByeDPI DLL
Primero, se instala el servicio ByeDPI y en el método ST, este proxy se ejecuta para aplicaciones seleccionadas usando ProxiFyre, en el método DLL, los archivos drover aseguran que Discord use el proxy iniciado por ByeDPI en localhost con inyección automática de DLL.

- Instalación Automática Zapret
Encuentra parámetros ideales para su sistema y proveedor de internet usando tecnología blockcheck y proporciona instalación de servicio combinando estos parámetros con sus preferencias. La selección de velocidad de escaneo ajusta qué tan simple o profundo será el escaneo de parámetros.

- Instalación y Una Vez Preconfigurado Zapret
El servicio Zapret se instala o se ejecuta una vez con configuraciones listas predeterminadas (o versiones editadas si hizo ediciones).

- Instalación Automática Zapret2
Encuentra parámetros ideales para su sistema y proveedor de internet usando tecnología blockcheck2 y proporciona instalación de servicio combinando estos parámetros con sus preferencias. Las configuraciones listas para ISP turcos conocidos como Türk Telekom, Superonline y Vodafone se prueban automáticamente primero; si una funciona, no se necesita un escaneo completo. La selección de velocidad de escaneo ajusta qué tan simple o profundo será el escaneo de parámetros.

- Instalación y Una Vez Preconfigurado Zapret2
El servicio Zapret2 se instala o se ejecuta una vez con configuraciones listas predeterminadas (o versiones editadas si hizo ediciones).

- Instalación de Servicio y Una Vez GoodbyeDPI
El servicio GoodbyeDPI se instala o se ejecuta una vez con configuraciones listas predeterminadas (o versiones editadas si hizo ediciones). Si la opción Usar lista negra está activa, el bypass se aplica solo para dominios en la lista negra. (Por defecto, está configurado para Roblox, Discord y Wattpad)

- Eliminar Todos los Servicios
Los servicios de bypass instalados por SplitWire-Turkey o por el usuario se enumeran y todos se eliminan en el orden correcto. Después de esta operación, no queda ningún método de bypass en su sistema.

- Método DNS (DnsCrypt-Proxy / Windows DoH) y Revertir Configuraciones DNS y DoH
Antes de cualquier instalación que realice en SplitWire-Turkey, todos los servicios se limpian para una instalación limpia, luego se aplica uno de dos métodos (nunca ambos) según el interruptor **Método DNS** en la pestaña **Avanzada**: con el interruptor activado, se instala DnsCrypt-Proxy y su DNS se apunta a 127.0.0.1 y ::1 (DNS cifrado); con el interruptor desactivado, se activa la configuración DoH compatible con Windows 11 y se realiza la asignación DNS IPv4/IPv6 (Google DNS primario, Quad9 secundario; DoH no es compatible con Windows 10 y versiones anteriores). El botón Revertir Configuraciones DNS y DoH revierte todas estas configuraciones independientemente del método usado, devolviendo las asignaciones DNS a Automático (DHCP) y desactivando DoH.

- Eliminar SplitWire-Turkey
Este botón realiza todas las operaciones de limpieza y ejecuta el paquete de eliminación unins000.exe. Cuando se completan las operaciones iniciadas con este botón, SplitWire-Turkey se vuelve como si nunca hubiera sido instalado en su sistema antes.

---

## Recompilación

### Recompilar el Programa Usando C#
Requisitos:
- **.NET 8.0 SDK** o superior
- **Visual Studio 2022** o **Visual Studio Code**
- Sistema operativo **Windows 10/11**

### Pasos de Compilación

1. **Descargar Código Fuente**
   ```bash
   git clone https://github.com/cagritaskn/SplitWire-Turkey.git
   cd SplitWire-Turkey/src
   ```

2. **Instalar Dependencias**
   ```bash
   cd SplitWireTurkey
   dotnet restore
   ```

3. **Compilar la Aplicación**
   ```bash
   # Compilación simple
   dotnet build -c Release
   
   # O use el script batch (Recomendado)
   ..\build_simple.bat
   ```

### Recompilar el Ejecutable de Instalación Usando InnoSetup
Requisitos:
- **InnoSetup 6**
- Sistema operativo **Windows 10/11**

### Pasos de Compilación

1. **Compilar el Programa C# e Ir a la Carpeta Donde se Encuentra el SplitWire-Turkey.exe de Salida**

2. **Copiar la Carpeta Prerequisites y la Carpeta Resources y Su Contenido a Su Carpeta Actual** (No es posible cargar los archivos Desktop Runtime a la carpeta Prerequisites porque excede el límite de tamaño de archivo. En su lugar, debe colocar manualmente los archivos windowsdesktop-runtime-6.0.35-win-x64.exe y windowsdesktop-runtime-6.0.35-win-x86.exe en esta carpeta.)

3. **Abrir una Línea de Comando en Su Carpeta Actual y Compilar el Ejecutable de Instalación**
   ```bash
   iscc "SplitWire-Turkey-Setup.iss"
   ```

---

## Derechos de Autor

```
Copyright © 2025 Çağrı Taşkın

Este proyecto está licenciado bajo la licencia MIT.
Consulte el archivo LICENSE para más detalles.
```

---

## Donación y Apoyo

Usar este programa es completamente gratuito. No obtengo ningún ingreso de su uso. Sin embargo, puede apoyarme desde las direcciones de donación a continuación para que pueda continuar mi trabajo. También puede dejar una estrella para el proyecto en Github (desde la parte superior de esta página).

**GitHub Sponsor:**

[![Sponsor](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/cagritaskn)

**Patreon:**

[![Static Badge](https://img.shields.io/badge/cagritaskn-purple?logo=patreon&label=Patreon)](https://www.patreon.com/cagritaskn/membership)

---

## Descargo de Responsabilidad

**Este software está creado con fines educativos.**

- Esta herramienta es solo para educación en programación y uso personal
- No es adecuada para uso comercial
- El desarrollador no es responsable de ningún daño que pueda surgir del uso de este software
- Los usuarios usan este software bajo su propia responsabilidad
- La selección del programa llamado Discord es necesaria para probarlo en un programa que se vuelve inaccesible por DPI
- El cumplimiento de las regulaciones legales es responsabilidad del usuario
> [!IMPORTANT]
> Toda la responsabilidad legal que surja del uso de este programa pertenece a la persona que lo usa. La aplicación está escrita y editada solo con fines educativos y de investigación; usar o no usar esta aplicación bajo estas condiciones es la propia elección del usuario. Este proyecto en la plataforma Github donde se comparten códigos de código abierto está escrito y editado con fines de intercambio de información y educación en programación.


