"""재사용 가능한 장면 컴포넌트.

각 컴포넌트는 키워드 인자(props)를 받아 오브젝트를 만들고 루트 오브젝트를 반환한다.
움직임은 전부 motion.drive()로 연결된 주기 드라이버이며, 키프레임을 찍지 않는다.
"""

import random

import bpy
from mathutils import Vector

from .motion import drive

Color = tuple[float, float, float]


def _link(obj: bpy.types.Object, parent: bpy.types.Object | None = None) -> bpy.types.Object:
    bpy.context.scene.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def _empty(name: str, location=(0, 0, 0)) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.location = location
    return _link(obj)


def material(name: str, color: Color, *, roughness: float = 0.6, emission: float = 0.0) -> bpy.types.Material:
    """단색 Principled 머티리얼. emission > 0이면 같은 색으로 발광."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if emission > 0:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat


def _mesh_object(name: str, op, material_: bpy.types.Material, **op_kwargs) -> bpy.types.Object:
    """bpy.ops 프리미티브로 메시를 만들고 머티리얼을 붙인다."""
    op(**op_kwargs)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material_)
    return obj


def reset_scene() -> None:
    """factory-startup 기본 오브젝트(큐브, 카메라, 라이트)를 모두 지운다."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def world(color: Color = (0.01, 0.009, 0.012), strength: float = 1.0) -> None:
    """배경 환경광. 어두운 장면은 거의 검정으로 둔다."""
    w = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*color, 1.0)
    bg.inputs["Strength"].default_value = strength


def room(
    *, floor_color: Color = (0.05, 0.035, 0.025), wall_color: Color = (0.04, 0.035, 0.035), wall_distance: float = 0.45
) -> bpy.types.Object:
    """바닥 + 뒷벽 배경. 카메라가 -Y 쪽에서 +Y를 바라본다고 가정."""
    root = _empty("room")
    floor = _mesh_object(
        "room_floor", bpy.ops.mesh.primitive_plane_add, material("floor", floor_color, roughness=0.8), size=8
    )
    wall = _mesh_object(
        "room_wall",
        bpy.ops.mesh.primitive_plane_add,
        material("wall", wall_color, roughness=0.9),
        size=8,
        location=(0, wall_distance, 4),
        rotation=(1.5708, 0, 0),
    )
    floor.parent = root
    wall.parent = root
    return root


def candle(
    *,
    period: int,
    location=(0, 0, 0),
    height: float = 0.14,
    radius: float = 0.022,
    flicker: float = 0.18,
    sway: float = 0.0015,
    light_power: float = 8.0,
    flame_color: Color = (1.0, 0.55, 0.22),
    seed: float = 0.0,
) -> bpy.types.Object:
    """촛불: 몸통 + 불꽃 + 포인트 라이트. 불꽃 밝기, 크기, 흔들림이 같은 노이즈를 공유해 동기화된다."""
    root = _empty("candle", location)

    body = _mesh_object(
        "candle_body",
        bpy.ops.mesh.primitive_cylinder_add,
        material("candle_wax", (0.85, 0.72, 0.55), roughness=0.4, emission=0.08),
        radius=radius,
        depth=height,
        location=(0, 0, height / 2),
        vertices=32,
    )
    body.parent = root
    body.location = (0, 0, height / 2)

    flame_z = height + 0.018
    flame = _mesh_object(
        "candle_flame",
        bpy.ops.mesh.primitive_uv_sphere_add,
        material("flame", flame_color, emission=6.0),
        radius=0.006,
        location=(0, 0, flame_z),
        segments=16,
        ring_count=8,
    )
    flame.parent = root
    flame.location = (0, 0, flame_z)
    flame.scale = (1, 1, 2.6)
    flame.visible_shadow = False  # 라이트가 불꽃 메시 안에 있으므로 그림자를 끄지 않으면 빛이 갇힌다

    light_data = bpy.data.lights.new("candle_light", "POINT")
    light_data.color = flame_color
    light_data.shadow_soft_size = 0.01
    light = _link(bpy.data.objects.new("candle_light", light_data), root)
    light.location = (0, 0, flame_z + 0.01)

    n = f"loop_noise(frame, {period}, {seed})"
    n2 = f"loop_noise(frame, {period}, {seed + 7})"
    drive(light_data, "energy", f"{light_power} * (1 + {flicker} * {n})")
    drive(flame, "scale", f"2.6 * (1 + {flicker * 0.6} * {n})", index=2)
    drive(flame, "location", f"{sway} * {n2}", index=0)
    drive(light, "location", f"{sway} * {n2}", index=0)

    return root


def dust_motes(
    *,
    period: int,
    count: int = 40,
    center=(0, 0, 0.3),
    extent=(0.6, 0.3, 0.3),
    drift: float = 0.02,
    size: float = 0.0007,
    brightness: float = 0.4,
    seed: int = 0,
) -> bpy.types.Object:
    """공기 중 먼지 입자. 메시 하나를 공유하는 인스턴스들이 각자 다른 위상으로 떠다닌다."""
    rng = random.Random(seed)
    root = _empty("dust", center)
    mesh_src = _mesh_object(
        "dust_src",
        bpy.ops.mesh.primitive_ico_sphere_add,
        material("dust", (1.0, 0.85, 0.65), emission=brightness),
        radius=size,
        subdivisions=1,
    )
    mesh = mesh_src.data
    bpy.data.objects.remove(mesh_src, do_unlink=True)

    for i in range(count):
        mote = _link(bpy.data.objects.new(f"dust_{i:03d}", mesh), root)
        base = [rng.uniform(-e, e) for e in extent]
        for axis in range(3):
            s = rng.uniform(0, 100)
            drive(mote, "location", f"{base[axis]:.4f} + {drift} * loop_noise(frame, {period}, {s:.3f})", index=axis)
    return root


def camera(
    *, period: int, location=(0, -0.9, 0.22), target=(0, 0, 0.12), lens: float = 50.0, breathe: float = 0.002
) -> bpy.types.Object:
    """카메라 + 아주 미세한 호흡(손떨림 수준). breathe=0이면 고정."""
    cam_data = bpy.data.cameras.new("camera")
    cam_data.lens = lens
    cam = _link(bpy.data.objects.new("camera", cam_data))
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    if breathe > 0:
        for axis, s in ((0, 11.0), (2, 23.0)):
            drive(cam, "location", f"{location[axis]} + {breathe} * loop_wave(frame, {period}, 1, {s})", index=axis)
    return cam
