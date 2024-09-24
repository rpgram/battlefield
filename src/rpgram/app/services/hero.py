from rpgram.domain.models.battle import Battle, HeroState, PlayInfo, PlayerState


class BattleService:

    def prepare_state(self) -> Battle:
        return Battle(
            PlayerState(HeroState(50, []), PlayInfo()),
            PlayerState(
                HeroState(30, []),
                PlayInfo(),
            ),
        )
