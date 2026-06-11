# Huntress Spear Throw Plan

`HuntressAtk3` is not a body animation like `HuntressAtk1` or `HuntressAtk2`.
The current `Attack3.png` sheet shows the thrown spear traveling without the Huntress body.

## Current Decision

Defer spear throw for now.
The Huntress currently uses only:

- `HuntressAtk1`
- `HuntressAtk2`

These are implemented as melee attacks with a separate `AttackHitbox`, matching the Medieval King melee setup.

## Why Atk3 Is Deferred

- The body sprite is not present in the `Attack3.png` sheet.
- Mixing projectile travel frames into the Huntress body `AnimatedSprite2D` would make the character disappear during the attack.
- Projectile logic should be separate from body animation logic.

## Recommended Future Implementation

Create a separate projectile scene, for example:

```text
Scenes/PlayerScenes/Huntress/spear_projectile.tscn
- Area2D
- AnimatedSprite2D
- CollisionShape2D
```

Recommended future flow:

1. Add a real body throw animation for the Huntress if one becomes available.
2. Play that throw animation on the Huntress body.
3. At the release frame, spawn `spear_projectile.tscn`.
4. Let the projectile handle:
   - forward travel
   - collision
   - enemy damage
   - despawn on hit or timeout

## Current Asset Notes

- `Attack1.png`: 5 frames, body melee slash
- `Attack2.png`: 5 frames, body melee slash
- `Attack3.png`: 7 frames, projectile travel sheet without body
- `Spear move.png`: projectile motion support asset
- `Spear.png`: static projectile asset

## Important Constraint

Do not add `HuntressAtk3` to the melee combo until a proper body throw animation or dedicated projectile flow is in place.
