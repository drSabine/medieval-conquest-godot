extends Node2D
## Runs the main level: spawns the chosen hero, tracks the HUD (score + health),
## and decides win/lose. You win by reaching the finish zone with all enemies
## dead; you lose if the hero's health hits zero.

const KING_SCENE := preload("res://Scenes/PlayerScenes/MedievalKing/medieval_king.tscn")
const HUNTRESS_SCENE := preload("res://Scenes/PlayerScenes/Huntress/huntress.tscn")

@onready var actors: Node2D = $Actors
@onready var player_spawn: Marker2D = $Actors/PlayerSpawn
@onready var score_label: Label = $HUD/ScoreLabel
@onready var health_label: Label = $HUD/HpPanel/HealthLabel
@onready var health_bar: ProgressBar = $HUD/HpPanel/HealthBar
@onready var finish_zone: Area2D = $FinishZone
@onready var win_overlay = $WinOverlay

var active_player          # the hero we spawned (Knight or Huntress)
var player_in_finish := false   # is the hero currently standing in the finish zone?
var game_over := false

func _ready() -> void:
	GameState.reset_score()
	GameState.score_changed.connect(_on_score_changed)
	spawn_selected_player()
	_on_score_changed(GameState.score)

	finish_zone.body_entered.connect(_on_finish_entered)
	finish_zone.body_exited.connect(_on_finish_exited)

func _process(_delta: float) -> void:
	# You win once you're standing in the finish zone AND every enemy is dead.
	if game_over or not player_in_finish:
		return
	if get_tree().get_nodes_in_group("enemies").is_empty():
		_trigger_win()

func spawn_selected_player() -> void:
	var use_huntress := GameState.selected_character == "huntress"
	var scene := HUNTRESS_SCENE if use_huntress else KING_SCENE

	active_player = scene.instantiate()
	actors.add_child(active_player)
	active_player.global_position = player_spawn.global_position

	active_player.health_changed.connect(_on_player_health_changed)
	_on_player_health_changed(active_player.current_health, active_player.max_health)

func _on_score_changed(score: int) -> void:
	score_label.text = "SCORE  %d" % score

func _on_player_health_changed(current_health: int, max_health: int) -> void:
	health_bar.max_value = max_health
	health_bar.value = current_health
	health_label.text = "%d/%d" % [current_health, max_health]
	if current_health <= 0:
		_trigger_lose()

func _on_finish_entered(body: Node) -> void:
	if body.is_in_group("player"):
		player_in_finish = true

func _on_finish_exited(body: Node) -> void:
	if body.is_in_group("player"):
		player_in_finish = false

func _trigger_win() -> void:
	game_over = true
	win_overlay.show_win()
	get_tree().paused = true

func _trigger_lose() -> void:
	if game_over:
		return
	game_over = true
	win_overlay.show_lose()
	get_tree().paused = true
