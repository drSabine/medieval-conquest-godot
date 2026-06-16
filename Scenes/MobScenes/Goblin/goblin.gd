extends CombatActor
## Goblin enemy: stands guard, then chases and attacks the hero when one comes
## near. Shared combat plumbing (hitbox, hit resolution, sfx, damage numbers,
## facing, gravity) lives in CombatActor; this script adds the enemy AI on top.

@export_group("Movement")
@export var speed := 140.0
@export var detection_range := Vector2(520.0, 48.0)
# only swing when the player is actually within the editor-set hitbox reach (~44px)
@export var attack_range := Vector2(40.0, 22.0)

@export_group("Combat")
@export var max_health := 30

@export_group("Audio")
@export var attack_sound_start_offsets: Array[float] = [0.45, 0.45]

const HealthBar := preload("res://Scripts/health_bar_2d.gd")

const IDLE_ANIMATION := "GoblinIdle"
const RUN_ANIMATION := "GoblinRun"
const HIT_ANIMATION := "GoblinHit"
const DEATH_ANIMATION := "GoblinDeath"
const HURT_STUN_TIME := 0.35

const ATK_SFX := preload("res://Assets/Mobs/Goblin/Effects/atk.mp3")
const ALERT_SFX := preload("res://Assets/Mobs/Goblin/Effects/Goblin saw you.mp3")
const DEATH_SFX := preload("res://Assets/Mobs/Goblin/Effects/goblin-death.mp3")

const ATTACK_ANIMATIONS := ["GoblinAtk1", "GoblinAtk2"]
const ATTACK_HITBOX_ANIMATIONS := ["Atk1Hitbox", "Atk2Hitbox"]

var current_health := 0
var is_hurt := false
var is_dead := false
var has_played_alert := false
var hurt_stun_timer := 0.0
var target: Node2D
var health_bar: HealthBar

func _ready() -> void:
	add_to_group("enemies")
	target_group = "player"
	attack_damages = [7, 10]
	fallback_damage = 7
	current_health = max_health
	setup_sfx_player()
	health_bar = HealthBar.new()
	add_child(health_bar)
	disable_attack_hitbox()
	anim.animation_finished.connect(_on_animation_finished)

func _physics_process(delta: float) -> void:
	apply_gravity(delta)

	if hurt_stun_timer > 0.0:
		hurt_stun_timer = maxf(0.0, hurt_stun_timer - delta)
		if hurt_stun_timer == 0.0:
			is_hurt = false

	target = find_player()

	# Decide how to move this frame, in priority order:
	if is_dead or is_hurt:
		velocity.x = move_toward(velocity.x, 0.0, speed)   # stunned/dead: skid to a stop
	elif is_attacking:
		velocity.x = 0.0                                   # mid-swing: stand still
	elif target != null:
		update_ai()                                        # hero exists: chase/attack
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed)   # no hero: idle

	move_and_slide()
	update_animation()

func update_ai() -> void:
	# Where is the hero relative to us? (positive x = to our right)
	var delta_to_target := get_body_delta_to(target)

	# Always turn to face the hero.
	if delta_to_target.x != 0.0:
		update_facing(signf(delta_to_target.x))

	# Yell once the first time the hero enters our detection box.
	if is_inside_rect(delta_to_target, detection_range):
		play_alert_sound_once()

	# Close enough to hit -> attack. Within sight -> walk toward. Otherwise -> stop.
	if is_inside_rect(delta_to_target, attack_range):
		velocity.x = 0.0
		start_attack()
	elif is_inside_rect(delta_to_target, detection_range):
		velocity.x = signf(delta_to_target.x) * speed
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed)

# Only one hero is ever in the level, so this just returns it (or null if the
# hero is gone). The goblin chases/attacks whatever this hands back.
func find_player() -> Node2D:
	var players := get_tree().get_nodes_in_group("player")
	if players.is_empty():
		return null
	return players[0] as Node2D

func get_body_delta_to(body: Node2D) -> Vector2:
	return get_body_position(body) - body_collision.global_position

func get_body_position(body: Node2D) -> Vector2:
	var shape := body.get_node("BodyCollision") as CollisionShape2D
	return shape.global_position

func is_inside_rect(delta: Vector2, rect_size: Vector2) -> bool:
	return absf(delta.x) <= rect_size.x and absf(delta.y) <= rect_size.y

func start_attack() -> void:
	if is_attacking or is_hurt or is_dead or hurt_stun_timer > 0.0:
		return

	is_attacking = true
	hit_targets.clear()
	attack_index = (attack_index + 1) % ATTACK_ANIMATIONS.size()
	play_attack_sound(attack_index)

	# NOTE: the attack hitbox is whatever is set on AttackArea in goblin.tscn.
	# We deliberately do NOT resize it per-attack so it matches the editor value.
	anim.play(ATTACK_ANIMATIONS[attack_index])
	animation_player.play(ATTACK_HITBOX_ANIMATIONS[attack_index])

func play_alert_sound_once() -> void:
	if has_played_alert:
		return
	has_played_alert = true
	play_sound(ALERT_SFX)

func play_attack_sound(index: int) -> void:
	var start_offset := 0.0
	if index < attack_sound_start_offsets.size():
		start_offset = attack_sound_start_offsets[index]
	play_sound(ATK_SFX, start_offset)

func update_animation() -> void:
	if is_dead or is_hurt or is_attacking:
		return
	if absf(velocity.x) > 5.0:
		anim.play(RUN_ANIMATION)
	else:
		anim.play(IDLE_ANIMATION)

func take_damage(amount: int) -> void:
	if is_dead:
		return

	current_health = max(0, current_health - amount)
	health_bar.set_health(current_health, max_health)
	spawn_damage_indicator(amount, global_position + Vector2(0.0, -34.0), Color(1.0, 0.86, 0.32))
	cancel_attack()

	if current_health <= 0:
		die()
		return

	is_hurt = true
	hurt_stun_timer = HURT_STUN_TIME
	anim.play(HIT_ANIMATION)

func die() -> void:
	is_dead = true
	is_hurt = false
	velocity.x = 0.0
	cancel_attack()
	GameState.add_score(100)
	play_detached_sound(DEATH_SFX)
	anim.play(DEATH_ANIMATION)

func cancel_attack() -> void:
	is_attacking = false
	animation_player.stop()
	disable_attack_hitbox()

func enable_attack_hitbox() -> void:
	if not is_attacking or is_dead or is_hurt or hurt_stun_timer > 0.0:
		return
	super.enable_attack_hitbox()

func _on_animation_finished() -> void:
	if anim.animation in ATTACK_ANIMATIONS:
		cancel_attack()
	elif anim.animation == HIT_ANIMATION:
		if hurt_stun_timer == 0.0:
			is_hurt = false
	elif anim.animation == DEATH_ANIMATION:
		queue_free()
