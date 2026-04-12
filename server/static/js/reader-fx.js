/**
 * reader-fx.js — 동적 텍스트 리더 효과
 *
 * data-fx 속성이 있는 요소를 Intersection Observer로 감시.
 * 뷰포트 30% 진입 시 fx-active 클래스 추가 → CSS 애니메이션 재생.
 */

(function() {
  'use strict';

  function initReaderFx() {
    var fxElements = document.querySelectorAll('[data-fx]');
    if (fxElements.length === 0) return;

    // typewriter 효과: 글자 수 기반 동적 duration 계산
    fxElements.forEach(function(el) {
      if (el.dataset.fx === 'typewriter') {
        var text = el.textContent || '';
        var steps = text.length;
        var duration = Math.max(0.5, steps * 0.05); // 글자당 50ms, 최소 0.5s
        el.style.setProperty('--fx-steps', steps);
        el.style.setProperty('--fx-duration', duration + 's');
      }
    });

    // Intersection Observer
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var el = entry.target;
          var delay = parseInt(el.dataset.delay || '0', 10);

          if (delay > 0) {
            setTimeout(function() { el.classList.add('fx-active'); }, delay);
          } else {
            el.classList.add('fx-active');
          }

          // 1회 재생 후 unobserve (float은 계속 관찰)
          if (el.dataset.fx !== 'float') {
            observer.unobserve(el);
          }
        }
      });
    }, {
      threshold: 0.3
    });

    fxElements.forEach(function(el) { observer.observe(el); });
  }

  // DOM 로드 완료 시 초기화
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initReaderFx);
  } else {
    initReaderFx();
  }

  // HTMX 로드 후 재초기화 (에피소드 컨텐츠가 HTMX로 로드되는 경우)
  document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'episode-content') {
      initReaderFx();
    }
  });
})();
