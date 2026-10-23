(() => {
  const form = document.querySelector('#site-search-form');
  const results = document.querySelector('#search-results');
  const query = document.querySelector('#site-query');
  if (!form || !query || !results) return;
  let cache;
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    results.replaceChildren();
    const q = query.value.trim().toLocaleLowerCase('ko-KR');
    if (q.length < 2) { results.textContent = '두 글자 이상 입력해 주세요.';return; }
    try {
      if (!cache) {
        const response = await fetch('/search-index.json');
        if (!response.ok) throw new Error('search-index unavailable');
        cache = await response.json();
      }
      const matches = cache.filter(row => (row.title+' '+row.description).toLocaleLowerCase('ko-KR').includes(q)).slice(0,40);
      if (!matches.length) {results.textContent='검색된 글이 없습니다.';return;}
      for (const match of matches) {
        const item = document.createElement('li');
        const anchor = document.createElement('a');
        anchor.href = match.path;
        anchor.textContent = match.title;
        item.append(anchor);
        results.append(item);
      }
    } catch (e) { results.textContent = '검색 목록을 읽을 수 없습니다.'; }
  });
})();
