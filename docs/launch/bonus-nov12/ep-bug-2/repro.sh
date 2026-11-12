#!/bin/sh
# Usage: IMAGE=<iris image> ./repro.sh   (runs in a fresh container, removes it afterwards)
set -e
IMAGE=${IMAGE:?set IMAGE to an IRIS image}
C=zprobe-rejected-$$
docker run -d --name $C --init "$IMAGE" >/dev/null
trap 'docker rm -f $C >/dev/null' EXIT
until docker exec $C iris qlist IRIS 2>/dev/null | grep -q running; do sleep 2; done
for f in "$(dirname "$0")"/ZProbe.*.cls; do docker cp "$f" $C:/tmp/; done
docker exec -i $C iris session IRIS -U USER <<'OS'
 write $zversion,!
 for c="Rejected","RejectedSyntax","RejectedOS" { set cls="ZProbe."_c, sc=$system.OBJ.Load("/tmp/"_cls_".cls","ck") write !,"== ",cls,": compile ok=",+$system.Status.IsOK(sc),", IsUpToDate=",$system.OBJ.IsUpToDate(cls),! for m="Good","Bad" { try { write "   ",m,"() -> ",$classmethod(cls,m),! } catch ex { write ex.DisplayString(),! } } }
 halt
OS
