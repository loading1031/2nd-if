// Local demo state only; no account, analytics or publishing requests are sent.
function required<T extends Element>(selector: string): T {
  const element = document.querySelector<T>(selector);
  if (!element) throw new Error(`Missing design element: ${selector}`);
  return element;
}

const labels: Record<string, string> = {
  insights: '독서 인사이트', sharing: '지표 공개 설정', books: '설정집과 에셋',
};
const previewState = required<HTMLSelectElement>('#preview-state');
const stateMessages: Record<string, [string, string]> = {
  loading: ['불러오는 중', '최신 집계를 확인하고 있습니다.'],
  empty: ['아직 표시할 데이터가 없습니다', '읽기 이벤트가 집계되거나 설정집을 채택하면 이곳에서 확인할 수 있습니다.'],
  error: ['데이터를 불러오지 못했습니다', '잠시 후 다시 시도해 주세요.'],
  denied: ['접근 권한이 없습니다', '이 화면을 볼 수 있는 현재 권한을 확인해 주세요.'],
};
function renderPreviewState(): void {
  const state = previewState.value;
  required<HTMLElement>('#screens').hidden = state !== 'normal';
  required<HTMLElement>('#state-panel').hidden = state === 'normal';
  if (state === 'normal') return;
  const [title, description] = stateMessages[state];
  required('#state-title').textContent = title;
  required('#state-description').textContent = description;
  required<HTMLElement>('#state-spinner').hidden = state !== 'loading';
  required<HTMLElement>('#state-retry').hidden = state !== 'error';
}
function navigate(): void {
  const screen = location.hash.slice(1);
  const active = Object.prototype.hasOwnProperty.call(labels, screen) ? screen : 'insights';
  document.querySelectorAll<HTMLElement>('[data-screen]').forEach(section => {
    section.hidden = section.id !== active;
  });
  document.querySelectorAll<HTMLAnchorElement>('[data-nav]').forEach(link => {
    const selected = link.dataset.nav === active;
    link.classList.toggle('menu-active', selected);
    if (selected) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  required('#breadcrumb').textContent = labels[active];
  previewState.value = 'normal';
  renderPreviewState();
}
window.addEventListener('hashchange', navigate);
previewState.addEventListener('change', renderPreviewState);
required('#state-retry').addEventListener('click', () => {
  previewState.value = 'normal';
  renderPreviewState();
});

document.querySelectorAll<HTMLButtonElement>('[data-insight-tab]').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll<HTMLElement>('[data-insight-panel]').forEach(panel => {
      panel.hidden = panel.id !== button.dataset.insightTab;
    });
    document.querySelectorAll<HTMLButtonElement>('[data-insight-tab]').forEach(tab => {
      tab.classList.toggle('tab-active', tab === button);
      tab.setAttribute('aria-selected', String(tab === button));
    });
  });
});

const periods: Record<string, {starts: number; completed: number; resolved: number;
  dropped: number; rejoins: number; episodes: [string, number, number][]}> = {
  '30': {starts: 2714, completed: 1936, resolved: 2481, dropped: 545, rejoins: 184,
    episodes: [['1화 · 유리 온실', 1000, 182], ['2화 · 오래된 열쇠', 800, 180], ['3화 · 밤의 손님', 681, 183]]},
  '7': {starts: 700, completed: 490, resolved: 620, dropped: 130, rejoins: 42,
    episodes: [['1화 · 유리 온실', 250, 45], ['2화 · 오래된 열쇠', 210, 45], ['3화 · 밤의 손님', 160, 40]]},
};
required<HTMLSelectElement>('#period').addEventListener('change', event => {
  const data = periods[(event.currentTarget as HTMLSelectElement).value];
  const format = (n: number) => n.toLocaleString('ko-KR');
  required('#stat-starts').textContent = format(data.starts);
  required('#stat-completed').textContent = format(data.completed);
  required('#stat-dropout').textContent = `${(data.dropped / data.resolved * 100).toFixed(1)}%`;
  required('#stat-resolved').textContent = `${format(data.dropped)} / 판정 완료 ${format(data.resolved)}회`;
  required('#stat-rejoins').textContent = format(data.rejoins);
  required('#rejoin-total').textContent = format(data.rejoins);
  required('#pending-count').textContent = `아직 판정 중인 ${format(data.starts - data.resolved)}회는 이탈률에 포함되지 않습니다.`;
  const tbody = required('#episode-rows');
  tbody.replaceChildren(...data.episodes.map(([label, resolved, dropped]) => {
    const row = document.createElement('tr');
    [label, format(resolved), `${(dropped / resolved * 100).toFixed(1)}%`].forEach((value, index) => {
      const cell = document.createElement('td');
      cell.textContent = value;
      if (index > 0) cell.className = 'text-right';
      row.append(cell);
    });
    return row;
  }));
  const week = (event.currentTarget as HTMLSelectElement).value === '7';
  const times = week ? [39, 31, 54] : [42, 29, 58];
  const counts = week ? [190, 186, 181] : [756, 742, 736];
  document.querySelectorAll('[data-page-time]').forEach((element, i) => { element.textContent = `${times[i]}초`; });
  document.querySelectorAll('[data-page-count]').forEach((element, i) => { element.textContent = `${counts[i]}건`; });
  document.querySelectorAll<HTMLProgressElement>('[data-page-progress]').forEach((element, i) => {
    element.value = times[i];
    element.setAttribute('aria-label', `${i + 1}쪽 전환 시간 ${times[i]}초`);
  });
  const traffic: [string, number, number][] = week
    ? [['홈 추천', 103, 78], ['작가 프로필', 56, 46], ['검색 결과', 45, 31]]
    : [['홈 추천', 412, 312], ['작가 프로필', 226, 184], ['검색 결과', 180, 123]];
  const shared: [string, number, number][] = week
    ? [['홈 추천', 20600, 1030], ['검색 결과', 6250, 438]]
    : [['홈 추천', 82400, 4120], ['검색 결과', 25000, 1750]];
  renderRows('#traffic-rows', traffic.map(([name, clicks, starts]) => [name, format(clicks), format(starts)]));
  renderRows('#shared-rows', shared.map(([name, impressions, clicks]) => [name, format(impressions), format(clicks), `${(clicks / impressions * 100).toFixed(1)}%`]));
});

