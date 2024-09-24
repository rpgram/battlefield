from rpgram.domain.models.battle import World, Battle, ComboNode


class ActionInteractor:
    def __init__(self, combo_root: ComboNode, world: World, battle: Battle):
        self.world = world
        self.battle = battle
        self.combo_root = combo_root

    def __call__(self, key: str, by_hero: bool) -> None:
        hero = self.battle.hero if by_hero else self.battle.opponent
        combo_by = hero.plays.previous if hero.plays.previous else self.combo_root
        combo = combo_by.propagate_combo(key, self.combo_root)
        previous_combo = None
        if combo.is_leaf and combo.action:
            if by_hero:
                self.world.move.hero.opponent_effect = combo.action.opponent_effect
                self.world.move.hero.opponent_health_delta = (
                    combo.action.opponent_health_delta
                )
            else:
                self.world.move.opponent.opponent_effect = combo.action.opponent_effect
                self.world.move.opponent.opponent_health_delta = (
                    combo.action.opponent_health_delta
                )
        else:
            previous_combo = combo
        if by_hero:
            self.battle.hero.plays.previous = previous_combo
        else:
            self.battle.opponent.plays.previous = previous_combo
