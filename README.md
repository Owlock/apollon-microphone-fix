# 🎙️ Apollon Microphone Tuning — KernelSU Module

### Fix de micrófono bajo para Xiaomi Mi 10T en ROMs AOSP/crDroid

> **Versión:** 1.0  
> **Dispositivo objetivo:** Xiaomi Mi 10T (M2007J3SY) — codename `apollo` / `apollon`  
> **SoC:** Qualcomm Snapdragon 865 (SM8250)  
> **Codec de audio:** WCD938x  
> **Autor:** dj & ANON  
> **Licencia:** Libre — úsalo, modifícalo, compártelo.

---

## 📖 ¿Qué problema resuelve?

Cuando flasheas una ROM custom como **crDroid**, **LineageOS**, **EvolutionX** o cualquier ROM basada en AOSP en tu Xiaomi Mi 10T, el micrófono se escucha extremadamente bajo. La persona al otro lado de la llamada apenas te oye, las notas de voz de WhatsApp suenan como si hablaras desde otra habitación, y las apps de transcripción de voz fallan constantemente porque no captan tu voz con suficiente potencia.

### ¿Por qué pasa esto?

Tu Xiaomi Mi 10T tiene **dos micrófonos físicos**:

| Micrófono | Ubicación | Nombre interno | Canal ADC |
| :--- | :--- | :--- | :--- |
| **Micrófono principal (bottom mic)** | Parte inferior, junto al USB-C | `ADC1` (vía `ADC0` / SoundWire) | Canal primario de voz |
| **Micrófono superior (top mic)** | Parte superior, junto al IR blaster | `ADC4` (vía `ADC3` / SoundWire, MUX `INP5`) | Referencia para cancelación de ruido |

En **MIUI** (la ROM de fábrica de Xiaomi), estos micrófonos funcionan perfecto porque Xiaomi tiene un sistema propietario de procesamiento de audio DSP que:
1. Toma la señal cruda del micrófono con ganancia baja (para evitar distorsión en ambientes ruidosos)
2. La amplifica digitalmente dentro de su propio software DSP
3. Aplica filtros de cancelación de ruido calibrados específicamente para el Mi 10T

Cuando instalas crDroid u otra ROM AOSP, **ese software DSP de Xiaomi desaparece**. Pero los archivos de configuración de audio del vendor (`mixer_paths_overlay_static.xml`) siguen con las ganancias bajísimas que Xiaomi configuró pensando que su DSP compensaría. El resultado: el micrófono capta tu voz a un volumen ridículamente bajo porque nadie está compensando la señal.

Adicionalmente, las **propiedades de Qualcomm Fluence** (el sistema de cancelación de ruido por hardware del Snapdragon 865) no están configuradas en las ROMs AOSP. Sin estas propiedades, el algoritmo Fluence toma decisiones incorrectas: cuando hablas a más de 15-20 cm del teléfono, clasifica tu voz como "ruido ambiental" y **la silencia activamente**.

---

## 🔊 Antes vs. Después — Apps que se benefician

### WhatsApp / Telegram / Signal (notas de voz)

**Antes del fix:**  
Grabas una nota de voz sosteniendo el teléfono a distancia normal (30 cm). La persona que la recibe te escucha como si estuvieras en una cueva, con un volumen tan bajo que tiene que subir el volumen al máximo y pegar la oreja al altavoz. Si hay cualquier ruido de fondo — un ventilador, una TV — tu voz se pierde completamente.

**Después del fix:**  
La nota de voz suena clara y con volumen natural. Puedes grabar con el teléfono sobre la mesa a 40-50 cm y tu voz llega nítida. El micrófono principal (`ADC1`) ahora captura con +6 dB de ganancia analógica adicional, y el volumen digital (`TX_DEC0`) sube de 87 a 92, dándote +5 dB más de headroom digital.

---

### Google Gemini / Google Assistant (transcripción de voz)

**Antes del fix:**  
Usas Gemini para dictar un mensaje largo o transcribir tus ideas. La app lucha por entender lo que dices — omite palabras, confunde sílabas, a veces se queda en silencio esperando input porque literalmente no detecta que estás hablando. Tienes que acercar el teléfono a 5 cm de tu boca para que funcione medianamente bien.

