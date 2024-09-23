from rpgram.domain.models.battle import Battle, HeroState


class BattleService:

    def prepare_state(self):
        return Battle(HeroState(100, []), HeroState(100, []))
