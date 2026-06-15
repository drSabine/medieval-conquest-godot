extends CharacterBody2D

@export_group("Movement")
@export var speed := 260.0
@export var jump_velocity := -380.0

@export_group("Combat")
@export var attack_damage := 10
@export var max_health := 100

@onready var anim: AnimatedSprite2D = $AnimatedSprite2D
@onready var attack_pivot: Node2D = $AttackPivot
@onready var attack_hitbox: Area2D = $AttackPivot/AttackHitbox
@onready var attack_area: CollisionShape2D = $AttackPivot/AttackHitbox/AttackArea
@onready var animation_player: AnimationPlayer = $AnimationPlayer

const HIT_REACTION_TIME := 0.3

var idle_animation := ""
var run_animation := ""
var jump_animation := ""
var fall_animation := ""
var hit_animation := ""
var combo_reset_time := 1.5
var attack_animations: Array[String] = []
var attack_hitbox_animations: Array[String] = []
var attack_hitbox_sizes: Array[Vector2] = []
var attack_hitbox_positions: Array[Vector2] = []

var attack_index := -1
var current_health := 0
var is_attacking := false
var is_attack_active := false
var is_attack_buffered := false
var combo_reset_timer := 0.0
var hit_reaction_timer := 0.0
var hit_targets: Array[Node] = []

# Character-specific scripts fill in animation names, combo timing, and hitbox sizes.
func configure_character() -> void:
	pass

func _ready() -> void:
	configure_character()
	current_health = max_health
	disable_attack_hitbox()

	if not is_visible_in_tree():
		set_physics_process(false)
		return

	add_to_group("player")
	anim.animation_finished.connect(_on_animation_finished)

func _physics_process(delta: float) -> void:
	apply_gravity(delta)
	update_timers(delta)
	handle_input()

	move_and_slide()
	update_animation()

func apply_gravity(delta: float) -> void:
	if not is_on_floor():
		velocity += get_gravity() * delta

func update_timers(delta: float) -> void:
	if hit_reaction_timer > 0.0:
		hit_reaction_timer = max(0.0, hit_reaction_timer - delta)

	if not is_attacking and attack_index != -1:
		combo_reset_timer -= delta
		if combo_reset_timer <= 0.0:
			attack_index = -1

func handle_input() -> void:
	var direction := Input.get_axis("move_left", "move_right")

	if is_attacking:
		velocity.x = 0.0
		if Input.is_action_just_pressed("attack"):
			start_attack()
		return

	velocity.x = direction * speed if direction != 0.0 else move_toward(velocity.x, 0.0, speed)

	if direction != 0.0:
		update_facing(direction)

	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = jump_velocity

	if Input.is_action_just_pressed("attack"):
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

	attack_index = (attack_index + 1) % attack_animations.size()
	configure_attack_hitbox(attack_index)
	anim.play(attack_animations[attack_index])
	animation_player.play(attack_hitbox_animations[attack_index])

func update_animation() -> void:
	if is_attacking or hit_reaction_timer > 0.0:
		return

	if not is_on_floor():
		anim.play(jump_animation if velocity.y < 0.0 else fall_animation)
	elif absf(velocity.x) > 5.0:
		anim.play(run_animation)
	else:
		anim.play(idle_animation)

func update_facing(direction: float) -> void:
	anim.flip_h = direction < 0.0
	attack_pivot.scale.x = -1.0 if direction < 0.0 else 1.0

func configure_attack_hitbox(index: int) -> void:
	var rect := attack_area.shape as RectangleShape2D
	rect.size = attack_hitbox_sizes[index]
	attack_area.position = attack_hitbox_positions[index]

func enable_attack_hitbox() -> void:
	is_attack_active = true
	attack_area.disabled = false
	attack_hitbox.monitoring = true

	for body in attack_hitbox.get_overlapping_bodies():
		try_hit_body(body)

func disable_attack_hitbox() -> void:
	is_attack_active = false
	attack_hitbox.set_deferred("monitoring", false)
	attack_area.set_deferred("disabled", true)

func try_hit_body(body: Node) -> void:
	if not is_attack_active:
		return
	if body in hit_targets:
		return
	if not body.is_in_group("enemies"):
		return
	if not body.has_node("BodyCollision"):
		return

	hit_targets.append(body)

	if body.has_method("take_damage"):
		body.take_damage(attack_damage)

func take_damage(amount: int) -> void:
	current_health = max(0, current_health - amount)
	cancel_attack()
	hit_reaction_timer = HIT_REACTION_TIME
	anim.play(hit_animation)
	anim.set_frame_and_progress(0, 0.0)

func cancel_attack() -> void:
	is_attacking = false
	is_attack_buffered = false
	attack_index = -1
	combo_reset_timer = 0.0
	disable_attack_hitbox()

func _on_animation_finished() -> void:
	if anim.animation not in attack_animations:
		return
	if is_attack_buffered and is_on_floor():
		play_next_attack()
		return

	is_attack_buffered = false
	is_attacking = false
	combo_reset_timer = combo_reset_time if is_on_floor() else 0.0
	if not is_on_floor():
		attack_index = -1
	disable_attack_hitbox()

func _on_attack_hitbox_body_entered(body: Node2D) -> void:
	try_hit_body(body)