**Después del fix:**  
Gemini capta tu voz con claridad desde distancia de brazo (50-60 cm). Las transcripciones son precisas, las palabras se detectan completas, y puedes hablar a velocidad normal sin tener que exagerar la pronunciación. La diferencia es que el path `voice-rec-mic` ahora tiene `ADC1 Volume=16` y `TX_DEC0 Volume=92`, lo que significa que la señal del micrófono principal llega al motor de reconocimiento de voz con un nivel 2.5x más alto que antes.

---

### Llamadas telefónicas (Teléfono / Dialer)

**Antes del fix:**  
La persona al otro lado te dice "no te escucho", "habla más fuerte", "¿estás lejos del teléfono?". En altavoz es aún peor — prácticamente inaudible para el otro.

**Después del fix:**  
Llamadas por auricular: el path `handset-mic` ahora tiene ambos ADC (`ADC1` y `ADC4`) en 12 en vez de 6, duplicando la ganancia analógica del uplink. La persona al otro lado te escucha con volumen normal.  
Llamadas por altavoz: el path `speaker-mic` eleva `ADC4` de 6 a 12 — el micrófono superior, que es el que se usa cuando el teléfono está en modo altavoz sobre la mesa, capta tu voz con el doble de potencia.

---

### Google Meet / Zoom / Discord (videollamadas VoIP)

**Antes del fix:**  
En videollamadas tus colegas te piden que repitas constantemente. Tu avatar muestra el indicador de "hablando" de forma intermitente porque el nivel de audio está tan bajo que la app cree que no estás hablando.

**Después del fix:**  
La propiedad `vendor.voice.path.for.pcm.voip=true` fuerza a que las apps VoIP usen el path de voz calibrado del telephony HAL en vez del path genérico de captura multimedia. Esto, combinado con `persist.vendor.audio.fluence.voicecomm=true`, activa la cancelación de ruido dual-mic optimizada para comunicación de voz. Tu voz llega con nivel estable y el ruido de fondo se reduce sin silenciar tu voz.

---

### Grabadora de voz / Sound Recorder

**Antes del fix:**  
Grabas una reunión o una clase. Al reproducir, tu voz suena lejana y el audio tiene un nivel tan bajo que necesitas apps externas para amplificar el archivo.

**Después del fix:**  
El path `voice-rec-mic` es el que usa la grabadora del sistema. Con `ADC1 Volume=16` (antes 12) y `TX_DEC0 Volume=92` (antes 87), la ganancia combinada sube aproximadamente +7 dB. La grabación tiene nivel profesional sin necesidad de post-procesamiento.

---

### Cámara (grabación de video)

**Sin cambios intencionalmente.**  
El path `camcorder-dmic` ya tiene `ADC1 Volume=20` y `ADC3 Volume=20` de fábrica — estos son los valores más altos posibles sin distorsión. Este módulo **no toca el audio de la cámara** porque subirlo más causaría saturación y clipping en ambientes ruidosos (conciertos, tráfico, etc.).

---

## ⚙️ Cómo funciona el módulo — Explicación técnica

El módulo opera en **dos fases independientes**, controladas por un archivo llamado `mode`:

### Fase 1: Propiedades de Qualcomm Fluence (`mode=props`)

Al arrancar el teléfono, el script `post-fs-data.sh` se ejecuta **antes** de que el daemon de audio (`audioserver`) cargue. Usa `resetprop -n` para inyectar las siguientes propiedades directamente en la memoria del sistema de propiedades de Android:

```properties
# Activa cancelación de ruido dual-mic en llamadas normales
persist.vendor.audio.fluence.voicecall=true

# Activa cancelación de ruido en apps de comunicación (Meet, Discord, etc.)
persist.vendor.audio.fluence.voicecomm=true

# Activa beamforming del altavoz para modo hands-free
persist.vendor.audio.fluence.speaker=true

# DESACTIVA Fluence en grabación de voz (WhatsApp, Recorder, Gemini)
# Si estuviera en "true", Fluence interpreta tu voz a >20cm como ruido
# ambiental y la silencia — este es el 60% del problema original
persist.vendor.audio.fluence.voicerec=false

# Tipo de motor Fluence (estándar para SM8250)
ro.vendor.audio.sdk.fluencetype=fluence

# Fuerza a VoIP a usar el path de voz calibrado en vez del genérico
vendor.voice.path.for.pcm.voip=true
```

