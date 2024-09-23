from adaptix.conversion import get_converter, link
from adaptix import P

from rpgram.domain.models.battle import Battle, HeroState, ComboNode
from rpgram.presentation.models.pure_reality import BattleDTO, HeroStateDTO


def combo_node_coercer(preious: list[ComboNode] | None) -> list[str] | None:
    if preious:
        return [cn.combo for cn in preious]
    return None


convert_hero_state_to_dto = get_converter(
    HeroState,
    HeroStateDTO,
    recipe=[
        link(
            P[HeroState].previous, P[HeroStateDTO].previous, coercer=combo_node_coercer
        )
    ],
)
convert_battle_to_dto = get_converter(
    Battle,
    BattleDTO,
    recipe=[
        link(P[Battle].hero, P[BattleDTO].hero, coercer=convert_hero_state_to_dto),
        link(
            P[Battle].opponent, P[BattleDTO].opponent, coercer=convert_hero_state_to_dto
        ),
    ],
)
