# Check IP and send email

Envía por email la dirección IP de una SBC (Raspberry Pi, Orange Pi, etc.) cuando se conecta a una red desconocida, para poder hacer SSH sin monitor.

Compatible con **Raspberry Pi OS** y **Armbian** sin modificar el script: solo cambia el fichero de configuración.

Script original de [Morrolan](https://gist.github.com/Morrolan/3201741), actualizado a Python 3, autenticación moderna de Gmail y configuración sin credenciales en el código.

---

## Requisitos

- Python 3 (incluido en Raspberry Pi OS Bookworm y Armbian)
- Cuenta de Gmail con **verificación en dos pasos** activada

## Configuración de Gmail (App Password)

"Aplicaciones menos seguras" fue eliminado por Google en mayo 2022. Ahora hay que usar una **Contraseña de aplicación**:

1. Ve a [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Crea una nueva contraseña de aplicación (nombre libre, p.ej. "Raspberry Pi")
3. Google te da una contraseña de 16 caracteres — úsala en `SMTP_PASSWORD`

## Instalación

### 1. Copiar el script

```bash
sudo cp check_ip_no_auth.py /usr/local/bin/
```

### 2. Crear el fichero de credenciales

```bash
sudo cp check-ip-email.env.example /etc/check-ip-email.env
sudo chmod 600 /etc/check-ip-email.env
sudo chown root:root /etc/check-ip-email.env
sudo nano /etc/check-ip-email.env
```

El fichero contiene toda la configuración. Los valores que debes editar:

| Variable | Descripción |
|---|---|
| `FIXED_IP` | Tu IP habitual en casa; si coincide, no se envía email |
| `NETWORK_IFACE` | Interfaz de red a monitorizar (ver tabla abajo) |
| `SMTP_USERNAME` | Tu cuenta de Gmail |
| `SMTP_PASSWORD` | App Password de 16 caracteres |
| `SMTP_RECIPIENT` | Dirección donde recibirás el email |

#### Nombre de la interfaz de red

| Sistema | Interfaz habitual | Cómo comprobarlo |
|---|---|---|
| Raspberry Pi OS | `eth0` | `ip link` |
| Armbian | `eth0`, `end0`, `enp2s0`… | `ip link` |

En Armbian ejecuta `ip link` para ver el nombre exacto de tu interfaz ethernet.

### 3. Activar el servicio systemd

```bash
sudo cp check-ip-email.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable check-ip-email.service
```

### 4. Probar sin reiniciar

```bash
sudo systemctl start check-ip-email.service
sudo journalctl -u check-ip-email.service
```

---

## Seguridad

Las credenciales **no están en el script** sino en `/etc/check-ip-email.env`, que solo root puede leer (`chmod 600`). El repositorio puede clonarse o compartirse sin exponer ninguna contraseña.

## Alternativa: cron con @reboot

Si prefieres no usar systemd, exporta las variables manualmente:

```bash
crontab -e
```

```
@reboot sleep 30 && \
  FIXED_IP=10.0.1.2 \
  NETWORK_IFACE=eth0 \
  SMTP_USERNAME=tu@gmail.com \
  SMTP_PASSWORD="xxxx xxxx xxxx xxxx" \
  SMTP_RECIPIENT=destino@example.com \
  /usr/bin/python3 /usr/local/bin/check_ip_no_auth.py
```

O carga el fichero de entorno:

```
@reboot sleep 30 && set -a && . /etc/check-ip-email.env && set +a && /usr/bin/python3 /usr/local/bin/check_ip_no_auth.py
```
