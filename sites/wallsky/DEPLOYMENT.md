# Parent-controlled publication

No main merge, production deployment, domain mutation, IndexNow submission or new scheduled task has been executed by the original local handoff. Remote persistence is being handled on the explicitly requested Wallsky branch separately.

## Reused operational evidence

- V5 baseline d4f58c660655afc5f8359fe0fa70b98fc7588309; V4 read-only clone 223b9348f32b700af98645d034943772d590aaba.
- V4 `.github/workflows/publish-national-flower-a.yml`: explicit dispatch/main gate, shared concurrency, before-version capture, readback, rollback, then IndexNow. `scripts/publish_national_release.py`: exact full-release HTTP/hash verification and separate IndexNow phase.
- V5 `.github/workflows/daysky-1736-deploy.yml`: existing custom-domain identity check, stable rollback version, Workers static-assets adapter. Most recent checked deploy runs 40435132123 and 40225502317 failed; do not describe them as successful. V5 build run 40643531356 succeeded.
- Existing V5 Worker `worker/index.js` permits indexing only for daysky/plants. Do not deploy Wallsky with an assumption that this allowlist includes the new hostname.

## Target and conflict policy

Candidate domain `wallsky.nalmada.net`, dedicated Worker `sfv52-wallsky`. A DNS query on 2026-10-28 reportedly returned that the name did not exist; this is historical and must be rechecked. Account-level Worker custom domains, routes and DNS wildcard bindings have not yet been verified. Stop on collision; do not overwrite an existing binding.

Earlier automatic approval review denied a source push and a proposed workflow for continuous remote artifact upload, citing insufficient explicit authorization for sending the business phone/content to the named GitHub destination. No bypass was attempted. The current user has now explicitly designated this repository, the Wallsky business purpose and creation/publication work; use only the normal GitHub write path. Do not create an artifact-upload workaround or widen permissions. If the standard write action is denied again, stop and record the exact denial.

## Reviewed release procedure

1. Review the pinned region-name source, source copy pool, similarity audit and saved desktop/mobile screenshots. These screenshots are historical local observations, not a live browser check.
2. Through an already-authorized Cloudflare connection, read current `nalmada.net` zone DNS, routes, account Worker custom-domain bindings and `sfv52-wallsky` existence. Stop on collision. Do not create credentials, change nameservers or widen permissions.
3. Build `python scripts/build_wallsky.py --public`, run `python scripts/qa_wallsky.py`, inspect sitemap/robots. Keep only the new hostname indexable; workers.dev and 404 must retain noindex. Use the existing Workers static-assets `html_handling:none`, `not_found_handling:404-page`, `run_worker_first:true` pattern with the dedicated adapter.
4. Snapshot previous new-site Worker version and binding state. For a fresh release with no previous version, rollback is to withdraw only the newly added Wallsky publication/binding and preserve all existing site routes. For subsequent releases deploy the previous captured version at 100%.
5. Deploy only dedicated Wallsky assets after build/QA and collision preflight. Read all 5,197 canonical URLs plus assets/sitemap/robots, unknown-path 404 and both display widths against the live host. Verify tel links without placing calls.
6. Only after live checks, reuse the existing authorized IndexNow key process, host the appropriate key file and submit the canonical sitemap URL list. Record the API response separately; acceptance does not guarantee search indexing.

The local review build is noindex. `--public` generates public files locally and is not itself a deployment or indexing submission.
