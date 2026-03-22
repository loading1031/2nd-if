/**
 * EditorJS 초기화 스크립트
 *
 * #editorjs 요소에 EditorJS 에디터를 초기화하고,
 * 폼 제출 시 에디터 데이터를 hidden input에 JSON으로 저장합니다.
 *
 * 필수 요소:
 * - #editorjs: 에디터가 마운트될 div
 * - #content-input: 에디터 데이터를 저장할 hidden input
 *
 * CDN 스크립트가 먼저 로드되어야 합니다:
 * - @editorjs/editorjs
 * - @editorjs/header
 * - @editorjs/list
 * - @editorjs/quote
 * - @editorjs/code
 * - @editorjs/image
 */
document.addEventListener('DOMContentLoaded', function () {
    const editorElement = document.getElementById('editorjs');
    if (!editorElement) return;

    const contentInput = document.getElementById('content-input');
    if (!contentInput) return;

    // 편집 모드: 기존 데이터 로드
    let initialData = {};
    if (contentInput.value) {
        try {
            initialData = JSON.parse(contentInput.value);
        } catch (e) {
            console.warn('EditorJS: 기존 콘텐츠 파싱 실패', e);
        }
    }

    const editor = new EditorJS({
        holder: 'editorjs',
        data: initialData,
        placeholder: '이야기를 시작해보세요...',
        minHeight: 300,
        logLevel: 'ERROR',
        tools: {
            header: {
                class: Header,
                config: {
                    levels: [2, 3, 4],
                    defaultLevel: 2,
                },
            },
            list: {
                class: NestedList,
                inlineToolbar: true,
            },
            quote: {
                class: Quote,
            },
            code: {
                class: CodeTool,
            },
            image: {
                class: ImageTool,
                config: {
                    endpoints: {
                        byFile: '/api/upload-image/',
                    },
                },
            },
        },
    });

    // 폼 제출 시 에디터 데이터를 hidden input에 저장
    const form = editorElement.closest('form');
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();

            try {
                const outputData = await editor.save();
                contentInput.value = JSON.stringify(outputData);

                // HTMX가 있으면 HTMX로 제출, 없으면 일반 제출
                if (typeof htmx !== 'undefined') {
                    htmx.trigger(form, 'submit');
                } else {
                    form.submit();
                }
            } catch (err) {
                console.error('EditorJS 저장 실패:', err);
            }
        });
    }
});