**¿Por qué `resetprop -n` y no `system.prop`?**  
En Android 16 con KernelSU-Next, las propiedades declaradas en `system.prop` pueden ser leídas demasiado tarde — después de que el HAL de audio ya inicializó con valores por defecto. `resetprop -n` escribe directamente en el área de memoria compartida de propiedades (`/dev/__properties__`), garantizando que cuando `vendor.audio-hal` arranque, lea los valores correctos desde el primer microsegundo.

---

### Fase 2: Ganancias de mixer (`mode=both` o `mode=gains`)

Cuando esta fase está activa, el script ejecuta un **bind mount** — una técnica del kernel Linux que "superpone" un archivo sobre otro sin modificar el original:

```
mount -o bind [archivo_modificado] /vendor/etc/mixer_paths_overlay_static.xml
```

El archivo original en la partición `/vendor` **nunca se toca**. El kernel simplemente redirige todas las lecturas de ese path hacia nuestro archivo modificado. Al desactivar el módulo o reiniciar sin él, el archivo original reaparece intacto.

#### ¿Qué cambia exactamente en cada ruta de audio?

##### `<path name="handset-mic">` — Llamadas con el teléfono en la oreja

Este path se activa cuando haces o recibes una llamada normal con el teléfono pegado a la cara.

| Control | Antes | Después | Qué hace |
| :--- | :--- | :--- | :--- |
| `ADC1 Volume` | **6** | **12** | Ganancia analógica del **micrófono inferior** (bottom mic). Es el micrófono principal que captura tu voz. Pasar de 6 a 12 añade +6 dB — la persona al otro lado te escucha al doble de volumen. |
| `ADC4 Volume` | **6** | **12** | Ganancia analógica del **micrófono superior** (top mic). En modo auricular, este micrófono actúa como referencia para la cancelación de ruido — captura el sonido ambiental para que el DSP lo reste de la señal del micrófono principal. Igualarlo con ADC1 mantiene la relación señal/ruido calibrada. |

**¿Qué micrófono importa aquí?** El **inferior** (`ADC1`). Es el que está junto a tu boca cuando hablas por teléfono. El superior (`ADC4`) solo ayuda a filtrar ruido.

---

##### `<path name="speaker-mic">` — Llamadas en altavoz

Este path se activa cuando pones una llamada en modo altavoz (speakerphone).

| Control | Antes | Después | Qué hace |
| :--- | :--- | :--- | :--- |
| `ADC4 Volume` | **6** | **12** | Ganancia analógica del **micrófono superior** (top mic). En modo altavoz, el teléfono suele estar sobre la mesa o a distancia. El micrófono superior se convierte en el principal para capturar tu voz. +6 dB de ganancia analógica. |

**¿Qué micrófono importa aquí?** El **superior** (`ADC4`). Cuando el teléfono está plano sobre una mesa, el mic superior tiene línea directa hacia tu boca.

---

##### `<path name="voice-rec-mic">` — WhatsApp, grabadora, Gemini, transcripción

Este es el path más importante para el uso diario. Se activa cuando cualquier app solicita el micrófono para grabación de voz (no llamada).

| Control | Antes | Después | Qué hace |
| :--- | :--- | :--- | :--- |
| `ADC1 Volume` | **12** | **16** | Ganancia analógica del **micrófono inferior**. Ya estaba más alto que en llamadas (12 vs 6), pero sigue siendo insuficiente sin el DSP de MIUI. Lo subimos a 16 (+4 dB analógicos adicionales). |
| `TX_DEC0 Volume` | **87** | **92** | Ganancia **digital** del decimator 0. Este control amplifica la señal después de la conversión analógica-digital. De 87 a 92 añade +5 dB digitales. El valor por defecto del chip WCD938x es 84 (unidad); 92 es seguro — distorsión comienza cerca de 100. |

