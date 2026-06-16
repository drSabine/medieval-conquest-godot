extends Label

const FLOAT_DISTANCE := 32.0
const FLOAT_TIME := 0.7
const FONT := preload("res://Assets/Fonts/Minecraft.ttf")

func show_damage(amount: int, start_position: Vector2, color: Color) -> void:
	text = "-%d" % amount
	modulate = color
	z_index = 100
	add_theme_font_override("font", FONT)
	add_theme_font_size_override("font_size", 24)
	add_theme_color_override("font_outline_color", Color(0, 0, 0))
	add_theme_constant_override("outline_size", 6)

	# centre the label on the hit point and pop-scale in
	pivot_offset = Vector2(16, 14)
	global_position = start_position - pivot_offset
	scale = Vector2(0.4, 0.4)

	var x_jitter := randf_range(-12.0, 12.0)
	var end_position := global_position + Vector2(x_jitter, -FLOAT_DISTANCE)

	# all three properties animate at once: float up, pop to full size, then fade out
	var tween := create_tween()
	tween.set_parallel(true)
	tween.tween_property(self, "global_position", end_position, FLOAT_TIME).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "scale", Vector2.ONE, 0.16).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "modulate:a", 0.0, FLOAT_TIME * 0.6).set_delay(FLOAT_TIME * 0.4)
	tween.chain().tween_callback(queue_free)
