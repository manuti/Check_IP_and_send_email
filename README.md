# Check IP and send email

Envía por email la dirección IP de una Raspberry Pi cuando se conecta a una red desconocida, para poder hacer SSH sin monitor.

Script original de [Morrolan](https://gist.github.com/Morrolan/3201741), actualizado a Python 3 y al método de autenticación actual de Gmail.

---

## Requisitos

- Python 3 (incluido en Raspberry Pi OS Bookworm y posteriores)
- Cuenta de Gmail con **verificación en dos pasos** activada

## Configuración de Gmail (App Password)

"Aplicaciones menos seguras" fue eliminado por Google en mayo 2022. Ahora hay que usar una **Contraseña de aplicación**:

1. Ve a [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Crea una nueva contraseña de aplicación (nombre libre, p.ej. "Raspberry Pi")
3. Google te da una contraseña de 16 caracteres — úsala en `SMTP_PASSWORD`

## Configuración del script

Edita las constantes al principio de `check_ip_no_auth.py`:

```python
FIXED_IP = '10.0.1.2'          # Tu IP habitual en casa; si coincide, no se envía email
IP_FILEPATH = '/home/pi/current_ip.txt'
SMTP_USERNAME = 'tu_cuenta@gmail.com'
SMTP_PASSWORD = 'xxxx xxxx xxxx xxxx'  # App Password de 16 caracteres
SMTP_RECIPIENT = 'destino@example.com'
```

## Arranque automático con systemd

1. Copia el script y el servicio a la Raspberry Pi:

```bash
cp check_ip_no_auth.py /home/pi/
sudo cp check-ip-email.service /etc/systemd/system/
```

2. Activa el servicio para que se ejecute en cada arranque:

```bash
sudo systemctl daemon-reload
sudo systemctl enable check-ip-email.service
```

3. Prueba sin reiniciar:

```bash
sudo systemctl start check-ip-email.service
sudo journalctl -u check-ip-email.service
```

El servicio espera a que la red esté disponible (`network-online.target`) antes de ejecutarse.

---

## Alternativa: cron con @reboot

Si prefieres no usar systemd:

```bash
crontab -e
```

Añade esta línea:

```
@reboot sleep 30 && /usr/bin/python3 /home/pi/check_ip_no_auth.py
```

El `sleep 30` da tiempo a que la red se configure antes de que el script se ejecute.
