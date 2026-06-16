extends "res://Scenes/PlayerScenes/player_character.gd"
## The Huntress hero. This script only holds her stats, animation names and attack
## sounds; all the actual movement/combat logic lives in player_character.gd.

const ATK1_SFX := preload("res://Assets/PlayerAssets/Huntress/Effects/atk1.mp3")
const ATK2_SFX := preload("res://Assets/PlayerAssets/Huntress/Effects/atk2.mp3")

func configure_character() -> void:
	speed = 300.0
	jump_velocity = -400.0
	max_health = 120
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

	attack_damages = [
		12,
		17,
	]

	attack_sounds = [
		ATK1_SFX,
		ATK2_SFX,
	]
