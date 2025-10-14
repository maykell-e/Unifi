# Scripts para Controladora UniFi

Este repositorio contiene dos scripts útiles para administrar dispositivos UniFi desde Linux. Están diseñados para automatizar tareas comunes como **actualizar dispositivos** y **adoptarlos en una controladora UniFi**.

---

## Contenido del Repositorio

| Archivo      | Descripción                                                               |
| ------------ | ------------------------------------------------------------------------- |
| `update.py`  | Script para actualizar dispositivos UniFi por SSH a la última versión.    |
| `adoptar.py` | Script para forzar la adopción de dispositivos en una controladora UniFi. |
| `ip_sw.txt`  | Lista de direcciones IP de los dispositivos a gestionar.                  |

---

## Requisitos

* Python 3
* Paquete `paramiko` (para conexiones SSH)
* Acceso SSH habilitado en los dispositivos UniFi
* Credenciales válidas de administrador

Instalar dependencias:

```bash
pip install paramiko
```

---

## Uso

### Actualizar dispositivos UniFi

```bash
python3 update.py
```

### Adoptar dispositivos en la controladora

```bash
python3 adoptar.py
```

---

## Notas

* Edita `ip_sw.txt` para añadir las IPs de los equipos a gestionar.
* Ambos scripts se pueden personalizar con usuario, contraseña y URL de controladora.
* Probado en UniFi AP/AC/AC LR y UniFi Switches.

---

## Advertencia

Usar bajo su propia responsabilidad. Este contenido es educativo y no está afiliado a Ubiquiti Networks.

---

## Autor

Repositorio creado por **maykell-e**
