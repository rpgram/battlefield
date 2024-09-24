from rpgram.domain.models.battle import Action, Effect, EffectTick, ComboNode

COMBO_ROOT = ComboNode(
    "",
    [
        ComboNode(
            "a", [ComboNode("a", [], prefix="a", action=Action("hit", -3, None))]
        ),
        ComboNode(
            "b",
            [
                ComboNode(
                    "c",
                    [ComboNode("b", [], prefix="bc", action=Action("sweep", -5, None))],
                    prefix="b",
                ),
                ComboNode(
                    "a",
                    [],
                    prefix="b",
                    action=Action(
                        "cripple",
                        4,
                        Effect(
                            "dream",
                            [
                                EffectTick(-3),
                                EffectTick(-3),
                                EffectTick(-3),
                            ],
                        ),
                    ),
                ),
            ],
        ),
    ],
)
