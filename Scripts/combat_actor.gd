extends CharacterBody2D
class_name CombatActor
## Shared combat plumbing for every fighter (player + goblins). Holds the bits
## that were duplicated across player_character.gd and goblin.gd: SFX, the swing
## hitbox, hit resolution, damage numbers and facing. Subclasses add their own
## movement/AI/animation logic on top.

const SFX_BUS := &"SFX"
const FloatingDamage := preload("res://Scripts/floating_damage.gd")

@onready var anim: AnimatedSprite2D = $AnimatedSprite2D
@onready var body_collision: CollisionShape2D = $BodyCollision
@onready var attack_pivot: Node2D = $AttackPivot
@onready var attack_hitbox: Area2D = $AttackPivot/AttackHitbox
@onready var attack_area: CollisionShape2D = $AttackPivot/AttackHitbox/AttackArea
@onready var animation_player: AnimationPlayer = $AnimationPlayer

# group whose bodies this actor's attacks damage ("enemies" for players, etc.)
var target_group := ""
var attack_damages: Array[int] = []
var fallback_damage := 0

var attack_index := -1
var is_attacking := false
var is_attack_active := false
var hit_targets: Array[Node] = []
var sfx_player: AudioStreamPlayer2D

func setup_sfx_player() -> void:
	sfx_player = AudioStreamPlayer2D.new()
	sfx_player.name = "SfxPlayer"
	_route_to_sfx_bus(sfx_player)
	add_child(sfx_player)

func play_sound(stream: AudioStream, from_position: float = 0.0) -> void:
	if stream == null or sfx_player == null:
		return
	sfx_player.stream = stream
	sfx_player.play(from_position)

func play_detached_sound(stream: AudioStream, from_position: float = 0.0) -> void:
	if stream == null:
		return
	var player := AudioStreamPlayer2D.new()
	player.name = "DetachedSfx"
	player.stream = stream
	player.global_position = global_position
	_route_to_sfx_bus(player)
	get_tree().current_scene.add_child(player)
	player.finished.connect(player.queue_free)
	player.play(from_position)

# both sfx_player and the one-off players in play_detached_sound need this
func _route_to_sfx_bus(player: AudioStreamPlayer2D) -> void:
	if AudioServer.get_bus_index(SFX_BUS) != -1:
		player.bus = SFX_BUS

# every fighter falls the same way; subclasses just call this each physics frame
func apply_gravity(delta: float) -> void:
	if not is_on_floor():
		velocity += get_gravity() * delta

# --- attack hitbox (driven by the AnimationPlayer tracks calling these) ---
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
	if not is_attack_active or body in hit_targets:
		return
	if not body.is_in_group(target_group) or not body.has_node("BodyCollision"):
		return
	hit_targets.append(body)
	if body.has_method("take_damage"):
		body.take_damage(get_attack_damage())

func get_attack_damage() -> int:
	if attack_index >= 0 and attack_index < attack_damages.size():
		return attack_damages[attack_index]
	return fallback_damage

func _on_attack_hitbox_body_entered(body: Node2D) -> void:
	try_hit_body(body)

# --- shared presentation ---
func update_facing(direction: float) -> void:
	anim.flip_h = direction < 0.0
	attack_pivot.scale.x = -1.0 if direction < 0.0 else 1.0

func spawn_damage_indicator(amount: int, world_position: Vector2, color: Color) -> void:
	var label := FloatingDamage.new()
	get_tree().current_scene.add_child(label)
	label.show_damage(amount, world_position, color)
