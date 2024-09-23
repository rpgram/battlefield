from rpgram.domain.models.battle import Action, Effect, EffectTick, ComboNode

COMBO_ROOT = ComboNode(
    "",
    [
        ComboNode("a", [ComboNode("a", [], prefix="a", action=Action(-3, None))]),
        ComboNode(
            "b",
            [
                ComboNode("c", [ComboNode("b", [], prefix="bc")], prefix="b"),
                ComboNode(
                    "a",
                    [],
                    prefix="b",
                    action=Action(
                        4,
                        Effect(
                            [
                                EffectTick(-3),
                                EffectTick(-3),
                                EffectTick(-3),
                            ]
                        ),
                    ),
                ),
            ],
        ),
    ],
)
