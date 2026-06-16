extends Control
## Title screen. The player clicks a hero card; we remember the choice in
## GameState and move on to the intro splash.

const INTRO_SCENE := "res://Scenes/Start/character_intro.tscn"

func _ready() -> void:
	$Cards/KnightCard/KnightButton.grab_focus()

func _on_knight_button_pressed() -> void:
	start_game("knight")

func _on_huntress_button_pressed() -> void:
	start_game("huntress")

func start_game(character_id: String) -> void:
	GameState.choose_character(character_id)
	get_tree().change_scene_to_file(INTRO_SCENE)
