(function(GameIconColors) {
    const data = JSON.parse(document.getElementById('palette-data').textContent);
    GameIconColors.palettes = data.palettes;
    const names = {
        '파란색': '#0066CC',
        '파랑': '#0066CC',
        '파란': '#0066CC',
        blue: '#0066CC',
        '빨간색': '#FF0000',
        '빨강': '#FF0000',
        '빨간': '#FF0000',
        red: '#FF0000',
        '초록색': '#008000',
        '초록': '#008000',
        green: '#008000',
        '녹색': '#008000',
        '노란색': '#FFFF00',
        '노랑': '#FFFF00',
        yellow: '#FFFF00',
        '보라색': '#800080',
        '보라': '#800080',
        purple: '#800080',
        '분홍색': '#FFC0CB',
        '분홍': '#FFC0CB',
        pink: '#FFC0CB',
        '주황색': '#FF8000',
        '주황': '#FF8000',
        orange: '#FF8000',
        '갈색': '#804020',
        brown: '#804020',
        '하늘색': '#87CEEB',
        '청록색': '#008080',
        teal: '#008080',
        '남색': '#000080',
        navy: '#000080',
        '검정색': '#000000',
        '검정': '#000000',
        black: '#000000',
        '흰색': '#FFFFFF',
        white: '#FFFFFF',
        '회색': '#808080',
        gray: '#808080',
        '은색': '#C0C0C0',
        silver: '#C0C0C0',
        '금색': '#FFD700',
        gold: '#FFD700'
    };
    function normalizeColor(value) {
        const input = value.trim().toLowerCase();
        if (names[input]) return names[input];
        if (/^#?[0-9a-f]{6}$/.test(input)) return '#' + input.replace('#', '').toUpperCase();
        if (/^#[0-9a-f]{3}$/.test(input)) return '#' + input.slice(1).split('').map((c)=>c + c).join('').toUpperCase();
        return null;
    }
    GameIconColors.normalizeColor = normalizeColor;
    function oklab(hex) {
        const [r, g, b] = [
            1,
            3,
            5
        ].map((i)=>{
            const v = parseInt(hex.slice(i, i + 2), 16) / 255;
            return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4;
        });
        const l = Math.cbrt(.4122214708 * r + .5363325363 * g + .0514459929 * b);
        const m = Math.cbrt(.2119034982 * r + .6806995451 * g + .1073969566 * b);
        const s = Math.cbrt(.0883024619 * r + .2817188376 * g + .6299787005 * b);
        return [
            .2104542553 * l + .793617785 * m - .0040720468 * s,
            1.9779984951 * l - 2.428592205 * m + .4505937099 * s,
            .0259040371 * l + .7827717662 * m - .808675766 * s
        ];
    }
    function nearest(value, paletteId) {
        const hex = normalizeColor(value);
        if (!hex) return null;
        const target = oklab(hex);
        let best = null;
        for (const p of GameIconColors.palettes.filter((p)=>!paletteId || p.id === paletteId)){
            for (const foreground of p.colors){
                const lab = oklab(foreground);
                const chromaTarget = Math.hypot(target[1], target[2]);
                const chroma = Math.hypot(lab[1], lab[2]);
                const deltaA = target[1] - lab[1], deltaB = target[2] - lab[2];
                const deltaChroma = chromaTarget - chroma;
                const hueSquared = Math.max(0, deltaA ** 2 + deltaB ** 2 - deltaChroma ** 2);
                const distance = Math.sqrt(.25 * (target[0] - lab[0]) ** 2 + deltaChroma ** 2 + 9 * hueSquared);
                if (!best || distance < best.distance) best = {
                    requestedColor: hex,
                    paletteId: p.id,
                    foreground,
                    background: p.background,
                    distance
                };
            }
        }
        return best;
    }
    GameIconColors.nearest = nearest;
    function init() {
        const palette = document.getElementById('palette');
        const swatches = document.getElementById('swatches');
        const background = document.getElementById('palette-background');
        const requested = document.getElementById('requested-color');
        const status = document.getElementById('color-status');
        const scope = document.getElementById('match-scope');
        const darkButton = document.getElementById('background');
        let foreground = '';
        let appearance = null;
        for (const p of GameIconColors.palettes)palette.add(new Option(p.id, p.id));
        function apply() {
            const p = GameIconColors.palettes.find((p)=>p.id === palette.value);
            document.body.classList.toggle('colorized', Boolean(p));
            darkButton.disabled = Boolean(p);
            background.disabled = !p;
            swatches.replaceChildren();
            if (!p) {
                status.textContent = '흑백 원본 · 작품 색상 적용 시 전체 팔레트에서 가까운 색을 찾습니다.';
                return;
            }
            if (!p.colors.includes(foreground)) foreground = p.colors[0];
            document.body.style.setProperty('--icon-foreground', foreground);
            document.body.style.setProperty('--icon-background', background.value === 'palette' ? p.background : '#FFFFFF');
            for (const hex of p.colors){
                const button = document.createElement('button');
                button.type = 'button';
                button.style.background = hex;
                button.title = hex;
                button.setAttribute('aria-label', hex);
                button.setAttribute('aria-pressed', String(hex === foreground));
                button.addEventListener('click', ()=>{
                    foreground = hex;
                    appearance = null;
                    apply();
                });
                swatches.append(button);
            }
            status.textContent = (appearance ? `입력 ${appearance.requestedColor} → ` : '') + `${p.id} · 아이콘 ${foreground} · ${background.value === 'palette' ? '배경 ' + p.background : '투명 · 밝은 바탕'} · 목록 전체 적용`;
        }
        function match() {
            const matched = nearest(requested.value, scope.value === 'selected' ? palette.value || undefined : undefined);
            if (!matched) {
                status.textContent = '지원하는 색 이름(파란색, blue 등) 또는 HEX 코드(#3366CC)를 입력하세요. 기존 배색을 유지합니다.';
                return;
            }
            appearance = matched;
            palette.value = matched.paletteId;
            foreground = matched.foreground;
            apply();
        }
        palette.addEventListener('change', ()=>{
            foreground = '';
            appearance = null;
            apply();
        });
        background.addEventListener('change', apply);
        document.getElementById('match-color').addEventListener('click', match);
        requested.addEventListener('keydown', (e)=>{
            if (e.key === 'Enter') match();
        });
        apply();
    }
    GameIconColors.init = init;
})(GameIconColors || (GameIconColors = {}));
var GameIconColors;
