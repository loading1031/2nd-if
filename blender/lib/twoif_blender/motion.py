"""주기 함수 기반 모션.

모든 모션은 루프 길이(period)마다 정확히 같은 값으로 돌아와야 한다.
그래서 키프레임 대신 정수배 주파수의 sin 합으로만 움직임을 만든다.
"""

import math

import bpy

TAU = math.tau
GOLDEN = 2.399963  # 시드별 위상을 고르게 흩뿌리기 위한 황금각(rad)


def loop_noise(f: float, period: float, seed: float = 0.0, octaves: int = 3) -> float:
    """period마다 정확히 반복되는 의사 노이즈. 범위 약 -1~1."""
    total = 0.0
    norm = 0.0
    for k in range(1, octaves + 1):
        amp = 1.0 / k
        total += amp * math.sin(TAU * k * f / period + seed * k * GOLDEN)
        norm += amp
    return total / norm


def loop_wave(f: float, period: float, cycles: int = 1, phase: float = 0.0) -> float:
    """period 동안 cycles번 왕복하는 sin. cycles는 반드시 정수."""
    return math.sin(TAU * cycles * f / period + phase)


def register() -> None:
    """드라이버 표현식에서 쓸 함수를 등록. 장면 스크립트 시작 시 반드시 호출."""
    ns = bpy.app.driver_namespace
    ns["loop_noise"] = loop_noise
    ns["loop_wave"] = loop_wave


def drive(target, data_path: str, expression: str, index: int = -1) -> None:
    """target.data_path에 프레임 기반 드라이버를 건다.

    expression 안에서 `frame`(현재 프레임), loop_noise, loop_wave를 쓸 수 있다.
    예: drive(light.data, "energy", "40 * (1 + 0.2 * loop_noise(frame, 72, 3))")
    """
    fcurve = target.driver_add(data_path, index)
    driver = fcurve.driver
    driver.type = "SCRIPTED"
    driver.use_self = False
    driver.expression = expression
