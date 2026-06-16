extends Node
## Global game state (an autoload singleton, see Project Settings > Autoload).
## Any scene can read GameState.selected_character or GameState.score. It survives
## scene changes, so it carries the chosen hero from the menu into the main level.

signal score_changed(score: int)

var selected_character := "knight"   # "knight" or "huntress", set on the start menu
var score := 0

func choose_character(character_id: String) -> void:
	selected_character = character_id

func reset_score() -> void:
	score = 0
	score_changed.emit(score)

func add_score(points: int) -> void:
	score += points
	score_changed.emit(score)