**¿Qué micrófono importa aquí?** El **inferior** (`ADC1`). Las apps de voz usan el micrófono principal por defecto. Este path NO usa cancelación dual-mic (solo 1 canal), por eso `persist.vendor.audio.fluence.voicerec=false` es crítico — evita que Fluence mutee tu voz al no tener referencia de ruido.

---

##### `<path name="camcorder-dmic">` — Cámara de video

**No se modifica.** Hereda de `handset-dmic-dual-adc` donde `ADC1=20` y `ADC3=20`. Estos son los valores máximos seguros. Subirlos causaría clipping audible en cualquier ambiente con volumen moderado.

---

## 📱 Compatibilidad

### Dispositivos compatibles

| Dispositivo | Modelo | Codename | Compatible |
| :--- | :--- | :--- | :--- |
| **Xiaomi Mi 10T** | M2007J3SY | `apollo` / `apollon` | ✅ **Sí** — Probado y calibrado |
| **Xiaomi Mi 10T Pro** | M2007J3SG | `apollo` / `apollon` | ✅ **Sí** — Comparte el mismo árbol de audio y codec WCD938x |
| **Redmi K30S Ultra** | M2007J3SC | `apollo` | ✅ **Sí** — Mismo hardware de audio, mismo mixer_paths |
| Otros SM8250 Xiaomi (POCO F3, Mi 11, etc.) | Varios | `alioth`, `venus`, etc. | ❌ **No** — Tienen rutas de mixer y codec diferentes. El módulo valida el codename al arrancar y se niega a ejecutar en dispositivos no-apollo. |

### Sistemas operativos compatibles

| ROM | Compatible | Notas |
| :--- | :--- | :--- |
| **crDroid 12.x** (Android 16) | ✅ | Probado en builds de MurtazaKolachi |
| **crDroid 11.x** (Android 15) | ✅ | Mismo device tree |
| **LineageOS 22.x / 23.x** | ✅ | Usa el mismo `mixer_paths_overlay_static.xml` del árbol `apollon` |
| **EvolutionX** | ✅ | Basado en el mismo árbol AOSP de apollon |
| **RisingOS / AlphaDroid** | ✅ | Mismo device tree |
| **MIUI / HyperOS** | ❌ | **No lo necesita** — MIUI tiene su propio DSP que compensa las ganancias bajas. Instalarlo en MIUI causaría volumen excesivo y distorsión. |

### Versiones de KernelSU compatibles

| Solución root | Compatible | Notas |
| :--- | :--- | :--- |
| **KernelSU-Next** (recomendado) | ✅ | Probado. Soporta `resetprop -n` y bind mounts en `post-fs-data`. |
| **KernelSU** (original, weishu) | ✅ | Mismo mecanismo de módulos. |
| **Magisk** (24.0+) | ✅ | Compatible — Magisk usa la misma estructura de módulos (`module.prop` + `post-fs-data.sh`). `resetprop` está incluido en Magisk. |
| **APatch** | ⚠️ | Debería funcionar, pero no probado. APatch soporta módulos estilo Magisk. |
| **Sin root** | ❌ | **No funciona** — Se requiere root para `resetprop` y para `mount -o bind` sobre `/vendor`. |

### Requisitos del sistema

- **Bootloader desbloqueado** (necesario para tener root)
- **Root activo** con KernelSU-Next, KernelSU, o Magisk
- **Kernel con OverlayFS** habilitado (`CONFIG_OVERLAY_FS=y`) — todos los kernels de apollon para ROMs custom lo incluyen
- **Android 12 o superior** — por la estructura de particiones dinámicas y vendor EROFS
- **Partición vendor con `mixer_paths_overlay_static.xml`** presente en `/vendor/etc/` — el módulo verifica su existencia antes de montar

---

## 📦 Contenido del .zip

```
apollon_mic_tuning_v1.0.zip
│
├── module.prop                              # Metadatos del módulo
├── post-fs-data.sh                          # Script principal (se ejecuta al arrancar)
├── service.sh                               # Verificación de montaje post-arranque
├── mode                                     # Archivo de control: "props", "both", o "gains"
│
└── files/
    ├── mixer_paths_overlay_static.xml       # Archivo modificado (ganancias calibradas)
    └── mixer_paths_overlay_static_stock.xml # Backup del archivo original de tu teléfono
```

