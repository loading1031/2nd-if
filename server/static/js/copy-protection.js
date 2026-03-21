document.addEventListener('DOMContentLoaded', () => {
    const reader = document.querySelector('.novel-reader');
    if (!reader) return;

    // Step 1: 복사 시 출처 URL 삽입
    reader.addEventListener('copy', (e) => {
        const selection = window.getSelection().toString();
        if (!selection) return;

        const url = reader.dataset.episodeUrl || window.location.href;
        const workTitle = reader.dataset.workTitle || '';
        const episodeTitle = reader.dataset.episodeTitle || '';

        const enriched = `${selection}\n\n— 「${workTitle}」 ${episodeTitle}\n${url}`;
        e.clipboardData.setData('text/plain', enriched);
        e.preventDefault();
    });
});

// Step 2: 핑거프린트 생성 + 쿠키 저장
(async function initFingerprint() {
    if (typeof FingerprintJS === 'undefined') return;

    try {
        const fp = await FingerprintJS.load();
        const result = await fp.get();
        const visitorId = result.visitorId;

        // 쿠키에 저장 (모든 요청에 자동 포함)
        document.cookie = `_2ndif_fp=${visitorId};path=/;max-age=31536000;SameSite=Lax`;

        // HTMX 요청에 헤더로도 전달
        document.body.addEventListener('htmx:configRequest', (e) => {
            e.detail.headers['X-Fingerprint'] = visitorId;
        });
    } catch (err) {
        // 핑거프린트 실패해도 서비스는 정상 동작
    }
})();
