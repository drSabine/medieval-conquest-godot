extends CanvasLayer
## Result overlay. Shown when the player wins or loses; the tree is paused by
## main.gd so everything freezes. This node keeps processing (process_mode =
## ALWAYS) so any key returns to the menu.

const MENU_SCENE := "res://Scenes/Start/start_menu.tscn"

func show_result(title: String, title_color: Color) -> void:
	$WinTitle.text = title
	$WinTitle.add_theme_color_override("font_color", title_color)
	visible = true

func show_win() -> void:
	show_result("YOU WIN!", Color(0.95, 0.82, 0.36))

func show_lose() -> void:
	show_result("YOU LOSE!", Color(0.86, 0.18, 0.15))

func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_pressed() and (event is InputEventKey or event is InputEventMouseButton):
		get_tree().paused = false
		get_tree().change_scene_to_file(MENU_SCENE)
