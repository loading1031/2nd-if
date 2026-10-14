"""데모 장면: 어두운 방의 촛불 + 떠다니는 먼지. 3초 루프.

실행:
  Blender -b --factory-startup --python-exit-code 1 -P blender/scenes/candle_room.py -- --still 0
  Blender -b --factory-startup --python-exit-code 1 -P blender/scenes/candle_room.py -- --preview
  Blender -b --factory-startup --python-exit-code 1 -P blender/scenes/candle_room.py
  Blender -b --factory-startup --python-exit-code 1 -P blender/scenes/candle_room.py -- --glb
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from twoif_blender import components as c  # noqa: E402
from twoif_blender import motion, render  # noqa: E402

PERIOD = 72  # 24fps × 3초

argv = render.args()
still = int(argv[argv.index("--still") + 1]) if "--still" in argv else None

c.reset_scene()
motion.register()
render.setup(period=PERIOD, preview="--preview" in argv or still is not None)

c.world()
c.room()
c.candle(period=PERIOD, seed=1.3)
c.dust_motes(period=PERIOD, count=40, center=(0.05, 0.1, 0.18), extent=(0.35, 0.2, 0.12), seed=4)
c.camera(period=PERIOD)

if "--glb" in argv:
    render.export_glb("candle_room")
else:
    render.render_loop("candle_room", period=PERIOD, still=still)