---

## 🚀 Instalación

### Paso 1 — Flashear el módulo
1. Copia `apollon_mic_tuning_v1.0.zip` a tu teléfono (ya está en `/sdcard/Download/` si lo pusimos vía ADB)
2. Abre la app de **KernelSU-Next** (o Magisk Manager)
3. Ve a **Módulos** → **Instalar desde almacenamiento**
4. Selecciona `apollon_mic_tuning_v1.0.zip`
5. Espera a que termine y **reinicia**

### Paso 2 — Probar en modo `props` (por defecto)
Después del reinicio, el módulo arranca en modo `props` — solo inyecta las propiedades de Fluence sin tocar ganancias. Prueba:
- Graba una nota de voz en WhatsApp a 30 cm de distancia
- Haz una llamada normal y una en altavoz
- Usa Gemini o Google Assistant para transcribir algo

Si el micrófono ya suena bien, **déjalo así**. Este modo es el más conservador y seguro.

### Paso 3 — Activar `both` si necesitas más volumen
Si las propiedades solas no son suficientes, activa la fase de ganancias:

```bash
# Desde una terminal con root (Termux, terminal de crDroid, o adb con root):
su -c 'echo both > /data/adb/modules/apollon_mic_tuning/mode'
reboot
```

### Cambiar de modo
Edita el archivo `mode` dentro del directorio del módulo. Las opciones son:
- **`props`** — Solo propiedades de Fluence (más seguro)
- **`both`** — Propiedades + ganancias de mixer (máximo volumen)
- **`gains`** — Solo ganancias de mixer, sin propiedades

---

## ↩️ Desinstalación / Rollback

- **Desde la app:** Abre KernelSU-Next → Módulos → Desmarca o elimina "Apollon Microphone Tuning" → Reinicia
- **Desde terminal:** `su -c 'touch /data/adb/modules/apollon_mic_tuning/disable' && reboot`
- **Emergencia:** Si el teléfono entra en bootloop (extremadamente improbable), arranca en recovery y borra la carpeta `/data/adb/modules/apollon_mic_tuning/`

**El archivo original de vendor NUNCA se modifica.** El bind mount es volátil — desaparece al reiniciar sin el módulo. El backup de tu XML original está incluido en `files/mixer_paths_overlay_static_stock.xml`.

---

## ⚠️ Qué puede salir mal

| Problema | Causa | Solución |
| :--- | :--- | :--- |
| **Distorsión o clipping** en notas de voz | `ADC1 Volume` demasiado alto para tu ambiente | Baja `ADC1 Volume` a `14` en el XML modificado (edita `files/mixer_paths_overlay_static.xml`) |
| **Eco en llamadas con altavoz** | El mic superior capta el audio del altavoz | Cambia `mode` a `props` (desactiva ganancias) o baja `ADC4 Volume` a `10` |
| **Micrófono muteado** | XML con error de sintaxis (tag no cerrado) | Restaura el XML stock: `su -c 'cp .../files/mixer_paths_overlay_static_stock.xml .../files/mixer_paths_overlay_static.xml' && reboot` |
| **El módulo no hace efecto** | El archivo `mode` tiene un espacio o newline extra | Asegúrate de que el archivo contiene exactamente `props`, `both`, o `gains` sin espacios |

---

## 🔬 Valores de referencia — Rango seguro del WCD938x

| Control | Mínimo | Default del chip | Nuestro valor | Máximo seguro | Distorsión |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ADC1 Volume` | 0 | 12 | 12-16 | 18 | >18 introduce hiss |
| `ADC4 Volume` | 0 | 12 | 12 | 18 | >18 introduce hiss |
| `TX_DEC0 Volume` | 0 | 84 (unidad) | 92 | 96 | >96 satura el DSP |

---

*Construido con datos reales extraídos vía ADB del dispositivo M2007J3SY serial 36ea8477, crDroid 12.11, kernel 4.19.325-cip131-st15 con CONFIG_KSU=y.*
