#!/bin/sh
set -eu
source_root=${1:?source root required}
output=${2:?output directory required}
junit=${3:?JUnit Platform console standalone jar required}
sh "$source_root/build.sh" "$source_root" "$output"
sdk=/usr/irissys/dev/java/lib/1.8
pex=$(find "$sdk" -maxdepth 1 -name 'intersystems-pex-*-shaded.jar' -print -quit)
jdbc=$(find "$sdk" -maxdepth 1 -name 'intersystems-jdbc-*.jar' -print -quit)
javac --release 11 -cp "$output/classes:$pex:$jdbc:$junit" -d "$output/test-classes" \
 "$source_root/src/test/java/SilentShift/PEX/ReceiptStoreTest.java"
java -jar "$junit" execute --class-path "$output/classes:$output/test-classes:$pex:$jdbc" \
 --scan-class-path --fail-if-no-tests --disable-ansi-colors
