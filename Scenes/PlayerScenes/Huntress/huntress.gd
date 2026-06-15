extends "res://Scenes/PlayerScenes/player_character.gd"

func configure_character() -> void:
	speed = 300.0
	jump_velocity = -400.0
	combo_reset_time = 1.5

	# Animation names from huntress.tscn SpriteFrames.
	idle_animation = "HuntressIdle"
	run_animation = "HuntressRun"
	jump_animation = "HuntressJump"
	fall_animation = "HuntressFall"
	hit_animation = "HuntressHit"

	# Combo order and matching AnimationPlayer hitbox tracks.
	attack_animations = [
		"HuntressAtk1",
		"HuntressAtk2",
	]
	attack_hitbox_animations = [
		"Atk1Hitbox",
		"Atk2Hitbox",
	]

	# Per-attack collision tuning.
	attack_hitbox_sizes = [
		Vector2(30.0, 24.0),
		Vector2(34.0, 26.0),
	]
	attack_hitbox_positions = [
		Vector2(16.0, 4.0),
		Vector2(18.0, 4.0),
	]
