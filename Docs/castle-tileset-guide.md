# Castle Tileset Guide

Source art lives in `TileSetCastle/`. Keep that folder for the original PNGs and their Godot `.import` files only.

## Tile Size

Use `16x16` when slicing these sheets into Godot TileSets.

## Layer Order

Use separate `TileMapLayer` nodes:

1. `BackgroundSprite` - `background.png`
2. `FarWalls` - `walls_far.png`
3. `FarSideTop` - `walls_side_top_far.png`
4. `FarObjects` - `env_objects_far.png`
5. `MainWalls` - `walls.png`
6. `SideTop` - `walls_side_top.png`
7. `Ground` - `ground.png` or `terrain.png`
8. `WoodStructures` - `wood_env.png`
9. `Decor` - `env_objects.png` and `environment.png`
10. `Actors`

The `far` sheets are darker and lower contrast. Paint them before the matching foreground sheets so the scene has depth.

## Sheet Notes

| PNG | Use |
| --- | --- |
| `background.png` | Distant mountain/sky backdrop, not a TileMap layer |
| `ground.png` | Stone platforms, bridges, ledges, stairs, red carpet trim |
| `terrain.png` | Mossy rock, dirt, cave chunks, natural platforms |
| `walls_far.png` | Shadowed background wall blocks |
| `walls.png` | Main readable castle masonry |
| `walls_side_top_far.png` | Dark side/top wall depth pieces |
| `walls_side_top.png` | Foreground side/top trims and room frames |
| `env_objects_far.png` | Shadowed arches, windows, columns, furniture silhouettes |
| `env_objects.png` | Foreground arches, windows, columns, signs, furniture |
| `environment.png` | Small props: banners, chains, doors, lamps, fences |
| `wood_env.png` | Wood beams, braces, gates, supports, barricades |
| `anim_light*.png` | AnimatedSprite2D light and torch scenes, not TileSets |

## Inspector And Groups

Static castle layers do not need signals. Suggested groups:

| Node kind | Group |
| --- | --- |
| Far wall/object layers | `castle_far` |
| Foreground visual layers | `castle_visual` |
| Solid floor layers | `castle_solid` |
| Animated torch/light scenes | `castle_light` |

Keep gameplay groups as they are: `player` and `enemies`.
