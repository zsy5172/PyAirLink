# PyAirLink

PyAirLink es una herramienta para gestionar módulos de comunicación inalámbrica a través de una interfaz web. Admite la ejecución manual de comandos AT y proporciona interfaces convenientes basadas en los comandos AT estándar definidos en `3GPP TS 27.005`, como el envío y recepción de SMS.

[中文](README.cn.md)

## Requisitos de hardware

1. El módulo debe admitir comunicación UART para comandos AT. Esta interfaz puede ser un puerto TTL físico o una conexión lógica (por ejemplo, a través de USB, Ethernet, TCP Server, etc.).
2. Necesitas un servidor (el sistema operativo no está estrictamente limitado, pero solo se ha probado en Linux) que pueda conectarse al módulo mediante un método UART estándar.
3. Si el módulo no muestra automáticamente una interfaz TTL después de conectar el USB, puedes probar los siguientes comandos (ejemplo para Linux):
   ```shell
   # Añade el ID del dispositivo USB para que la interfaz sea reconocida. Ajusta el ID (1286 4e3d en el ejemplo) según la salida de lsusb.
   sudo modprobe option
   sudo sh -c 'echo 1286 4e3d > /sys/bus/usb-serial/drivers/option1/new_id'

   # Después de este paso, podrías ver varios dispositivos /dev/ttyACM* o /dev/ttyUSB*.
   # Puedes verificar un dispositivo en particular usando una herramienta serial como minicom:
   sudo minicom -D /dev/ttyACM0
   ```

## Características

1. API web para configuración y gestión
2. Reenvío automático de SMS:
   - Correo electrónico
   - Bark
   - ServerChan (Server酱)
   - WeCom (WeChat corporativo)
3. Reinicio del módulo programado o manual
4. Envío de SMS programado o manual
5. Ejecución de comandos AT personalizados

## Contexto

PyAirLink fue diseñado para permitir fácilmente que varias tarjetas SIM permanezcan activas mientras reenvían automáticamente los mensajes SMS recibidos, sin requerir hardware costoso.

**Ventajas**
- Todas las funcionalidades están integradas en el lado del servidor, lo que facilita ejecutar múltiples instancias para gestionar varias tarjetas SIM.
- Requiere capacidades mínimas del módulo: cualquier módulo correcto podría potencialmente funcionar en cualquier red.
- No tiene requisitos de hardware especiales, manteniendo los costos bajos. El siguiente es un ejemplo de módulo (firmware AT):
  ![img.jpg](doc/Air780E.jpg)
- El módulo y el servidor no necesitan estar físicamente colocados juntos. Hay dos enfoques:
  - Usa un módulo con firmware DTU, y configura ambos lados para interactuar a través de la plataforma del fabricante o tu propia nube (usando los datos de la tarjeta SIM).
  - Usa un conversor TTL-a-red adicional para el módulo.
- No se requiere soldadura ni flasheo de hardware.

**Desventajas**
- Requiere un servidor, lo cual no es eficiente en energía en comparación con otras soluciones.
- El módulo no es portátil. Si se requiere portabilidad, una solución basada en eSIM como 5ber podría ser más adecuada.

## Uso

1. Identifica/define la ruta de la interfaz de tu módulo. En Linux, generalmente es `/dev/ttyACM*` o `/dev/ttyUSB*`; en Windows, suele ser `COM*`.
2. Confirma la velocidad de baudios.
3. Asegúrate de que el módulo esté encendido correctamente.

### Código fuente

```shell
git clone https://github.com/zsy5172/PyAirLink.git
cd PyAirLink
pip install -r requiremenets.txt
cp config.ini.template data/config.ini
# Modifica config.ini según tu entorno
python main.py
```

### Contenedor

```shell
docker run -d -p 10103:10103 -v /PyAirLink/data:/PyAirLink/data --device=/dev/ttyACM0 --name PyAirLink --restart always ghcr.io/zsy5172/pyairlink:master
```

Asegúrate de actualizar las asignaciones de rutas según tu configuración antes de ejecutar. Copia el contenido de `config.ini.template` en `/PyAirLink/data/config.ini` y modifica la configuración según sea necesario.

Una vez iniciado, puedes acceder a la interfaz web en [http://localhost:10103/docs#/](http://localhost:10103/docs#/).
