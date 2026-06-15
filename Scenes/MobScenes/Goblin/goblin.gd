extends CharacterBody2D

@export_group("Movement")
@export var speed := 140.0
@export var detection_range := Vector2(520.0, 48.0)
@export var attack_range := Vector2(48.0, 28.0)

@export_group("Combat")
@export var attack_damage := 8
@export var max_health := 30

@onready var anim: AnimatedSprite2D = $AnimatedSprite2D
@onready var body_collision: CollisionShape2D = $BodyCollision
@onready var attack_pivot: Node2D = $AttackPivot
@onready var attack_hitbox: Area2D = $AttackPivot/AttackHitbox
@onready var attack_area: CollisionShape2D = $AttackPivot/AttackHitbox/AttackArea
@onready var animation_player: AnimationPlayer = $AnimationPlayer

const IDLE_ANIMATION := "GoblinIdle"
const RUN_ANIMATION := "GoblinRun"
const HIT_ANIMATION := "GoblinHit"
const DEATH_ANIMATION := "GoblinDeath"

const ATTACK_ANIMATIONS := [
	"GoblinAtk1",
	"GoblinAtk2",
]

const ATTACK_HITBOX_ANIMATIONS := [
	"Atk1Hitbox",
	"Atk2Hitbox",
]

var attack_index := -1
var current_health := 0
var is_attacking := false
var is_attack_active := false
var is_hurt := false
var is_dead := false
var hit_targets: Array[Node] = []
var target: Node2D

func _ready() -> void:
	add_to_group("enemies")
	current_health = max_health
	disable_attack_hitbox()
	anim.animation_finished.connect(_on_animation_finished)

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity += get_gravity() * delta

	target = find_player()

	if is_dead or is_hurt:
		velocity.x = move_toward(velocity.x, 0.0, speed)
	elif is_attacking:
		velocity.x = 0.0
	elif target != null:
		update_ai()
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed)

	move_and_slide()
	update_animation()

func update_ai() -> void:
	var delta_to_target := get_body_delta_to(target)

	if delta_to_target.x != 0.0:
		update_facing(signf(delta_to_target.x))

	if is_inside_rect(delta_to_target, attack_range):
		velocity.x = 0.0
		start_attack()
	elif is_inside_rect(delta_to_target, detection_range):
		velocity.x = signf(delta_to_target.x) * speed
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed)

func find_player() -> Node2D:
	var closest_player: Node2D = null
	var closest_distance := INF

	for node in get_tree().get_nodes_in_group("player"):
		var player := node as Node2D
		if player == null or not player.is_visible_in_tree() or not player.has_node("BodyCollision"):
			continue

		var distance := body_collision.global_position.distance_to(get_body_position(player))
		if distance < closest_distance:
			closest_distance = distance
			closest_player = player

	return closest_player

func get_body_delta_to(body: Node2D) -> Vector2:
	return get_body_position(body) - body_collision.global_position

func get_body_position(body: Node2D) -> Vector2:
	var shape := body.get_node("BodyCollision") as CollisionShape2D
	return shape.global_position

func is_inside_rect(delta: Vector2, rect_size: Vector2) -> bool:
	return absf(delta.x) <= rect_size.x and absf(delta.y) <= rect_size.y

func start_attack() -> void:
	if is_attacking or is_hurt or is_dead:
		return

	is_attacking = true
	hit_targets.clear()
	attack_index = (attack_index + 1) % ATTACK_ANIMATIONS.size()
	configure_attack_hitbox(attack_index)

	anim.play(ATTACK_ANIMATIONS[attack_index])
	animation_player.play(ATTACK_HITBOX_ANIMATIONS[attack_index])

func update_animation() -> void:
	if is_dead or is_hurt or is_attacking:
		return

	if absf(velocity.x) > 5.0:
		anim.play(RUN_ANIMATION)
	else:
		anim.play(IDLE_ANIMATION)

func update_facing(direction: float) -> void:
	anim.flip_h = direction < 0.0
	attack_pivot.scale.x = -1.0 if direction < 0.0 else 1.0

func configure_attack_hitbox(index: int) -> void:
	var rect := attack_area.shape as RectangleShape2D

	match index:
		0:
			rect.size = Vector2(30.0, 34.0)
			attack_area.position = Vector2(18.0, 12.0)
		1:
			rect.size = Vector2(34.0, 34.0)
			attack_area.position = Vector2(20.0, 12.0)

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
	if not body.is_in_group("player"):
		return
	if not body.has_node("BodyCollision"):
		return

	hit_targets.append(body)

	if body.has_method("take_damage"):
		body.take_damage(attack_damage)

func take_damage(amount: int) -> void:
	if is_dead:
		return

	current_health = max(0, current_health - amount)
	cancel_attack()

	if current_health <= 0:
		die()
		return

	is_hurt = true
	anim.play(HIT_ANIMATION)

func die() -> void:
	is_dead = true
	is_hurt = false
	velocity.x = 0.0
	cancel_attack()
	anim.play(DEATH_ANIMATION)

func cancel_attack() -> void:
	is_attacking = false
	disable_attack_hitbox()

func _on_animation_finished() -> void:
	if anim.animation in ATTACK_ANIMATIONS:
		cancel_attack()
	elif anim.animation == HIT_ANIMATION:
		is_hurt = false
	elif anim.animation == DEATH_ANIMATION:
		queue_free()

func _on_attack_hitbox_body_entered(body: Node2D) -> void:
	try_hit_body(body)
