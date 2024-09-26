from rpgram.data.battle import BattleRepository
from rpgram.domain.errors import NoBattle
from rpgram.domain.models.battle import World, ComboNode, RunningBattle
from rpgram.domain.utypes import PlayerId


class ActionInteractor:
    def __init__(self, combo_root: ComboNode, world: World, battle_repo: BattleRepository):
        self.world = world
        self.battle_repo = battle_repo
        self.combo_root = combo_root

    def __call__(self, key: str, player_id: PlayerId) -> None:
        battle = self.battle_repo.get_battle(player_id)
        if not isinstance(battle, RunningBattle):
            raise NoBattle
        by_hero = battle.hero.player_id == player_id
        hero = battle.hero if by_hero else battle.opponent
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
            battle.hero.plays.previous = previous_combo
        else:
            battle.opponent.plays.previous = previous_combo