function renderRows(selector: string, rows: string[][]): void {
  required(selector).replaceChildren(...rows.map(values => {
    const row = document.createElement('tr');
    values.forEach((value, index) => {
      const cell = document.createElement('td');
      cell.textContent = value;
      if (index > 0) cell.className = 'text-right';
      row.append(cell);
    });
    return row;
  }));
}

const visibility = () => required<HTMLInputElement>('input[name="visibility"]:checked').value;
required('#sharing-form').addEventListener('change', () => {
  required<HTMLElement>('#invites-panel').hidden = visibility() !== 'invited';
});
required('#sharing-form').addEventListener('submit', event => {
  event.preventDefault();
  const names: Record<string, string> = {private: '작가만', invited: '초대한 계정만', public: '전체 공개'};
  required('#sharing-status').textContent = `현재 저장된 범위: ${names[visibility()]} (시안 내 상태)`;
  toast('시안에서 공개 설정을 저장했습니다.');
});
required('#add-invite').addEventListener('click', () => {
  const input = required<HTMLInputElement>('#invite-email');
  const email = input.value.trim();
  const error = required<HTMLElement>('#invite-error');
  const existing = Array.from(document.querySelectorAll('#invite-list li span')).map(span => span.textContent);
  if (!email || !input.checkValidity() || existing.includes(email)) {
    error.textContent = existing.includes(email) ? '이미 추가된 계정입니다.' : '유효한 이메일을 입력해 주세요.';
    error.hidden = false;
    return;
  }
  error.hidden = true;
  const item = document.createElement('li');
  item.className = 'flex items-center justify-between gap-3 py-3 text-sm';
  const name = document.createElement('span');
  name.textContent = email;
  const remove = document.createElement('button');
  remove.type = 'button';
  remove.dataset.removeInvite = '';
  remove.className = 'btn btn-ghost btn-xs text-error';
  remove.textContent = '초대 취소';
  item.append(name, remove);
  required('#invite-list').append(item);
  input.value = '';
});
required('#invite-list').addEventListener('click', event => {
  const target = event.target;
  if (target instanceof Element) target.closest('[data-remove-invite]')?.closest('li')?.remove();
});

type Book = {title: string; current: string; next: string; changes: string; license: string};
const books: Record<string, Book> = {
  flora: {title: '북부의 식물 도감', current: 'v1.4', next: 'v1.5', changes: '추가: 식물 이미지 3개. 기존에 선택한 항목과 표현 연결을 유지합니다.', license: '라이선스: 무료 작품 이용 허용 → 동일 조건'},
  city: {title: '비 오는 도시의 소품', current: 'v1.0', next: 'v1.1', changes: '개선: 우산·가로등 이미지 해상도. 기존 에셋 식별자와 표현 연결을 유지합니다.', license: '라이선스: 상업 이용 허용 → 동일 조건'},
};
let selectedBook: string | null = null;
const updateDialog = required<HTMLDialogElement>('#update-dialog');
document.querySelectorAll<HTMLButtonElement>('[data-review-update]').forEach(button => {
  button.addEventListener('click', () => {
    selectedBook = button.dataset.reviewUpdate ?? null;
    if (!selectedBook) return;
    const book = books[selectedBook];
    required('#update-title').textContent = book.title;
    required('#update-current').textContent = book.current;
    required('#update-next').textContent = book.next;
    required('#update-changes').textContent = book.changes;
    required('#update-license').textContent = book.license;
    updateDialog.showModal();
  });
});
required('#confirm-update').addEventListener('click', () => {
  if (!selectedBook) return;
  const book = books[selectedBook];
  book.current = book.next;
  required(`[data-current-version="${selectedBook}"]`).textContent = book.current;
  required<HTMLElement>(`[data-review-update="${selectedBook}"]`).hidden = true;
  required<HTMLElement>(`[data-latest="${selectedBook}"]`).hidden = false;
  if (selectedBook === 'flora') required('#asset-flora-version').textContent = book.current;
  updateDialog.close();
  toast(`${book.title}만 ${book.current}로 업데이트했습니다. (시안)`);
});

const assetDialog = required<HTMLDialogElement>('#asset-dialog');
required('#choose-asset').addEventListener('click', () => assetDialog.showModal());
assetDialog.addEventListener('change', () => { required<HTMLButtonElement>('#confirm-asset').disabled = false; });
required('#confirm-asset').addEventListener('click', () => {
  const selected = required<HTMLInputElement>('input[name="asset-choice"]:checked');
  required('#mapping-status').textContent = `${selected.value} 연결됨 · 이 표현에서 독자에게 표시됩니다.`;
  required('#choose-asset').textContent = '연결 변경';
  assetDialog.close();
});
required('#browse-books').addEventListener('click', () => required<HTMLDialogElement>('#catalog-dialog').showModal());
let toastTimer: ReturnType<typeof setTimeout> | undefined;
function toast(message: string): void {
  clearTimeout(toastTimer);
  required('#toast-text').textContent = message;
  required<HTMLElement>('#toast').hidden = false;
  toastTimer = setTimeout(() => { required<HTMLElement>('#toast').hidden = true; }, 4000);
}
navigate();
