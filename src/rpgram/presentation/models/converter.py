from adaptix.conversion import get_converter, link
from adaptix import P

from rpgram.domain.models.battle import (
    Battle,
    HeroState,
    ComboNode,
    PlayerState,
    Hint,
)
from rpgram.presentation.models.battle import WaitingBattle
from rpgram.presentation.models.pure_reality import (
    BattleDTO,
    PlayerDTO,
    BattleFieldDTO,
)
from rpgram.presentation.models import battle


def combo_node_coercer(previous: ComboNode | None) -> str | None:
    return previous.combo if previous else None


def effect_description(hero_state: HeroState) -> list[str]:
    return [f"{e.effect.name}({e.tick + 1}" for e in hero_state.effect_states]


def move(key: str) -> battle.Move:
    return battle.Move({"a": 1, "b": 2, "c": 3, "d": 4}[key])


def next_move_getter(hints: list[Hint]) -> list[battle.Suggestion]:
    return [battle.Suggestion(move(h.key), h.distance, h.action_name) for h in hints]


def get_players_hints(player: PlayerState) -> list[battle.Suggestion]:
    if player.plays.previous is None:
        return []
    return next_move_getter(player.plays.previous.hints)


def get_health(hero_state: HeroState) -> int:
    return hero_state.health


def convert_hero_state_to_dto(
    hero_state: HeroState,
) -> PlayerDTO:
    return PlayerDTO(
        username="TESTER",
        health_points=get_health(hero_state),
        effects=effect_description(hero_state),
    )


def convert_battle_to_field_dto(
    battle_state: Battle,
) -> BattleFieldDTO:
    return BattleFieldDTO(
        battle_id=battle_state.battle_id,
        player=convert_hero_state_to_dto(battle_state.hero.unit_state),
        opponent=(
            convert_hero_state_to_dto(battle_state.opponent.unit_state)
            if battle_state.opponent
            else None
        ),
        next_move=get_players_hints(battle_state.hero),
        complete_actions=[],
        moves=[battle.Move(3), battle.Move(2), battle.Move(1)],
    )


# def convert_hero_state_to_dto(hero_state: PlayerState) -> HeroStateDTO:
#     return HeroStateDTO(
#         health=player_state.unit_state.health,
#         effect_states=player_state.unit_state.effect_states,
#         plays=PlayerStateDTO(
#             hints=player_state.plays.previous.hints,
#             previous=player_state.plays.previous,
#         ),
#     )
#

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


def waiting_battles_converter(battle_state: Battle) -> WaitingBattle:
    return WaitingBattle(battle_state.hero.player_id, battle_state.battle_id)
