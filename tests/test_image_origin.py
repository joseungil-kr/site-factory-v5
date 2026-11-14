from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import check_image_origin as gate

class ImageSourcePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        path=self.root/"assets/library/unit/test.webp"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"RIFF1234WEBPexample-original-image-asset-bytes")
        self.path="assets/library/unit/test.webp"
        self.binary=path.read_bytes()
        self.sha=hashlib.sha256(self.binary).hexdigest()
    def generated(self):
        return {
            "sourceType":"GENERATED_VERIFIED",
            "assetPath":self.path,
            "assetRole":"menu_illustration",
            "depictedFactRole":"illustration",
            "generatorTool":"openai:image_gen",
            "toolResultRef":"gen_id:unit-test-actual-tool-result",
            "toolPromptVerbatim":"Soft natural restaurant lighting, an original simple food setting.",
            "userRequestText":"Generate an original restaurant food image",
            "generatedAt":"2026-10-30T07:05:00Z",
            "originalFilename":"imagegen.png",
            "originalSha256":"0"*64,
            "originalArchiveLocation":"/SiteFactory/image-origin/test/generated_originals.zip",
            "transformations":[{"operation":"resize","target":[1280,720]},{"operation":"encode","format":"WEBP"}],
            "finalSha256":self.sha,
            "finalBytes":len(self.binary)
        }
    def approved(self):
        r=self.generated()
        r.pop("generatorTool")
        r.pop("toolResultRef")
        r.pop("toolPromptVerbatim")
        r.pop("generatedAt")
        r.pop("originalFilename")
        r.pop("originalArchiveLocation")
        r.pop("transformations")
        r["sourceType"]="USER_APPROVED_EXTERNAL"
        r["depictedFactRole"]="approved_external_photo"
        r["originalURL"]="https://skycar1day.com/images/yjsky_01.jpg"
        r["permission"]={"scopeHostname":"skycar1day.com","exactAsset":True,
                         "userQuote":"skycar1day.com 사진은 사용해도 좋음",
                         "issuedOn":"2026-10-30"}
        return r

    def test_generated_requires_genuine_complete_tool_evidence(self):
        self.assertEqual(gate.validate_one(self.generated(),self.root),[])

    def test_ai_label_or_file_hash_cannot_replace_generator_result(self):
        r=self.generated()
        for key in ("toolResultRef","toolPromptVerbatim","generatedAt"):
            r[key]=None
        errors=gate.validate_one(r,self.root)
        self.assertTrue(any("toolResultRef" in x for x in errors))
        self.assertTrue(any("toolPromptVerbatim" in x for x in errors))
        self.assertTrue(any("generatedAt" in x for x in errors))
        self.assertTrue(errors)

    def test_explicit_skycar_source_grant_scoped_to_exact_host(self):
        r=self.approved()
        self.assertEqual(gate.validate_one(r,self.root),[])
        r["originalURL"]="https://another-skycar-service.example/images/yjsky_01.jpg"
        errors=gate.validate_one(r,self.root)
        self.assertTrue(any("host scope mismatch" in x for x in errors))

    def test_unknown_source_or_wrong_hash_fails_closed(self):
        r=self.generated()
        r["finalSha256"]="1"*64
        self.assertTrue(any("Final SHA256" in e for e in gate.validate_one(r,self.root)))
        r["sourceType"]="GENERATION_EVIDENCE_PARTIAL"
        self.assertTrue(any("not authorized" in e for e in gate.validate_one(r,self.root)))

    def test_new_image_hotlinks_are_rejected(self):
        p=self.root/"sites/unit/index.html"
        p.parent.mkdir(parents=True)
        p.write_text('<img src="https://unsplash.example/photo.jpg">',encoding="utf-8")
        self.assertEqual(len(gate.scan_hotlinks(["sites/unit/index.html"],self.root)),1)
        p.write_text('<img src="/assets/library/unit/test.webp">',encoding="utf-8")
        self.assertEqual(gate.scan_hotlinks(["sites/unit/index.html"],self.root),[])

    def test_missing_timestamp_timezone_and_fake_copy_are_rejected(self):
        r=self.generated()
        r["generatedAt"]="2026-10-30 17:50"
        self.assertTrue(gate.validate_one(r,self.root))
        r["generatedAt"]="2026-10-30T08:50:00+09:00"
        self.assertTrue(gate.validate_one(r,self.root))
        r["generatedAt"]="2026-10-30T08:50:00Z"
        self.assertEqual(gate.validate_one(r,self.root),[])

    def test_new_site_reusing_old_unknown_image_fails_even_without_binary_change(self):
        site=self.root/"sites/future-site"
        site.mkdir(parents=True)
        (site/"site.json").write_text(json.dumps({
            "id":"future-site","imageLibrary":"unit","imagePool":["test.webp"]}),encoding="utf-8")
        refs=gate.referenced_site_images("future-site",self.root)
        self.assertEqual(refs,{self.path})
        changed=["sites/future-site/site.json"]
        result=gate.check_changed_site_dependencies(changed,{},self.root)
        self.assertTrue(any("without verified origin" in e for e in result["errors"]))
        allowed=gate.check_changed_site_dependencies(changed,{self.path:self.generated()},self.root)
        self.assertEqual(allowed["errors"],[])

    def test_explicit_release_asset_manifest_rejects_missing_origin(self):
        manifest=self.root/"release-assets.json"
        manifest.write_text(json.dumps({"assets":[self.path]}),encoding="utf-8")
        failed=gate.check_explicit_release_assets(manifest,{},self.root)
        self.assertTrue(any("no approved provenance" in e for e in failed))
        passed=gate.check_explicit_release_assets(manifest,{self.path:self.generated()},self.root)
        self.assertEqual(passed,[])

if __name__=="__main__":
    unittest.main()
