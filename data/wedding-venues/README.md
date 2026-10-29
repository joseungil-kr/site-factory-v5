# Wedding venues research dataset

Status: research-only; not connected to site generation or deployment.

## First batch (2026-10-30)

- `venues.json`: normalized structured records.
- `venues.csv`: flat review/export copy.
- `sources.json`: source register, conditions, freshness, and verification scope.
- Current records: 5 public-data candidates; **0 independently confirmed against each venue's own official wedding-operation page in this batch**.
- Candidate records are not publication-ready. Government standard data currently reports operation as Y for the included sample rows, but the venue's current wedding operation, official website, current phone, and flower delivery rules still need direct verification.

## Scope and inclusion

Include wedding halls, hotels, convention venues, and public facilities only when an official source supports wedding use. A generic banquet room is not sufficient. Do not mix funeral halls into this dataset.

## Record and verification policy

- `stable_id`: persistent internal ID, not derived from phone number.
- `status`: `candidate_official_dataset`, `verified_active`, `closure_unconfirmed`, `relocated`, `renamed`, `operation_unconfirmed`, or `closed`.
- `wedding_operation_evidence`: source proving the facility hosts weddings; dataset membership alone is not direct venue-level confirmation.
- `flower_policy.status`: `allowed`, `restricted`, `prohibited`, or `unknown`. Unknown flower rules never exclude an otherwise valid venue.
- Keep the facility's official facts separate from seller's flower products, prices, delivery promises, and partnership claims.
- Do not infer same-day delivery, exact arrival time, free delivery, or venue partnership.
- Never collect private individuals' contacts, couple/booking data, or personal reservation information.
- De-duplicate using normalized name + address + official URL; preserve building/venue parent-child relationships rather than collapsing distinct halls.

## Region tracking

National coverage has 17 province-level units: Seoul, Busan, Daegu, Incheon, Gwangju, Daejeon, Ulsan, Sejong, Gyeonggi, Gangwon, Chungbuk, Chungnam, Jeonbuk, Jeonnam, Gyeongbuk, Gyeongnam, Jeju. This initial sample is **not** a representative coverage sample. Region completion counts must be added only after candidate discovery and verification.

## Source and reuse

See `sources.json`. The initial source is the official Korean public data portal's National Wedding and Ceremony Hall Standard Data page. Its page was observed on 2026-10-30 and displays a dataset update date of 2026-10-07. Data may lag local authority updates. Preserve provenance and re-check operational status before publication. Do not copy venue website prose or images into this repository.

## Files are research artifacts only

This branch must not modify operating content, workflows, site generation, deployment configuration, or production URLs.
