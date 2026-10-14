// candle_room 실시간 3D PoC
// - 장면 지오메트리/머티리얼: Blender에서 내보낸 glb (blender/scenes/candle_room.py -- --glb)
// - 모션: Blender 드라이버와 같은 주기 함수(loop.js)를 웹에서 다시 적용
// - 인터랙션: 사물 클릭 → 카메라 dolly-in, 빈 곳 클릭 → dolly-out / 복귀 (FOV 고정 = 진짜 원근 변화)
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js'
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js'
import { loopNoise, loopWave } from './loop.js'

const PERIOD = 72           // candle_room.py 의 PERIOD와 동일
const FPS = 24
const FOCUSABLE = new Set(['candle'])
const NEAR_FACTOR = 3.2     // 다가갈 때 거리 = 대상 크기 × NEAR_FACTOR
const FAR_FACTOR = 1.8      // 물러날 때 거리 = 기본 거리 × FAR_FACTOR
const MOVE_MS = 1800
const TEXT_SHIFT = 0.17     // 기본 시점에서 피사체를 오른쪽으로 미는 비율 (글 칸 확보, 렌즈 시프트)
const LIGHT_INTENSITY = 0.35
const CANDLE_SEED = 1.3     // candle(seed=1.3)과 동일

// --- 렌더러 ---
const renderer = new THREE.WebGLRenderer({ antialias: true })
renderer.setPixelRatio(Math.min(devicePixelRatio, 2))
renderer.setSize(innerWidth, innerHeight)
renderer.toneMapping = THREE.AgXToneMapping
renderer.toneMappingExposure = 1.0
renderer.shadowMap.enabled = true
renderer.shadowMap.type = THREE.PCFSoftShadowMap
document.body.prepend(renderer.domElement)

const scene = new THREE.Scene()
scene.background = new THREE.Color(0x020101)
scene.add(new THREE.AmbientLight(0xffe2c4, 0.015))

const gltf = await new GLTFLoader().loadAsync('../out/candle_room.glb')
scene.add(gltf.scene)
gltf.scene.updateMatrixWorld(true)

// --- 카메라: Blender 카메라 시점을 기본값으로 ---
const src = gltf.cameras[0]
const camera = new THREE.PerspectiveCamera(src.fov, innerWidth / innerHeight, 0.01, 50)
const homePos = src.getWorldPosition(new THREE.Vector3())
const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(src.getWorldQuaternion(new THREE.Quaternion()))

// --- 촛불: 불꽃 위치에 실시간 포인트 라이트 ---
const flame = gltf.scene.getObjectByName('candle_flame')
const flameBase = { x: flame.position.x, sy: flame.scale.y }
const light = new THREE.PointLight(0xff8c38, LIGHT_INTENSITY, 0, 2)
light.castShadow = true
light.shadow.mapSize.set(1024, 1024)
light.shadow.radius = 4
light.shadow.bias = -0.0005
light.shadow.camera.near = 0.005  // 기본값 0.5m는 이 장면 스케일(수십 cm)보다 커서 그림자가 사라진다
light.shadow.camera.far = 5
light.position.copy(flame.getWorldPosition(new THREE.Vector3())).add(new THREE.Vector3(0, 0.012, 0))
const lightBaseX = light.position.x
scene.add(light)

gltf.scene.traverse((o) => {
    if (!o.isMesh) return
    o.castShadow = o.name !== 'candle_flame' && !o.name.startsWith('dust_')
    o.receiveShadow = true
})

// --- 먼지: 각 입자가 축마다 다른 시드로 떠다님 (dust_motes와 같은 방식) ---
let rngState = 4
const rng = () => ((rngState = (rngState * 16807) % 2147483647) / 2147483647)
const dust = []
gltf.scene.traverse((o) => {
    if (/^dust_\d+$/.test(o.name)) dust.push({ o, base: o.position.clone(), seeds: [rng() * 100, rng() * 100, rng() * 100] })
})
const DUST_DRIFT = 0.02

// --- 시점 상태 ---
const componentOf = (obj) => {
    while (obj.parent && obj.parent !== gltf.scene) obj = obj.parent
    return obj
}
const boundsOf = (obj) => new THREE.Box3().setFromObject(obj)

const candleRoot = gltf.scene.getObjectByName('candle')
const homeTarget = boundsOf(candleRoot).getCenter(new THREE.Vector3())
const homeDist = homePos.distanceTo(homeTarget)
// Blender 카메라가 바라보던 방향을 유지하면서 촛불 중심 거리의 점을 기준점으로
homeTarget.copy(homePos).addScaledVector(forward, homeDist)

