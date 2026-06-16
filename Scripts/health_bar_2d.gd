extends ColorRect
## Small floating health bar shown above an enemy. It builds itself in code:
## this node is the dark background, and a green/yellow/red "fill" child shrinks
## as health drops. Create one with .new(), add it as a child, then call
## set_health() whenever the enemy takes damage.

const BAR_W := 38.0

var fill: ColorRect
var current_value := 1
var max_value := 1

func _ready() -> void:
	name = "HpBarBg"
	color = Color(0.0, 0.0, 0.0, 0.7)
	size = Vector2(BAR_W + 2.0, 7.0)
	position = Vector2(-(BAR_W + 2.0) * 0.5, -42.0)
	z_index = 80

	fill = ColorRect.new()
	fill.name = "Fill"
	fill.position = Vector2(1.0, 1.0)
	fill.size = Vector2(BAR_W, 5.0)
	add_child(fill)
	_update_fill()

func set_health(current_health: int, max_health: int) -> void:
	current_value = current_health
	max_value = max(1, max_health)
	_update_fill()

func _update_fill() -> void:
	if fill == null:
		return
	var ratio := clampf(float(current_value) / float(max_value), 0.0, 1.0)
	fill.size.x = BAR_W * ratio
	if ratio < 0.35:
		fill.color = Color(0.85, 0.25, 0.2)
	elif ratio < 0.6:
		fill.color = Color(0.9, 0.72, 0.2)
	else:
		fill.color = Color(0.3, 0.82, 0.32)
