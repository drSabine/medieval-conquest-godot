extends CombatActor
## Base class for playable heroes (Knight, Huntress). Handles walking, jumping,
## the attack combo and getting hurt. Each hero's own script fills in its stats
## and animation names in configure_character(); the logic here is shared.

signal health_changed(current_health: int, max_health: int)

@export_group("Movement")
@export var speed := 260.0
@export var jump_velocity := -380.0

@export_group("Combat")
@export var max_health := 120

@onready var camera: Camera2D = $Camera2D

const HIT_REACTION_TIME := 0.3

# --- Per-hero settings: filled in by configure_character() in the child script ---
var idle_animation := ""
var run_animation := ""
var jump_animation := ""
var fall_animation := ""
var hit_animation := ""
var combo_reset_time := 1.5
var attack_speed_scale := 0.85    # how fast attack animations play (1.0 = normal)
var attack_animations: Array[String] = []
var attack_hitbox_animations: Array[String] = []
var attack_sounds: Array[AudioStream] = []

# --- Live state ---
var current_health := 0
var is_attack_buffered := false   # player pressed attack mid-swing -> queue next combo hit
var combo_reset_timer := 0.0
var hit_reaction_timer := 0.0

# Each hero script overrides this to set its own stats, animations and sounds.
func configure_character() -> void:
	pass

func _ready() -> void:
	configure_character()
	target_group = "enemies"
	setup_sfx_player()
	current_health = max_health
	disable_attack_hitbox()

	# Walk up/down the sloped stair ramps smoothly (ramps are ~27 deg).
	floor_max_angle = deg_to_rad(50.0)
	floor_snap_length = 16.0
	floor_stop_on_slope = true

	add_to_group("player")
	camera.enabled = true
	camera.make_current()

	anim.animation_finished.connect(_on_animation_finished)
	health_changed.emit(current_health, max_health)

func _physics_process(delta: float) -> void:
	apply_gravity(delta)
	update_timers(delta)
	handle_input()

	move_and_slide()
	update_animation()

func update_timers(delta: float) -> void:
	if hit_reaction_timer > 0.0:
		hit_reaction_timer = max(0.0, hit_reaction_timer - delta)

	if not is_attacking and attack_index != -1:
		combo_reset_timer -= delta
		if combo_reset_timer <= 0.0:
			attack_index = -1

func handle_input() -> void:
	var direction := Input.get_axis("move_left", "move_right")  # -1 left, 0 none, +1 right
	var wants_attack := Input.is_action_just_pressed("attack")

	# While mid-swing the hero stands still; pressing attack queues the next combo hit.
	if is_attacking:
		velocity.x = 0.0
		if wants_attack:
			start_attack()
		return

	# Move in the held direction, or slow to a stop when nothing is pressed.
	if direction != 0.0:
		velocity.x = direction * speed
		update_facing(direction)
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed)

	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = jump_velocity

	if wants_attack:
		start_attack()

func start_attack() -> void:
	if not is_on_floor():
		return
	if is_attacking:
		is_attack_buffered = true
		return

	play_next_attack()

func play_next_attack() -> void:
	is_attacking = true
	is_attack_buffered = false
	combo_reset_timer = 0.0
	hit_targets.clear()
	disable_attack_hitbox()

	# step to the next attack in the combo, looping back to the first
	attack_index = (attack_index + 1) % attack_animations.size()
	play_attack_sound(attack_index)

	# the sprite animation and its matching hitbox track play at the same speed
	anim.speed_scale = attack_speed_scale
	animation_player.speed_scale = attack_speed_scale
	anim.play(attack_animations[attack_index])
	animation_player.play(attack_hitbox_animations[attack_index])

func play_attack_sound(index: int) -> void:
	if index >= attack_sounds.size():
		return
	play_sound(attack_sounds[index])

func update_animation() -> void:
	if is_attacking or hit_reaction_timer > 0.0:
		return

	anim.speed_scale = 1.0
	if not is_on_floor():
		anim.play(jump_animation if velocity.y < 0.0 else fall_animation)
	elif absf(velocity.x) > 5.0:
		anim.play(run_animation)
	else:
		anim.play(idle_animation)

func take_damage(amount: int) -> void:
	current_health = max(0, current_health - amount)
	health_changed.emit(current_health, max_health)
	spawn_damage_indicator(amount, global_position + Vector2(0.0, -38.0), Color(1.0, 0.2, 0.16))
	if current_health <= 0:
		return
	if is_attacking:
		return
	hit_reaction_timer = HIT_REACTION_TIME
	anim.play(hit_animation)
	anim.set_frame_and_progress(0, 0.0)

# Called when any animation finishes. We only care about attack animations here.
func _on_animation_finished() -> void:
	if anim.animation not in attack_animations:
		return

	# A buffered press continues the combo, but only while on the ground.
	var on_floor := is_on_floor()
	if is_attack_buffered and on_floor:
		play_next_attack()
		return

	is_attack_buffered = false
	is_attacking = false
	if on_floor:
		# keep the combo open briefly so the next swing chains
		combo_reset_timer = combo_reset_time
	else:
		# air attacks don't chain
		combo_reset_timer = 0.0
		attack_index = -1
	anim.speed_scale = 1.0
	animation_player.speed_scale = 1.0
	disable_attack_hitbox()
