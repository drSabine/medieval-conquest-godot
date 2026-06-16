extends "res://Scenes/PlayerScenes/player_character.gd"
## The Knight hero. This script only holds his stats, animation names and attack
## sounds; all the actual movement/combat logic lives in player_character.gd.

const ATK1_SFX := preload("res://Assets/PlayerAssets/Medieval King Pack 2/Effects/atk1.mp3")
const ATK2_SFX := preload("res://Assets/PlayerAssets/Medieval King Pack 2/Effects/atk2.mp3")
const ATK3_SFX := preload("res://Assets/PlayerAssets/Medieval King Pack 2/Effects/atk3.mp3")

func configure_character() -> void:
	speed = 260.0
	jump_velocity = -380.0
	max_health = 120
	combo_reset_time = 0.4
	attack_speed_scale = 0.82   # swings a touch slower than the default

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

	attack_damages = [
		8,
		11,
		16,
	]

	attack_sounds = [
		ATK1_SFX,
		ATK2_SFX,
		ATK3_SFX,
	]
