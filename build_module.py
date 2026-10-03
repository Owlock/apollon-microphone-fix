import os
import zipfile
import hashlib

workspace = os.path.dirname(os.path.abspath(__file__))
dump_file = os.path.join(workspace, "apollon_mic_tuning", "files", "mixer_paths_overlay_static_stock.xml")
if not os.path.exists(dump_file):
    dump_file = os.path.join(workspace, "device_dump", "mixer_paths_overlay_static.xml")

with open(dump_file, "r", encoding="utf-8") as f:
    stock_content = f.read()

# Verify target blocks exist in stock
assert '<path name="handset-mic">' in stock_content
assert '<path name="speaker-mic">' in stock_content
assert '<path name="voice-rec-mic">' in stock_content

# Perform exact surgical replacements
# 1. handset-mic
old_handset = '''    <path name="handset-mic">
        <ctl name="TX_CDC_DMA_TX_3 Channels" value="Two" />
        <ctl name="TX DEC1 MUX" value="SWR_MIC"/>
        <ctl name="TX SMIC MUX1" value="ADC0" />
        <ctl name="TX_AIF1_CAP Mixer DEC1" value="1" />
        <ctl name="ADC1_MIXER Switch" value="1" />
        <ctl name="ADC1 Volume" value="6" />
        <ctl name="TX DEC0 MUX" value="SWR_MIC"/>
        <ctl name="TX SMIC MUX0" value="ADC3" />
        <ctl name="ADC4_MIXER Switch" value="1" />
        <ctl name="TX_AIF1_CAP Mixer DEC0" value="1" />
        <ctl name="ADC4 MUX" value="INP5" />
        <ctl name="ADC4 Volume" value="6" />
    </path>'''

new_handset = '''    <path name="handset-mic">
        <ctl name="TX_CDC_DMA_TX_3 Channels" value="Two" />
        <ctl name="TX DEC1 MUX" value="SWR_MIC"/>
        <ctl name="TX SMIC MUX1" value="ADC0" />
        <ctl name="TX_AIF1_CAP Mixer DEC1" value="1" />
        <ctl name="ADC1_MIXER Switch" value="1" />
        <ctl name="ADC1 Volume" value="12" />
        <ctl name="TX DEC0 MUX" value="SWR_MIC"/>
        <ctl name="TX SMIC MUX0" value="ADC3" />
        <ctl name="ADC4_MIXER Switch" value="1" />
        <ctl name="TX_AIF1_CAP Mixer DEC0" value="1" />
        <ctl name="ADC4 MUX" value="INP5" />
        <ctl name="ADC4 Volume" value="12" />
    </path>'''

# 2. speaker-mic
old_speaker = '''    <path name="speaker-mic">
        <ctl name="TX DEC0 MUX" value="SWR_MIC"/>
        <ctl name="TX SMIC MUX0" value="ADC3" />
        <ctl name="TX_CDC_DMA_TX_3 Channels" value="One" />
        <ctl name="TX_AIF1_CAP Mixer DEC0" value="1" />
        <ctl name="ADC4_MIXER Switch" value="1" />
        <ctl name="ADC4 MUX" value="INP5" />
        <ctl name="ADC4 Volume" value="6" />
    </path>'''

new_speaker = '''    <path name="speaker-mic">
        <ctl name="TX DEC0 MUX" value="SWR_MIC"/>
        <ctl name="TX SMIC MUX0" value="ADC3" />
        <ctl name="TX_CDC_DMA_TX_3 Channels" value="One" />
        <ctl name="TX_AIF1_CAP Mixer DEC0" value="1" />
        <ctl name="ADC4_MIXER Switch" value="1" />
        <ctl name="ADC4 MUX" value="INP5" />
        <ctl name="ADC4 Volume" value="12" />
    </path>'''

# 3. voice-rec-mic
old_voicerec = '''    <path name="voice-rec-mic">
        <ctl name="TX DEC0 MUX" value="SWR_MIC"/>
        <ctl name="TX SMIC MUX0" value="ADC0" />
        <ctl name="TX_CDC_DMA_TX_3 Channels" value="One" />
        <ctl name="TX_AIF1_CAP Mixer DEC0" value="1" />
        <ctl name="ADC1_MIXER Switch" value="1" />
        <ctl name="ADC1 Volume" value="12" />
        <ctl name="TX_DEC0 Volume" value="87" />
    </path>'''

new_voicerec = '''    <path name="voice-rec-mic">
        <ctl name="TX DEC0 MUX" value="SWR_MIC"/>
        <ctl name="TX SMIC MUX0" value="ADC0" />
        <ctl name="TX_CDC_DMA_TX_3 Channels" value="One" />
        <ctl name="TX_AIF1_CAP Mixer DEC0" value="1" />
        <ctl name="ADC1_MIXER Switch" value="1" />
        <ctl name="ADC1 Volume" value="16" />
        <ctl name="TX_DEC0 Volume" value="92" />
    </path>'''

mod_content = stock_content.replace(old_handset, new_handset)
assert mod_content != stock_content, "handset-mic replacement failed"
mod_content2 = mod_content.replace(old_speaker, new_speaker)
assert mod_content2 != mod_content, "speaker-mic replacement failed"
mod_content3 = mod_content2.replace(old_voicerec, new_voicerec)
assert mod_content3 != mod_content2, "voice-rec-mic replacement failed"

# Create module folder
mod_dir = os.path.join(workspace, "apollon_mic_tuning")
files_dir = os.path.join(mod_dir, "files")
os.makedirs(files_dir, exist_ok=True)

