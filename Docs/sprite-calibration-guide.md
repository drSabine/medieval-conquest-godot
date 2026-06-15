# Sprite And Hitbox Calibration

Many asset-pack sprites have large transparent padding. The player may look far away even when physics bodies are close. Treat this as a visual alignment problem first, not a combat logic problem.

## Current Node Contract

Player scenes and enemy scenes should keep this shape:

```text
CharacterBody2D
  AnimatedSprite2D
  BodyCollision
  AttackPivot
    AttackHitbox
      AttackArea
  AnimationPlayer
```

Scripts should use:

- `BodyCollision` for body position, AI range, and character blocking.
- `AttackArea` for attack size and offset.
- `AttackHitbox` for actual damage overlap.
- Groups: `player` for playable characters, `enemies` for mobs.

## Player Controller

Shared player logic lives in:

```text
Scenes/PlayerScenes/player_character.gd
```

Knight and Huntress scripts should mostly configure:

- animation names
- combo order
- hitbox sizes
- hitbox positions
- movement values

Avoid duplicating movement, damage, combo, or hitbox logic in each character script.

## Attack Hitbox Rules

- `AnimationPlayer` enables and disables attack timing with `enable_attack_hitbox()` and `disable_attack_hitbox()`.
- `disable_attack_hitbox()` should use `set_deferred()` for physics properties.
- Damage is applied in `try_hit_body()` only while `is_attack_active` is true.
- Do not use sprite bounds or center-to-center distance for melee damage.

## Alignment Checklist

Use this when adding or fixing a character:

1. Enable visible collision shapes in Godot.
2. Make sure `BodyCollision` covers the actual body, not the transparent frame.
3. Tune `AnimatedSprite2D.position`, `scale`, or `offset` until the feet sit correctly on the floor.
4. Tune each attack's `AttackArea` size and position while watching the active frames.
5. Confirm the target is in the correct group.
6. Confirm the hitbox starts disabled and only enables during active attack frames.

## Common Problems

| Problem | Likely cause | Fix |
| --- | --- | --- |
| Attack hits from too far away | `AttackArea` too wide or offset too far forward | Tune hitbox per attack |
| Attack never hits | Wrong group, disabled hitbox, or bad signal connection | Check `player`/`enemies`, `body_entered`, and active frames |
| Hitbox stays active | Missing disable call in the hitbox animation | Add `disable_attack_hitbox()` after active frames |
| Character looks misaligned | Transparent sprite padding | Tune sprite position/offset, not combat logic |
| Godot warns about flushing queries | Physics property changed inside callback | Use `set_deferred()` for `monitoring` and `disabled` |

## Enemy Ranges

Enemy range checks are only for choosing behavior. For example, the goblin can use rectangular detection and attack ranges to decide whether to chase or attack.

Actual damage should still come from active `AttackHitbox` overlap or a projectile `Area2D`.
