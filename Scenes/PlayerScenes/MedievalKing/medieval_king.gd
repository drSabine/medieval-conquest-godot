extends "res://Scenes/PlayerScenes/player_character.gd"

func configure_character() -> void:
	speed = 260.0
	jump_velocity = -380.0
	combo_reset_time = 0.4

	# Animation names from medieval_king.tscn SpriteFrames.
	idle_animation = "MedievalKingIdle"
	run_animation = "MedievalKingRun"
	jump_animation = "MedievalKingJump"
	fall_animation = "MedievalKingFall"
	hit_animation = "MedievalKingHit"

	# Combo order and matching AnimationPlayer hitbox tracks.
	attack_animations = [
		"MedievalKingAtk1",
		"MedievalKingAtk2",
		"MedievalKingAtk3",
	]
	attack_hitbox_animations = [
		"Atk1Hitbox",
		"Atk2Hitbox",
		"Atk3Hitbox",
	]

	# Per-attack collision tuning.
	attack_hitbox_sizes = [
		Vector2(30.0, 28.0),
		Vector2(34.0, 30.0),
		Vector2(38.0, 32.0),
	]
	attack_hitbox_positions = [
		Vector2(16.0, 18.0),
		Vector2(18.0, 17.0),
		Vector2(20.0, 18.0),
	]