# Write modified and stock XML
with open(os.path.join(files_dir, "mixer_paths_overlay_static.xml"), "w", encoding="utf-8", newline="\n") as f:
    f.write(mod_content3)

with open(os.path.join(files_dir, "mixer_paths_overlay_static_stock.xml"), "w", encoding="utf-8", newline="\n") as f:
    f.write(stock_content)

# Write mode file (default: props)
with open(os.path.join(mod_dir, "mode"), "w", encoding="utf-8", newline="\n") as f:
    f.write("props\n")

# Write module.prop
module_prop = """id=apollon_mic_tuning
name=Apollon Microphone Tuning (crDroid 12.11)
version=1.0
versionCode=100
author=dj & ANON
description=Fixes low mic volume on apollo/apollon (crDroid 12.11 / Android 16) via selective MIUI Fluence properties and optional calibrated mixer gains.
"""
with open(os.path.join(mod_dir, "module.prop"), "w", encoding="utf-8", newline="\n") as f:
    f.write(module_prop)

# Write post-fs-data.sh
post_fs_data = """#!/system/bin/sh
MODDIR="${0%/*}"
MODE="$(cat "$MODDIR/mode" 2>/dev/null | tr -d '[:space:]')"
LOG="$MODDIR/mount.log"
DST="/vendor/etc/mixer_paths_overlay_static.xml"
SRC="$MODDIR/files/mixer_paths_overlay_static.xml"

exec >>"$LOG" 2>&1
echo "=== $(date) ==="
echo "Active mode: $MODE"

DEVICE="$(getprop ro.product.device)"
PRODUCT="$(getprop ro.product.vendor.device)"

case "$DEVICE:$PRODUCT" in
    *apollo*|*apollon*)
        echo "Device verified: $DEVICE ($PRODUCT)"
        ;;
    *)
        echo "Refusing unsupported device: $DEVICE / $PRODUCT"
        exit 1
        ;;
esac

# Phase 1: Apply MIUI vendor Fluence & VoIP properties
if [ "$MODE" = "props" ] || [ "$MODE" = "both" ]; then
    echo "Applying Qualcomm Fluence & VoIP properties via resetprop -n..."
    resetprop -n ro.vendor.audio.sdk.fluencetype fluence
    resetprop -n persist.vendor.audio.fluence.voicecall true
    resetprop -n persist.vendor.audio.fluence.voicecomm true
    resetprop -n persist.vendor.audio.fluence.speaker true
    resetprop -n persist.vendor.audio.fluence.voicerec false
    resetprop -n persist.vendor.audio.fluence.tmic.enabled false
    resetprop -n vendor.audio.feature.fluence.enable true
    resetprop -n vendor.voice.path.for.pcm.voip true
    resetprop -n vendor.audio.feature.compr_voip.enable false
    echo "Properties applied successfully."
fi

# Phase 2: Bind-mount calibrated mixer overlay
if [ "$MODE" = "gains" ] || [ "$MODE" = "both" ]; then
    echo "Applying mixer overlay bind mount..."
    if [ ! -f "$DST" ]; then
        echo "Missing target: $DST"
        exit 1
    fi
    if [ ! -f "$SRC" ]; then
        echo "Missing replacement: $SRC"
        exit 1
    fi

    chmod 0644 "$SRC"
    chown 0:0 "$SRC"

    if command -v chcon >/dev/null 2>&1; then
        chcon --reference="$DST" "$SRC" 2>/dev/null || chcon u:object_r:vendor_configs_file:s0 "$SRC" 2>/dev/null
    fi

    mount -o bind "$SRC" "$DST" || {
        echo "Bind mount failed"
        exit 1
    }
    echo "Mounted successfully:"
    grep "mixer_paths_overlay_static.xml" /proc/self/mountinfo
    sha256sum "$SRC" "$DST"
fi
"""
with open(os.path.join(mod_dir, "post-fs-data.sh"), "w", encoding="utf-8", newline="\n") as f:
    f.write(post_fs_data)

# Write service.sh for fallback mount check in audioserver namespace
service_sh = """#!/system/bin/sh
MODDIR="${0%/*}"
MODE="$(cat "$MODDIR/mode" 2>/dev/null | tr -d '[:space:]')"
DST="/vendor/etc/mixer_paths_overlay_static.xml"
SRC="$MODDIR/files/mixer_paths_overlay_static.xml"

if [ "$MODE" = "gains" ] || [ "$MODE" = "both" ]; then
    # Ensure mount persists
    if ! grep -q "$DST" /proc/mounts 2>/dev/null; then
        mount -o bind "$SRC" "$DST"
    fi
fi
"""
with open(os.path.join(mod_dir, "service.sh"), "w", encoding="utf-8", newline="\n") as f:
    f.write(service_sh)

# Create zip file
zip_path = os.path.join(workspace, "apollon_mic_tuning_v1.0.zip")
rel_dir = os.path.join(workspace, "releases")
os.makedirs(rel_dir, exist_ok=True)
rel_zip = os.path.join(rel_dir, "apollon_mic_tuning_v1.0.zip")

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(mod_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, mod_dir)
            z.write(full_path, rel_path)

import shutil
shutil.copy2(zip_path, rel_zip)

print(f"Zip created: {zip_path}")
print(f"Release copy: {rel_zip}")
print(f"Zip size: {os.path.getsize(zip_path)} bytes")
