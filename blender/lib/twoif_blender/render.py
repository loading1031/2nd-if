"""렌더 설정, 루프 검증, webm 인코딩."""

import shutil
import subprocess
import sys
from pathlib import Path

import bpy

OUT_ROOT = Path(__file__).resolve().parents[2] / "out"


def args() -> list[str]:
    """`Blender -b -P scene.py -- --preview` 에서 `--` 뒤 인자만 반환."""
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def setup(
    *, period: int, fps: int = 24, resolution=(1280, 720), samples: int = 32, preview: bool = False
) -> bpy.types.Scene:
    """루프 렌더 기본 설정. 프레임 0 ~ period-1을 렌더하면 period에서 0으로 끊김 없이 이어진다."""
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 8 if preview else samples
    scene.render.fps = fps
    scale = 0.5 if preview else 1.0
    scene.render.resolution_x = int(resolution[0] * scale)
    scene.render.resolution_y = int(resolution[1] * scale)
    scene.render.resolution_percentage = 100
    scene.frame_start = 0
    scene.frame_end = period - 1
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.file_format = "PNG"
    return scene


def check_loop(scene: bpy.types.Scene, period: int, tol: float = 1e-4) -> None:
    """모든 드라이버 값이 frame 0과 frame period에서 같은지 확인. 다르면 루프가 튄다."""

    def snapshot(frame: int) -> dict[str, float]:
        scene.frame_set(frame)
        values = {}
        for id_ in [*bpy.data.objects, *bpy.data.lights, *bpy.data.cameras]:
            anim = id_.animation_data
            if not anim:
                continue
            for fc in anim.drivers:
                value = id_.path_resolve(fc.data_path)
                if hasattr(value, "__len__"):
                    value = value[fc.array_index]
                values[f"{id_.name}.{fc.data_path}[{fc.array_index}]"] = value
        return values

    start, end = snapshot(0), snapshot(period)
    broken = [k for k in start if abs(start[k] - end[k]) > tol]
    if broken:
        raise RuntimeError(f"루프가 이어지지 않는 드라이버 {len(broken)}개: {broken[:5]}")
    print(f"[loop] OK: drivers={len(start)} period={period}")


def render_loop(name: str, *, period: int, still: int | None = None) -> Path:
    """루프 검증 → PNG 시퀀스 렌더 → webm 인코딩. still을 주면 그 프레임 한 장만 렌더."""
    scene = bpy.context.scene
    check_loop(scene, period)
    out_dir = OUT_ROOT / name

    if still is not None:
        scene.frame_set(still)
        scene.render.filepath = str(out_dir / f"still_{still:04d}.png")
        bpy.ops.render.render(write_still=True)
        return Path(scene.render.filepath)

    frames = out_dir / "frames"
    shutil.rmtree(frames, ignore_errors=True)
    scene.render.filepath = str(frames / "####")
    bpy.ops.render.render(animation=True)

    webm = OUT_ROOT / f"{name}.webm"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-framerate",
            str(scene.render.fps),
            "-i",
            str(frames / "%04d.png"),
            "-c:v",
            "libvpx-vp9",
            "-b:v",
            "0",
            "-crf",
            "34",
            "-pix_fmt",
            "yuv420p",
            "-row-mt",
            "1",
            "-an",
            str(webm),
        ],
        check=True,
    )
    print(f"[render] {webm}")
    return webm


def export_glb(name: str) -> Path:
    """실시간 3D(three.js)용 glb 내보내기.

    드라이버 모션과 라이트는 내보내지 않는다. 웹에서 같은 주기 함수(loop.js)로 다시 움직이고,
    라이트도 웹에서 오브젝트 이름(`*_light`) 위치를 기준으로 새로 만든다.
    """
    bpy.context.scene.frame_set(0)
    path = OUT_ROOT / f"{name}.glb"
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        export_animations=False,
        export_lights=False,
        export_cameras=True,
        export_extras=True,
        export_yup=True,
    )
    print(f"[export] {path}")
    return path
