def plan_tools_from_message(message: str) -> list[str]:
    """Keyword planner for offline mode. Returns [] when intent is unclear."""
    text = message.strip().lower()
    if not text:
        return []

    wants_collision = any(k in text for k in ("碰撞", "冲突", "collision", "clash", "相交"))
    wants_attrs = any(
        k in text
        for k in ("属性", "fire", "firerating", "完整性", "缺项", "缺失", "attribute")
    )
    wants_both = any(
        k in text
        for k in ("都查", "全部", "两者", "两个", "一起", "都检查", "全面检查", "交付前")
    )
    # 泛化「检查」且未指定类型时，视为两项都查（需有明确检查语义，避免纯数字）
    wants_generic_check = any(
        k in text for k in ("帮我查", "帮我检查", "检查一下", "查一下", "做检查", "跑检查")
    )

    if wants_both or (wants_collision and wants_attrs) or (
        wants_generic_check and not wants_collision and not wants_attrs
    ):
        return ["run_collision_check", "run_attribute_check"]
    if wants_collision:
        return ["run_collision_check"]
    if wants_attrs:
        return ["run_attribute_check"]
    if any(k in text for k in ("信息", "概况", "多少", "构件", "model info")):
        return ["get_model_info"]
    return []
