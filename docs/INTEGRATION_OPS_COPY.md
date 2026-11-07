# SilentShift for integration operations

Proposed pilot copy. Not published; no customer validation or pilot availability is asserted.

## Positioning

**Catch unsupported order changes before they reach fulfillment.**

Your partner's order passes the transport and schema checks. The quantity, unit or approved terms still deserve a second look. SilentShift brings the incoming value and the approved order record into one investigation, so the integration operator can see what changed and why the order should be held.

An order arrives as 20 CASE against an approved commitment of 240 EA. Without an authorized conversion, SilentShift holds the demonstrated order. If an effective approved amendment authorizes 20 CASE, the demonstrated workflow lets it proceed. The distinction follows approved evidence rather than a guessed conversion.

For a first pilot, the proposed scope is one partner's CSV feed and an independent approved-order export, evaluated in shadow mode alongside the existing pipeline. Operators would review discrepancies and compare the results with their current checks before considering any delivery control.

The intended audience is the team responsible for partner-order exceptions, regardless of its ERP or EDI platform. A proposed managed deployment would expose feed and review interfaces while keeping IRIS operation behind the service boundary. That deployment is not available today; current local setup requires IRIS expertise and a separately licensed runtime.

## Proof available today

The existing local IRIS demonstrator provides native AI Hub investigation, deterministic policy, recoverable human review and traceable simulator outcomes on synthetic cases. It has a [captioned walkthrough](https://youtu.be/a4dOcqu89EA), [public source](https://github.com/himanshu748/silentshift) and a [verified native replay recipe](../README.md#see-it-in-visual-trace).

A separate [local CSV pilot](../pilot/README.md) accepts a bounded order feed and an independently approved reference export, then sends individual lines through the existing native production. Its samples are synthetic and its destination is the IRIS simulator. X12 support, whole-order release, a hosted demo and customer-data validation remain proposed. The [pilot specification](PRODUCT_PILOT.md) defines those acceptance gates. No measured reduction in exceptions, resolution time or business loss is claimed.

## Discovery prompt

Which partner feed most often produces orders that pass technical checks but still need manual correction? Start with its column layout, the approved reference used to resolve disputes and a small de-identified set of accepted, disputed and amended orders. The first evaluation should establish whether SilentShift finds useful discrepancies without creating an unmanageable review queue.
