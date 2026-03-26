import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Placeholder from '@tiptap/extension-placeholder'
import BubbleMenu from '@tiptap/extension-bubble-menu'

/**
 * TipTap 에디터 초기화 (소설 작성용 미니멀 설정)
 *
 * 필수 요소:
 * - #editor: 에디터가 마운트될 div
 * - #content-input: 에디터 HTML을 저장할 hidden input
 *
 * 기능:
 * - 연속 텍스트 입력 (블록 끊김 없음)
 * - 텍스트 선택 시 버블 메뉴 (bold/italic)
 * - 슬래시 커맨드 (/image, /divider)
 * - 이미지 드래그앤드롭/업로드
 */

function getCsrfToken() {
  const cookie = document.cookie.split('; ').find(c => c.startsWith('csrftoken='))
  return cookie ? cookie.split('=')[1] : ''
}

async function uploadImage(file) {
  const formData = new FormData()
  formData.append('image', file)

  const resp = await fetch('/api/upload-image/', {
    method: 'POST',
    headers: { 'X-CSRFToken': getCsrfToken() },
    body: formData,
  })

  const data = await resp.json()
  if (data.success === 1) return data.file.url
  if (data.url) return data.url
  return null
}

function createSlashCommandDropdown(editor) {
  const dropdown = document.createElement('div')
  dropdown.id = 'slash-menu'
  dropdown.className = 'hidden absolute z-50 bg-base-100 border border-base-300 rounded-lg shadow-lg p-1 w-48'
  dropdown.innerHTML = `
    <button type="button" data-command="image" class="flex items-center gap-2 w-full px-3 py-2 text-sm text-left rounded hover:bg-base-200">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
      삽화 삽입
    </button>
    <button type="button" data-command="divider" class="flex items-center gap-2 w-full px-3 py-2 text-sm text-left rounded hover:bg-base-200">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/></svg>
      구분선
    </button>
  `
  document.body.appendChild(dropdown)
  return dropdown
}

function initEditor() {
  const editorEl = document.getElementById('editor')
  if (!editorEl) return

  const contentInput = document.getElementById('content-input')
  if (!contentInput) return

  // 버블 메뉴 컨테이너
  const bubbleMenuEl = document.createElement('div')
  bubbleMenuEl.id = 'bubble-menu'
  bubbleMenuEl.className = 'bg-base-100 border border-base-300 rounded-lg shadow-lg flex gap-1 p-1'
  bubbleMenuEl.innerHTML = `
    <button type="button" data-action="bold" class="btn btn-ghost btn-xs font-bold">B</button>
    <button type="button" data-action="italic" class="btn btn-ghost btn-xs italic">I</button>
  `
  document.body.appendChild(bubbleMenuEl)

  // 슬래시 메뉴
  const slashMenu = createSlashCommandDropdown()

  // 기존 콘텐츠 로드
  const initialContent = contentInput.value || '<p></p>'

  const editor = new Editor({
    element: editorEl,
    extensions: [
      StarterKit.configure({
        heading: { levels: [2, 3] },
        codeBlock: false,
        code: false,
        blockquote: false,
      }),
      Image.configure({
        HTMLAttributes: { class: 'rounded-lg shadow-md my-6 max-w-full h-auto mx-auto block' },
      }),
      Placeholder.configure({
        placeholder: '이야기를 시작해보세요... ( / 로 삽화나 구분선을 삽입할 수 있습니다)',
      }),
      BubbleMenu.configure({
        element: bubbleMenuEl,
        tippyOptions: { duration: 100 },
      }),
    ],
    content: initialContent,
    editorProps: {
      attributes: {
        class: 'prose prose-lg max-w-none focus:outline-none min-h-[400px] p-4',
      },
      handleDrop(view, event, slice, moved) {
        if (moved) return false
        const files = event.dataTransfer?.files
        if (!files || files.length === 0) return false

        const file = files[0]
        if (!file.type.startsWith('image/')) return false

        event.preventDefault()
        uploadImage(file).then(url => {
          if (url) {
            editor.chain().focus().setImage({ src: url }).run()
          }
        })
        return true
      },
      handlePaste(view, event) {
        const items = event.clipboardData?.items
        if (!items) return false

        for (const item of items) {
          if (item.type.startsWith('image/')) {
            event.preventDefault()
            const file = item.getAsFile()
            if (file) {
              uploadImage(file).then(url => {
                if (url) {
                  editor.chain().focus().setImage({ src: url }).run()
                }
              })
            }
            return true
          }
        }
        return false
      },
    },
  })

  // 버블 메뉴 버튼 이벤트
  bubbleMenuEl.querySelector('[data-action="bold"]').addEventListener('click', () => {
    editor.chain().focus().toggleBold().run()
  })
  bubbleMenuEl.querySelector('[data-action="italic"]').addEventListener('click', () => {
    editor.chain().focus().toggleItalic().run()
  })

  // 슬래시 커맨드
  let slashActive = false
  let slashPos = null

  editor.on('update', ({ editor: ed }) => {
    const { $head } = ed.state.selection
    const textBefore = $head.parent.textContent.slice(0, $head.parentOffset)

    if (textBefore === '/') {
      slashActive = true
      slashPos = ed.state.selection.from - 1

      // 슬래시 메뉴 위치 계산
      const coords = ed.view.coordsAtPos(ed.state.selection.from)
      slashMenu.style.top = `${coords.bottom + window.scrollY + 4}px`
      slashMenu.style.left = `${coords.left + window.scrollX}px`
      slashMenu.classList.remove('hidden')
    } else if (slashActive) {
      slashMenu.classList.add('hidden')
      slashActive = false
    }
  })

  // 슬래시 메뉴 커맨드 실행
  slashMenu.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-command]')
    if (!btn) return

    const command = btn.dataset.command
    slashMenu.classList.add('hidden')
    slashActive = false

    // '/' 문자 삭제
    if (slashPos !== null) {
      editor.chain().focus()
        .deleteRange({ from: slashPos, to: slashPos + 1 })
        .run()
    }

    if (command === 'image') {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = 'image/*'
      input.onchange = async () => {
        const file = input.files[0]
        if (!file) return
        const url = await uploadImage(file)
        if (url) {
          editor.chain().focus().setImage({ src: url }).run()
        }
      }
      input.click()
    } else if (command === 'divider') {
      editor.chain().focus().setHorizontalRule().run()
    }
  })

  // 클릭 외부 시 슬래시 메뉴 닫기
  document.addEventListener('click', (e) => {
    if (!slashMenu.contains(e.target) && !editorEl.contains(e.target)) {
      slashMenu.classList.add('hidden')
      slashActive = false
    }
  })

  // ESC로 슬래시 메뉴 닫기
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && slashActive) {
      slashMenu.classList.add('hidden')
      slashActive = false
    }
  })

  // 폼 제출 시 에디터 HTML을 hidden input에 저장
  const form = editorEl.closest('form')
  if (form) {
    // HTMX 제출 전에 content 동기화
    document.body.addEventListener('htmx:configRequest', (evt) => {
      if (evt.detail.elt === form || form.contains(evt.detail.elt)) {
        contentInput.value = editor.getHTML()
      }
    })

    // 일반 폼 제출 대비
    form.addEventListener('submit', (e) => {
      contentInput.value = editor.getHTML()
    })
  }
}

// DOM 로드 후 초기화
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initEditor)
} else {
  initEditor()
}
