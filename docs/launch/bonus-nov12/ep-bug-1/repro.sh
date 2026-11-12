#!/bin/sh
# Usage: IMAGE=<iris image> ./repro.sh   (runs in a fresh container, removes it afterwards)
set -e
IMAGE=${IMAGE:?set IMAGE to an IRIS image}
C=zprobe-skippedarg-$$
docker run -d --name $C --init "$IMAGE" >/dev/null
trap 'docker rm -f $C >/dev/null' EXIT
until docker exec $C iris qlist IRIS 2>/dev/null | grep -q running; do sleep 2; done
docker cp "$(dirname "$0")/ZProbe.SkippedArg.cls" $C:/tmp/
docker exec -i $C iris session IRIS -U USER <<'OS'
 write $zversion,!
 do $system.OBJ.Load("/tmp/ZProbe.SkippedArg.cls","ck-d")
 do ##class(ZProbe.SkippedArg).Run()
 halt
OS
