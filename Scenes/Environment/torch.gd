extends Node2D

@export var animation_name := ""

@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D

func _ready() -> void:
	add_to_group("castle_light")

	if animation_name != "":
		animated_sprite.play(animation_name)
		return

	animated_sprite.play(animated_sprite.animation)
