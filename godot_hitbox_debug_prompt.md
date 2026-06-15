# Hitbox Debug Checklist

Use this when melee damage feels wrong.

## First Checks

1. Turn on visible collision shapes in Godot.
2. Confirm the attacker has:

```text
AttackPivot
  AttackHitbox
    AttackArea
```

3. Confirm the target has `BodyCollision`.
4. Confirm groups are correct:
   - player characters: `player`
   - enemies: `enemies`

## Timing Checks

- The attack animation should call `enable_attack_hitbox()` only on active frames.
- It should call `disable_attack_hitbox()` right after active frames.
- `AttackHitbox.monitoring` and `AttackArea.disabled` should not be edited directly inside physics callbacks; use deferred changes.

## Range Checks

- Do not use sprite size or texture frame size for combat range.
- Do not use center-to-center distance for melee damage.
- Use enemy AI ranges only to decide when to start an attack.
- Use `AttackHitbox` overlap to deal damage.

## Code Paths To Inspect

- `Scenes/PlayerScenes/player_character.gd`
- The active character config script, such as `MedievalKing/medieval_king.gd` or `Huntress/huntress.gd`
- The enemy script, such as `Scenes/MobScenes/Goblin/goblin.gd`
- The attack call tracks in the relevant `AnimationPlayer`
