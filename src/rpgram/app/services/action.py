import itertools

from rpgram.domain.models.battle import World, Battle, ComboNode


class ActionInteractor:
    def __init__(self, combo_root: ComboNode, world: World, battle: Battle):
        self.world = world
        self.battle = battle
        self.combo_root = combo_root

    def __call__(self, key: str, by_hero: bool) -> list[str]:
        hero = self.battle.hero if by_hero else self.battle.opponent
        combo_by = hero.previous if hero.previous else [self.combo_root]
        combo = list(
            itertools.chain(
                *[hpc.propagate_combo(key, self.combo_root) for hpc in combo_by]
            )
        )
        previous_combo = None
        if len(combo) == 1:
            node = combo[0]
            if node.is_leaf:
                if by_hero:
                    self.world.move.hero.opponent_effect = node.effect.opponent_effect
                    self.world.move.hero.opponent_health_delta = (
                        node.effect.opponent_health_delta
                    )
                    self.battle.hero.previous = None
                else:
                    self.world.move.opponent.opponent_effect = (
                        node.effect.opponent_effect
                    )
                    self.world.move.opponent.opponent_health_delta = (
                        node.effect.opponent_health_delta
                    )
                    self.battle.opponent.previous = None
            else:
                previous_combo = combo
        else:
            previous_combo = combo
        if by_hero:
            self.battle.hero.previous = previous_combo
        return [c.value for c in combo]
