extends Control
## Intro splash after a character is picked: shows the chosen hero's idle
## animation, a flavor line and the jingle, then fades out into the main scene.

const MAIN_SCENE := "res://Scenes/Main/main.tscn"

const CHARACTERS := {
	"knight": {
		"sheet": preload("res://Assets/PlayerAssets/Medieval King Pack 2/Sprites/Idle.png"),
		"line": "You Have Chosen the Almighty Medieval Knight, Lion of the West!",
		"scale": 4.0,
		"offset": Vector2(0.0, -22.0),
	},
	"huntress": {
		"sheet": preload("res://Assets/PlayerAssets/Huntress/Idle.png"),
		"line": "You Have Chosen the Huntress of Saxony, Ranger of the Northern Forest.",
		"scale": 4.6,
		"offset": Vector2.ZERO,
	},
}

const FRAMES := 8
const FPS := 8.0

var _time := 0.0
var _done := false

func _ready() -> void:
	var id: String = GameState.selected_character
	if not CHARACTERS.has(id):
		id = "knight"
	var character: Dictionary = CHARACTERS[id]

	$Sprite.texture = character.sheet
	$Sprite.hframes = FRAMES
	$Sprite.scale = Vector2.ONE * character.scale
	$Sprite.offset = character.offset
	$Title.text = character.line
	$Audio.play()

	# fade IN -> hold for the ~6.5s song -> fade OUT -> load the game
	var t := create_tween()
	t.tween_property($Fade, "modulate:a", 0.0, 0.6)
	t.tween_interval(5.6)
	t.tween_property($Fade, "modulate:a", 1.0, 0.8)
	t.tween_callback(_go)

func _process(delta: float) -> void:
	_time += delta * FPS
	$Sprite.frame = int(_time) % FRAMES

func _go() -> void:
	if _done:
		return
	_done = true
	get_tree().change_scene_to_file(MAIN_SCENE)
