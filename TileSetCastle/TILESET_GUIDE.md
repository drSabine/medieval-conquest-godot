# Castle Tileset Guide

Tile size: `16x16`.

Contact sheet: `../Docs/tileset_castle_contact_sheet.png`

## TileSet Resources

Assign these in the Inspector on `TileMapLayer.tile_set`.

| Source | Resource | Use |
| --- | --- | --- |
| `ground.png` | `ground_tileset.tres` | Stone platforms, bridges, ledges, red carpet trim |
| `terrain.png` | `terrain_tileset.tres` | Dirt, mossy rock, cave edges, natural platforms |
| `walls_far.png` | `walls_far_tileset.tres` | Dark background wall layer |
| `walls.png` | `walls_tileset.tres` | Main readable castle wall layer |
| `walls_side_top_far.png` | `walls_side_top_far_tileset.tres` | Dark side/top depth layer |
| `walls_side_top.png` | `walls_side_top_tileset.tres` | Foreground side/top wall trims |
| `env_objects_far.png` | `env_objects_far_tileset.tres` | Dark background arches, windows, columns, furniture silhouettes |
| `env_objects.png` | `env_objects_tileset.tres` | Foreground arches, windows, columns, furniture, signs |
| `environment.png` | `environment_tileset.tres` | Small decor: banners, lamps, chains, fences, doors |
| `wood_env.png` | `wood_env_tileset.tres` | Wood beams, braces, gates, supports, barricades |

## Non-TileSet Art

- `background.png`: use as `Sprite2D` or a parallax background.
- `anim_light1.png`, `anim_light2.png`, `anim_light3.png`, `anim_lights.png`: use as `AnimatedSprite2D` light/torch scenes.

## Recommended Layer Order

Use separate `TileMapLayer` nodes:

1. `BackgroundSprite`
2. `FarWalls`
3. `FarSideTop`
4. `FarObjects`
5. `MainWalls`
6. `SideTop`
7. `Ground`
8. `WoodStructures`
9. `Decor`
10. `Actors`

The `far` sheets are darker and lower contrast. Paint them before the matching foreground sheets so the room reads with depth.

## Inspector And Groups

Static castle layers do not need signals. Keep organization simple:

| Node kind | Group |
| --- | --- |
| Far wall/object layers | `castle_far` |
| Foreground visual layers | `castle_visual` |
| Solid floor layers | `castle_solid` |
| Animated torch/light scenes | `castle_light` |
| Player/enemy scenes | existing `player` and `enemies` groups |

## Visual Notes For Generation

- `background.png`: cyan sky and gray/brown mountains; use as distant outdoor backdrop.
- `ground.png`: dark stone platforms, red carpet, bridges, stairs, ledges.
- `terrain.png`: mossy green rock, tan dirt, cave chunks.
- `walls_far.png`: shadowed masonry for background depth.
- `walls.png`: brighter gray/brown masonry for main castle structure.
- `walls_side_top_far.png`: dark side/top trim depth pieces.
- `walls_side_top.png`: foreground wall caps, side trims, room frames.
- `env_objects_far.png`: shadowed arches, windows, columns, furniture silhouettes.
- `env_objects.png`: readable foreground props, arches, windows, furniture.
- `environment.png`: small props, banners, chains, doors, lamps, fences.
- `wood_env.png`: wood construction pieces and supports.
- `anim_light*.png`: flame, brazier, chandelier, and torch animation sheets.

Prompt seed for future castle generation:

```text
Layered pixel-art medieval castle interior using dark far wall tiles, brighter foreground stone walls, mossy ground platforms, wood supports, arches, banners, small props, and warm animated torch lights.
```
