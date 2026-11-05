const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const ctx={module:{exports:{}},globalThis:{}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../Core.html'),'utf8'),ctx);
const C=ctx.module.exports;
const sample=['식자재 거래명세서','거래일자: 2026.11.05','거래처: 안산식자재유통',
'품명 수량 단가 금액','양파(10kg) 2 15000 30000','당근(1kg) 3 2300 6900',
'공급가액 36900','부가세 0','합계 36900'].join('\n');
test('품목 여러 개와 날짜·거래처·금액 추출',()=>{
 const r=C.extractReceipt(sample);assert.equal(r.date,'2026-11-05');
 assert.equal(r.supplier,'안산식자재유통');assert.equal(r.type,'거래명세서');
 assert.equal(r.items.length,2);assert.equal(r.items[0].spec,'10kg');
 assert.equal(r.items[1].amount,6900);assert.equal(r.supply,36900);assert.equal(r.tax,0);
 assert.equal(r.total,36900);assert.equal(r.payment,'미확인');
});
test('인식 불가능한 값은 없는 그대로',()=>{
 const r=C.extractReceipt('품목\n양파 2개\n감사합니다');
 assert.equal(r.date,'');assert.equal(r.supplier,'');assert.equal(r.total,null);assert.equal(r.items.length,0);
});
test('유효하지 않은 날짜 미기입',()=>assert.equal(C.isoDate('2026.02.30'),''));
test('수량 단가 계산 불일치 알림',()=>{
 const a=C.audit({date:'2026-11-05',supplier:'상회'},[{name:'양파',quantity:2,unitPrice:10000,amount:9000}]);
 assert.match(a.join('|'),/수량×단가/);
});
test('품목 합계 불일치 시 원값 보존',()=>{
 const d={date:'2026-11-05',supplier:'상회',supply:9000,tax:900,total:9900};
 assert.match(C.audit(d,[{name:'양파',quantity:2,unitPrice:4000,amount:8000}]).join('|'),/품목 합계/);
 assert.equal(d.supply,9000);
});
test('세금 포함 합계 불일치',()=>{
 assert.match(C.audit({date:'2026-11-05',supplier:'상회',supply:9000,tax:900,total:12000},[]).join('|'),/공급가액 \+ 부가세/);
});
test('빈 숫자를 0으로 가정하지 않음',()=>{assert.equal(C.numberOrNull(''),null);assert.equal(C.numberOrNull('1,234'),1234);});
test('영수증과 거래명세서 중복 후보 경고',()=>{
 const d={date:'2026-11-05',supplier:'안산 식자재',total:10000,type:'영수증'};
 const list=[{id:'x',date:'2026-11-05',supplier:'안산   식자재',total:10000,type:'거래명세서'}];
 assert.equal(C.duplicates(d,list).length,1);
});
test('금액 다르면 중복 자동 판정하지 않음',()=>assert.equal(C.duplicates(
 {date:'2026-11-05',supplier:'A',total:30000},[{date:'2026-11-05',supplier:'A',total:40000}]).length,0));
test('10kg / 1kg 별도 가격 비교',()=>{
 const groups=C.comparableGroups([{name:'양파',spec:'10kg',unit:'박스'},{name:'양파',spec:'1kg',unit:'박스'},{name:'양파',spec:'10kg',unit:'박스'}]);
 assert.equal(groups.map(g=>g.length).join(','),'2,1');
});
test('월간 집계에서 삭제 문서 제외',()=>assert.equal(C.monthTotal([
 {date:'2026-11-05',total:100},{date:'2026-11-03',total:300,status:'삭제'},
 {date:'2026-10-30',total:200}],'2026-11'),100));
test('한글 파일명 CSV 인코딩, 수식 주입 경감',()=>{
 const csv=C.csvExport([{id:'a',date:'2026-11-05',supplier:'=HYPERLINK(1)',imageName:'한글 영수증.jpg',
 items:[{name:'양파',spec:'10kg',unit:'박스',quantity:2,unitPrice:15000,amount:30000}]}]);
 assert.ok(csv.includes('한글 영수증.jpg'));assert.ok(csv.includes("'=HYPERLINK(1)"));assert.ok(csv.startsWith('\ufeff'));
});
