// blender/lib/twoif_blender/motion.py 의 JS 포팅. 두 구현의 수식은 항상 같아야 한다.
const TAU = Math.PI * 2
const GOLDEN = 2.399963

export function loopNoise(f, period, seed = 0, octaves = 3) {
    let total = 0
    let norm = 0
    for (let k = 1; k <= octaves; k++) {
        const amp = 1 / k
        total += amp * Math.sin(TAU * k * f / period + seed * k * GOLDEN)
        norm += amp
    }
    return total / norm
}

export function loopWave(f, period, cycles = 1, phase = 0) {
    return Math.sin(TAU * cycles * f / period + phase)
}
