from dishka import Provider, provide, Scope

from rpgram.app.battle import BattleRunner
from rpgram.app.services.action import ActionInteractor
from rpgram.domain.algos.trie import COMBO_ROOT
from rpgram.domain.models.battle import Battle, World, HeroState, Move, Action


class InteractorsProvider(Provider):
    scope = Scope.REQUEST

    battle_runner = provide(BattleRunner)

    @provide
    def action_interactor(self, battle: Battle, world: World) -> ActionInteractor:
        return ActionInteractor(COMBO_ROOT, world, battle)


class BattleProvider(Provider):
    scope = Scope.APP

    @provide
    def battle(self) -> Battle:
        return Battle(HeroState(50, []), HeroState(30, []))

    @provide
    def world(self) -> World:
        return World(Move(Action(0, None), Action(0, None)))
