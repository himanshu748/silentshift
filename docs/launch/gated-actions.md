# Matching 0.3.3 release — owner gates

The owner clarified that a **real IPM 0.3.3 publication is intended**. OEX, the GitHub tag and `module.xml` must agree; an OEX-only version is not acceptable. No native code or evaluation changes are included. Public native/IPM/OEX remain **0.3.2** until publication; React stays **0.2.1**.

PR #14 was merged as `921b37d`. Its Pages publication and anonymous public checks passed. The [agent-value view](https://himanshu748.github.io/silentshift/agent-value.html#HO-045), [tour](https://himanshu748.github.io/silentshift/evidence-tour.html) and [receipt inspector](https://himanshu748.github.io/silentshift/receipts.html) are already live; no further Pages deployment is needed for those links.

## Release order — one public action per exact submit

1. Review the small 0.3.3 metadata/docs PR after CI and a fresh-container local-archive install pass. Merge with a merge commit; no squash or force push. Do not merge a blocked or failing native candidate.
2. Create the matching **v0.3.3** tag and GitHub release at that approved merge. Use [release notes](release-notes.md), explicitly saying “No native code changes.” Do not move an existing tag or declare the release before readback.
3. Prepare the existing OEX app using [the corrected description](../OPEN_EXCHANGE_COPY.md), preserve IPM, idea, contest, logo, Demo/video/MP4 and article fields, and type **0.3.3** manually — **never 1.0.0**. Show the version/form screenshot. Save and final Send/Publish remain distinct approvals if the UI separates them. Never cancel or duplicate a pending approval.
4. After the approved OEX/IPM publication, verify the anonymous listing version, downloaded registry manifest, matching tag and a fresh public literal `zpm "install silentshift"` with the native suite and both recorded replays. Retain the old 0.3.2 evidence as history; do not relabel it 0.3.3.

## Support and duplicate-post discipline

A short follow-up about the missing description-only approval control is prepared for the existing OEX support thread. It acknowledges that we are proceeding with a matching real 0.3.3 package, asks for UI guidance, and does not make a reply a release prerequisite. Sending it remains its own exact-submit action. Do not send the obsolete draft that forbids any 0.3.3 IPM publication.

The Java PEX update is already public as [comment 288628](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows#comment-288628); do not post it again. Optional article/social actions stay on hold. The [2:20 re-cut](video-script.md) remains a script only. No new evaluation, online-demo or award claim is added.
