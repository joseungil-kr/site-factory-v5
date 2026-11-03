# RSS release evidence

The source baseline is ac9ed94872f681752417a52b1b26a86567f55721. Existing active Worker generic-skycar-shadow version 4fd85134-2ef2-4705-856f-e999134b9c11 was confirmed through Wrangler and the actual deploy log from V4 run 41275791253. That run deployed successfully but its subsequent workers.dev check received existing edge HTTP 403. It must not be mistaken for an absent deployment.

Before modification, all 42 public HTML pages matched this baseline after Windows/Linux newline normalization. All five image files matched their public SHA-256 hashes. The existing public sitemap has 42 URLs. Main and the separate order project are not modified by this source branch.

Public builds generate /rss.xml from existing main content, with full bodies, absolute references and stable URL GUIDs. Existing pages have no publication metadata, so pubDate is omitted. No publication or modification dates are invented. The feed limit is 50 and output must stay below 10MB. HTML discovery is added only to public builds. Preview builds remain unchanged; workers.dev cannot serve the public feed.

Run the existing Webbuilder Python/Node regressions plus tests.test_rss. On a Windows host with an unrelated installed scripts package, use `python -X utf8 -S -m unittest tests.test_webbuilder tests.test_webbuilder_public tests.test_rss`. The CI Python environment uses the normal module commands.

The control repository retains the existing Worker binding and Cloudflare credentials. It records a backup and refuses to deploy if the active baseline version or custom-domain binding has changed. Rollback uses the captured prior Worker version. No routes, domain ownership, permissions or prices are changed.
