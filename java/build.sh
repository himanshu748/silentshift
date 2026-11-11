#!/bin/sh
# Build only owned sources against the SDK already supplied by the operator's IRIS image.
set -eu
source_root=${1:?source root required}
output=${2:?output directory required}
sdk=/usr/irissys/dev/java/lib/1.8
pex=$(find "$sdk" -maxdepth 1 -name 'intersystems-pex-*-shaded.jar' -print -quit)
jdbc=$(find "$sdk" -maxdepth 1 -name 'intersystems-jdbc-*.jar' -print -quit)
test -n "$pex" && test -n "$jdbc"
command -v javac >/dev/null || { echo 'Java 11 JDK is required to build the PEX operation.' >&2; exit 1; }
mkdir -p "$output/classes"
javac --release 11 -cp "$pex:$jdbc" -d "$output/classes" \
 "$source_root/src/main/java/SilentShift/PEX/ReceiptStore.java" \
 "$source_root/src/main/java/SilentShift/PEX/ReceiptExporter.java"
jar --create --file "$output/silentshift-pex.jar" -C "$output/classes" .
echo 'SILENTSHIFT_PEX_BUILD_OK'
