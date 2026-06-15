# Huntress Spear Throw Notes

`Attack3.png` is a full Huntress spear-throw body animation. The missing piece is not the body art; it is the projectile scene and the animation call that spawns it.

## Current State

- Huntress melee combo currently uses `HuntressAtk1` and `HuntressAtk2`.
- Shared player behavior lives in `Scenes/PlayerScenes/player_character.gd`.
- Huntress-specific animation names and hitbox tuning live in `Scenes/PlayerScenes/Huntress/huntress.gd`.

## Implementation Steps

1. Add `HuntressAtk3` to `huntress.tscn` using the 7 frames from `Attack3.png`.
2. Create `Scenes/PlayerScenes/Huntress/spear_projectile.tscn`.
3. Add a call track in `AnimationPlayer` at the release frame that calls `spawn_spear()`.
4. Add `HuntressAtk3` and its matching hitbox/call animation name to `attack_animations` and `attack_hitbox_animations` in `huntress.gd`.

## Projectile Scene Shape

```text
SpearProjectile (Area2D)
  AnimatedSprite2D
  CollisionShape2D
```

Projectile script responsibilities:

- Move forward using a passed-in `direction`.
- Damage bodies in the `enemies` group that have `take_damage`.
- Free itself on hit, timeout, or max travel distance.

## Spawn Example

```gdscript
const SPEAR_PROJECTILE = preload("res://Scenes/PlayerScenes/Huntress/spear_projectile.tscn")

func spawn_spear() -> void:
	var spear = SPEAR_PROJECTILE.instantiate()
	spear.global_position = global_position + Vector2(attack_pivot.scale.x * 20.0, -10.0)
	spear.direction = attack_pivot.scale.x
	get_parent().add_child(spear)
```

Keep the throw as a committed grounded attack, matching the shared player controller.