const views = {
    home: () => ({ pos: homePos.clone(), target: homeTarget.clone(), shift: TEXT_SHIFT }),
    far: () => ({
        pos: homeTarget.clone().add(homePos.clone().sub(homeTarget).multiplyScalar(FAR_FACTOR)),
        target: homeTarget.clone(), shift: 0,
    }),
    near: (root) => {
        const box = boundsOf(root)
        const center = box.getCenter(new THREE.Vector3())
        const size = box.getSize(new THREE.Vector3()).length()
        const dir = homePos.clone().sub(center).normalize()
        return { pos: center.clone().addScaledVector(dir, size * NEAR_FACTOR), target: center, shift: 0 }
    },
}

let mode = 'home'
let current = views.home()
let tween = null

function goTo(nextMode, view) {
    mode = nextMode
    document.body.classList.toggle('exploring', mode !== 'home')
    tween = { from: { pos: current.pos.clone(), target: current.target.clone(), shift: current.shift }, to: view, t0: performance.now() }
}

const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)

function stepTween(now) {
    if (!tween) return
    const t = Math.min((now - tween.t0) / MOVE_MS, 1)
    const k = ease(t)
    current.pos.lerpVectors(tween.from.pos, tween.to.pos, k)
    current.target.lerpVectors(tween.from.target, tween.to.target, k)
    current.shift = tween.from.shift + (tween.to.shift - tween.from.shift) * k
    if (t === 1) tween = null
}

// --- 입력 ---
const raycaster = new THREE.Raycaster()
const pointer = new THREE.Vector2()
function pick(e) {
    pointer.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1)
    raycaster.setFromCamera(pointer, camera)
    const hit = raycaster.intersectObject(gltf.scene, true).find((h) => !h.object.name.startsWith('dust_'))
    return hit ? componentOf(hit.object) : null
}

renderer.domElement.addEventListener('click', (e) => {
    const root = pick(e)
    if (root && FOCUSABLE.has(root.name) && mode !== 'near') return goTo('near', views.near(root))
    if (mode === 'home') return goTo('far', views.far())
    goTo('home', views.home())
})
renderer.domElement.addEventListener('pointermove', (e) => {
    const root = pick(e)
    renderer.domElement.style.cursor = root && FOCUSABLE.has(root.name) ? 'pointer' : 'default'
})
addEventListener('keydown', (e) => { if (e.key === 'Escape') goTo('home', views.home()) })

// --- 후처리: 불꽃 번짐 ---
const composer = new EffectComposer(renderer)
composer.addPass(new RenderPass(scene, camera))
const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.55, 0.5, 0.8)
composer.addPass(bloom)
composer.addPass(new OutputPass())

function applyViewOffset() {
    const w = innerWidth
    const h = innerHeight
    camera.setViewOffset(w, h, -current.shift * w, 0, w, h)
}

addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight
    renderer.setSize(innerWidth, innerHeight)
    composer.setSize(innerWidth, innerHeight)
    applyViewOffset()
})

// --- 루프 ---
renderer.setAnimationLoop((now) => {
    const f = ((now / 1000) * FPS) % PERIOD

    const n = loopNoise(f, PERIOD, CANDLE_SEED)
    const n2 = loopNoise(f, PERIOD, CANDLE_SEED + 7)
    light.intensity = LIGHT_INTENSITY * (1 + 0.18 * n)
    flame.scale.y = flameBase.sy * (1 + 0.108 * n)
    flame.position.x = flameBase.x + 0.0015 * n2
    light.position.x = lightBaseX + 0.0015 * n2

    for (const d of dust) {
        d.o.position.set(
            d.base.x + DUST_DRIFT * loopNoise(f, PERIOD, d.seeds[0]),
            d.base.y + DUST_DRIFT * loopNoise(f, PERIOD, d.seeds[1]),
            d.base.z + DUST_DRIFT * loopNoise(f, PERIOD, d.seeds[2]),
        )
    }

    stepTween(now)
    camera.position.copy(current.pos)
    camera.position.x += 0.002 * loopWave(f, PERIOD, 1, 11)
    camera.position.y += 0.002 * loopWave(f, PERIOD, 1, 23)
    camera.lookAt(current.target)
    applyViewOffset()

    composer.render()
})

window.__poc = { goTo, views, get mode() { return mode } }
