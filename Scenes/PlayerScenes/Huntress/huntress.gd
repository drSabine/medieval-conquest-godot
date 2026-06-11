extends CharacterBody2D

@export_group("Movement")
@export var speed := 300.0
@export var jump_velocity := -400.0

@export_group("Combat")
@export var attack_damage := 10

@onready var anim: AnimatedSprite2D = $AnimatedSprite2D
@onready var attack_pivot: Node2D = $AttackPivot
@onready var attack_hitbox: Area2D = $AttackPivot/AttackHitbox
@onready var attack_shape: CollisionShape2D = $AttackPivot/AttackHitbox/CollisionShape2D
@onready var animation_player: AnimationPlayer = $AnimationPlayer

const IDLE_ANIMATION := "HuntressIdle"
const RUN_ANIMATION := "HuntressRun"
const JUMP_ANIMATION := "HuntressJump"
const FALL_ANIMATION := "HuntressFall"

const ATTACK_ANIMATIONS := [
	"HuntressAtk1",
	"HuntressAtk2",
]

const ATTACK_HITBOX_ANIMATIONS := [
	"Atk1Hitbox",
	"Atk2Hitbox",
]

var attack_index := -1
var is_attacking := false
var hit_targets: Array[Node] = []

func _ready() -> void:
	attack_hitbox.monitoring = false
	anim.animation_finished.connect(_on_animation_finished)

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity += get_gravity() * delta

	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = jump_velocity

	var direction := Input.get_axis("move_left", "move_right")
	if direction != 0.0:
		velocity.x = direction * speed
		update_facing(direction)
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed)

	if Input.is_action_just_pressed("attack"):
		start_attack()

	move_and_slide()
	update_animation()

func start_attack() -> void:
	if is_attacking:
		return

	is_attacking = true
	hit_targets.clear()
	attack_index = (attack_index + 1) % ATTACK_ANIMATIONS.size()
	configure_attack_hitbox(attack_index)

	anim.play(ATTACK_ANIMATIONS[attack_index])
	animation_player.play(ATTACK_HITBOX_ANIMATIONS[attack_index])

func update_animation() -> void:
	if is_attacking:
		return

	if not is_on_floor():
		anim.play(JUMP_ANIMATION if velocity.y < 0.0 else FALL_ANIMATION)
	elif absf(velocity.x) > 5.0:
		anim.play(RUN_ANIMATION)
	else:
		anim.play(IDLE_ANIMATION)

func update_facing(direction: float) -> void:
	if direction > 0.0:
		anim.flip_h = false
		attack_pivot.scale.x = 1.0
	elif direction < 0.0:
		anim.flip_h = true
		attack_pivot.scale.x = -1.0

func enable_attack_hitbox() -> void:
	attack_hitbox.monitoring = true
	for body in attack_hitbox.get_overlapping_bodies():
		_try_hit_body(body)

func disable_attack_hitbox() -> void:
	attack_hitbox.monitoring = false

func configure_attack_hitbox(index: int) -> void:
	var rect := attack_shape.shape as RectangleShape2D

	match index:
		0:
			rect.size = Vector2(78.0, 40.0)
			attack_shape.position = Vector2(44.0, 18.0)
		1:
			rect.size = Vector2(92.0, 44.0)
			attack_shape.position = Vector2(54.0, 12.0)

func _on_animation_finished() -> void:
	if anim.animation in ATTACK_ANIMATIONS:
		is_attacking = false
		disable_attack_hitbox()

func _on_attack_hitbox_body_entered(body: Node2D) -> void:
	_try_hit_body(body)

func _try_hit_body(body: Node) -> void:
	if not attack_hitbox.monitoring:
		return
	if not body.is_in_group("enemies"):
		return
	if body in hit_targets:
		return

	hit_targets.append(body)

	if body.has_method("take_damage"):
		body.take_damage(attack_damage)
