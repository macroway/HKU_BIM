import re


def plan_tools_from_message(message: str) -> list[str]:
    """Keyword planner. Returns [] when intent is unclear."""
    text = message.strip().lower()
    if not text:
        return []

    wants_collision = any(
        k in text
        for k in (
            "碰撞",
            "冲突",
            "collision",
            "clash",
            "相交",
            "干涉",
            "硬碰",
            "空间冲突",
            "几何冲突",
            "撞墙",
            "管线碰",
            "梁碰",
            "有没有撞",
            "有没有碰",
        )
    )
    wants_attrs = any(
        k in text
        for k in (
            "属性",
            "fire",
            "firerating",
            "完整性",
            "缺项",
            "缺失",
            "attribute",
            "防火等级",
            "防火属性",
            "消防属性",
            "名称齐全",
            "缺字段",
            "fire rating",
            "缺不缺",
            "齐全吗",
        )
    )
    wants_both = any(
        k in text
        for k in (
            "都查",
            "全部",
            "两者",
            "两个",
            "一起",
            "都检查",
            "全面检查",
            "交付前",
            "全量",
            "过一遍",
            "自查",
            "逐项检查",
            "完整检查",
            "全面自查",
        )
    )
    wants_generic_check = any(
        k in text
        for k in (
            "帮我查",
            "帮我检查",
            "检查一下",
            "查一下",
            "做检查",
            "跑检查",
            "检查模型",
            "检查这个模型",
            "跑一下检查",
        )
    )

    if wants_both or (wants_collision and wants_attrs) or (
        wants_generic_check and not wants_collision and not wants_attrs
    ):
        return ["run_collision_check", "run_attribute_check"]
    if wants_collision:
        return ["run_collision_check"]
    if wants_attrs:
        return ["run_attribute_check"]
    if any(
        k in text
        for k in (
            "信息",
            "概况",
            "多少",
            "构件",
            "model info",
            "统计",
            "数量",
            "模型情况",
            "有哪些构件",
            "几扇门",
            "几面墙",
        )
    ):
        return ["get_model_info"]
    return []


def has_actionable_intent(message: str) -> bool:
    """True only when message maps to a known check/info intent."""
    return bool(plan_tools_from_message(message))


def is_gibberish(message: str) -> bool:
    """Obvious non-requests: empty, pure digits/symbols, ultra-short noise."""
    text = message.strip()
    if not text:
        return True
    # 111 / ??? / ... — no letters or CJK
    if re.fullmatch(r"[\d\s\W_]+", text, flags=re.UNICODE):
        return True
    if len(text) <= 2 and not re.search(r"[\u4e00-\u9fffA-Za-z]", text):
        return True
    return False
