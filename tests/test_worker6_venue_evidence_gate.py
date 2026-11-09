import unittest,json
from pathlib import Path
from scripts.worker6_venue_evidence_gate import normalize,validate,may_make_confirmed_customer_claim
class VenueEvidenceGateTests(unittest.TestCase):
 def base(self):
  return dict(readMode="full-text",exactQuote="행사장 화분 반입을 허용합니다.",
   pageOrSection="제4절 반입 품목",documentVenue="고양 킨텍스",eventYear=2026,
   targetVenue="고양 킨텍스",checkedAt="2026-11-09",sourceUpdatedAt="2026-10-01",
   currentRuleIndependentlyVerified=True)
 def test_full_text_current_matching_venue_structurally_passes(self):
  self.assertTrue(may_make_confirmed_customer_claim(self.base()))
 def test_string_false_independent_verification_rejected(self):
  x=self.base();x["currentRuleIndependentlyVerified"]="false"
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_bool_event_year_rejected(self):
  x=self.base();x["eventYear"]=True
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_string_false_contradiction_rejected(self):
  x=self.base();x["contradictionUnresolved"]="false"
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_string_false_seller_flag_rejected(self):
  x=self.base();x["sellerReportedOnly"]="false"
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_string_event_year_rejected(self):
  x=self.base();x["eventYear"]="2026"
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_inaccessible_kintex_pdf_fails(self):
  x=self.base();x.update(readMode="unavailable",exactQuote=None,pageOrSection=None)
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_search_excerpt_fails(self):
  x=self.base();x["readMode"]="excerpt"
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_metadata_only_fails(self):
  x=self.base();x["readMode"]="metadata"
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_kes_coex_to_kintex_mislink_fails(self):
  x=self.base();x.update(documentVenue="서울 코엑스 A·B홀",eventYear=2023)
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_seller_notice_without_date_and_official_confirmation_fails(self):
  x=self.base();x.update(sourceUpdatedAt=None,sellerReportedOnly=True,
      currentRuleIndependentlyVerified=False,pageOrSection="3단화환 반입불가 대체상품 배송지")
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_full_text_but_not_current_fails(self):
  x=self.base();x["currentRuleIndependentlyVerified"]=False
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_conflicting_source_fails(self):
  x=self.base();x["contradictionUnresolved"]=True
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_legacy_502_normalizes_without_upgrading(self):
  x=dict(accessResult="HTTP 502 Bad Gateway (web reader)",checkedAt="2026-11-09",
   sourceUpdatedAt=None)
  self.assertEqual(normalize(x)["readMode"],"unavailable")
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_legacy_kes_excerpt_normalizes(self):
  x=dict(quoteEvidenceLevel="indexed search excerpt only; exact PDF page number not verified",
   exactQuoteFromIndexedExcerpt="대형 화환 및 대형 화분을 반입할 수 없습니다.",
   eventVenue="서울 코엑스 A·B홀",targetVenue="고양 킨텍스",
   eventYear=2023,accessAttemptedAt="2026-11-09",sourceUpdatedAt=None)
  self.assertEqual(normalize(x)["readMode"],"excerpt")
  self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_actual_corrected_ledger_all_unconfirmed(self):
  d=json.loads(Path("sites/promotion-gift-plants/TWO_VENUE_ADMISSION_EVIDENCE_20261109.json").read_text(encoding="utf-8"))
  k=d["venues"][0]
  for source in k["officialSources"]:
   x=dict(source,targetVenue="고양 킨텍스",documentVenue="고양 킨텍스")
   self.assertEqual(normalize(x)["readMode"],"unavailable")
   self.assertFalse(may_make_confirmed_customer_claim(x))
  for source in k["unrelatedEventReferences"]:
   x=dict(source,targetVenue="고양 킨텍스")
   self.assertEqual(normalize(x)["readMode"],"excerpt")
   self.assertFalse(may_make_confirmed_customer_claim(x))
  for entry in d["sellerNotice"]["observations"]:
   x=dict(readMode="full-text",exactQuote=entry["exactQuote"],
    pageOrSection=d["sellerNotice"]["heading"],documentVenue=entry["venue"],
    targetVenue=entry["venue"],eventYear=None,checkedAt=d["checkedAt"],
    sourceUpdatedAt=d["sellerNotice"]["sourceUpdatedAt"],
    sellerReportedOnly=True,currentRuleIndependentlyVerified=False)
   self.assertFalse(may_make_confirmed_customer_claim(x))
 def test_missing_quote_section_or_year_fails(self):
  for key in ("exactQuote","pageOrSection","eventYear"):
   x=self.base();x[key]=None
   self.assertFalse(may_make_confirmed_customer_claim(x))
if __name__=="__main__":unittest.main()
