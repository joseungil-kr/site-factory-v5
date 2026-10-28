'use strict';
const form = document.querySelector('#order-note');
if (form) {
  const allowed = new Set(['D144', 'D158', 'D149']);
  const sku = new URLSearchParams(location.search).get('sku');
  if (allowed.has(sku)) form.elements.sku.value = sku;
  const purposes = {opening:'사무실 개업 축하',move:'사무실 이전 축하',partner:'거래처 개업선물'};
  const purpose = new URLSearchParams(location.search).get('purpose');
  if (Object.hasOwn(purposes,purpose)) form.elements.purpose.value = purposes[purpose];
  form.addEventListener('submit', event => {
    event.preventDefault();
    const data = new FormData(form);
    const labels = {purpose:'선물 목적',ribbon:'축하 문구',sender:'보내는 이름',recipient:'받는 회사·담당자',phone:'수령 연락처',address:'주소·건물·층·호수',date:'희망 날짜',time:'수령 가능 시간',note:'요청사항'};
    const lines = ['상품: ' + form.elements.sku.selectedOptions[0].textContent];
    for (const [key,label] of Object.entries(labels)) if (data.get(key).trim()) lines.push(label + ': ' + data.get(key).trim());
    document.querySelector('#summary').textContent = lines.join('\n');
    const selected = allowed.has(data.get('sku')) ? data.get('sku') : 'D144';
    document.querySelector('#checkout').href = 'https://fwith.co.kr/shop/item.php?it_id=' + selected;
    document.querySelector('.note-output').hidden = false;
    document.querySelector('#copy-status').textContent = '';
  });
  form.addEventListener('reset', () => {
    document.querySelector('.note-output').hidden = true;
    document.querySelector('#summary').textContent = '';
    document.querySelector('#copy-status').textContent = '';
  });
  document.querySelector('#copy-note').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(document.querySelector('#summary').textContent);
      document.querySelector('#copy-status').textContent = '메모를 복사했습니다. 판매처 주문이나 상담에서 사용하세요.';
    } catch {
      document.querySelector('#copy-status').textContent = '메모 글을 직접 선택해 복사해 주세요.';
    }
  });
}
const search = document.querySelector('#region-search');
if (search) search.addEventListener('input', () => {
  const query = search.value.trim().replace(/\s+/g,'');
  for (const row of document.querySelectorAll('.region-row')) row.hidden = !row.textContent.replace(/\s+/g,'').includes(query);
});
const spaceFilter = document.querySelector('#space-filter');
if (spaceFilter) {
  const budgetFilter = document.querySelector('#budget-filter');
  const purposeFilter = document.querySelector('#purpose-filter');
  const advice = {opening:'처음 문을 여는 사무실의 놓을 자리와 개업일을 확인하세요.',move:'이전한 주소와 새 배치를 확인하고 이전 축하 문구를 준비하세요.',partner:'받는 회사의 정식 명칭과 보내는 회사명을 정확히 적어 주세요.'};
  const update = () => {
    let shown = 0;
    for (const card of document.querySelectorAll('#collection .product')) {
      card.hidden = (spaceFilter.value !== 'all' && card.dataset.space !== spaceFilter.value) || Number(card.dataset.price) > Number(budgetFilter.value) || !card.dataset.purposes.split(' ').includes(purposeFilter.value);
      if (!card.hidden) shown++;
      const link = card.querySelector('.subtle');
      const url = new URL(link.href);
      url.searchParams.set('purpose',purposeFilter.value);
      link.href = url.pathname + url.search;
    }
    document.querySelector('#no-products').hidden = shown !== 0;
    document.querySelector('#selection-advice').textContent = advice[purposeFilter.value];
  };
  for (const control of [spaceFilter,budgetFilter,purposeFilter]) control.addEventListener('change',update);
  update();
}