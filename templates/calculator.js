(() => {
  const el = document.getElementById('price-data');
  const qty = document.getElementById('quantity');
  const sku = document.getElementById('sku');
  const output = document.getElementById('estimate');
  if (!el || !qty || !sku || !output) return;
  const prices = JSON.parse(el.textContent);
  function calculate() {
    const count = Number(qty.value);
    const amount = Number(prices[sku.value]);
    if (!Number.isInteger(count) || count < 1 || count > 99 || !Number.isSafeInteger(amount)) {
      output.textContent = '수량 1~99를 선택해 주세요.';
      return;
    }
    output.textContent = `상품 합계: ${(count * amount).toLocaleString('ko-KR')}원`;
  }
  const submit = document.getElementById('estimate-submit');
  if (submit) submit.addEventListener('click', () => { calculate(); window.v5TrackCalculator?.(); });
  qty.addEventListener('input', calculate);
  sku.addEventListener('change', calculate);
  calculate();
})();
