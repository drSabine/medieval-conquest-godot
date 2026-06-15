# Goblin Bomb Throw Notes

`Attack3.png` is a full goblin bomb-throw body animation. `Bomb_sprite.png` contains the flying bomb and explosion frames. The missing piece is the projectile scene and AI wiring.

## Current State

- Goblin melee currently uses `GoblinAtk1` and `GoblinAtk2`.
- Close-range attacks are chosen by `attack_range`.
- Damage should still come from active hitboxes or projectile overlap, not distance checks.

## Implementation Steps

1. Add `GoblinAtk3` to `goblin.tscn` using the 12 frames from `Attack3.png`.
2. Create `Scenes/MobScenes/Goblin/bomb_projectile.tscn`.
3. Add an `AnimationPlayer` call track at the release frame that calls `spawn_bomb()`.
4. Add a longer `throw_range` so the goblin throws when the player is outside melee range but still nearby.

## Projectile Scene Shape

```text
BombProjectile (Area2D)
  AnimatedSprite2D
  CollisionShape2D
```

Projectile script responsibilities:

- State flow: `flying` then `exploding`.
- While flying, move forward or arc toward the player.
- On player hit, call `take_damage`, disable collision, and play explosion.
- Free itself when the explosion animation ends or after a timeout.

## Spawn Example

```gdscript
const BOMB_PROJECTILE = preload("res://Scenes/MobScenes/Goblin/bomb_projectile.tscn")

func spawn_bomb() -> void:
	var bomb = BOMB_PROJECTILE.instantiate()
	bomb.global_position = global_position + Vector2(attack_pivot.scale.x * 24.0, -20.0)
	bomb.direction = attack_pivot.scale.x
	get_parent().add_child(bomb)
```

Keep melee and projectile damage separate: melee uses `AttackHitbox`, bomb uses its own `Area2D`.
