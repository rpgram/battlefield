import random

from rpgram.presentation.models.battle import BattleEvent, Side, Action, Combo


def generate_events(from_id: int) -> list[BattleEvent]:
    events: list[BattleEvent] = []
    for i in range(random.randint(0, 7)):
        events.append(make_random_event(events[-1].eid if events else from_id))
    return events


def make_random_event(from_id: int) -> BattleEvent:
    side = random.choice([Side.LEFT, Side.RIGHT])
    action = random.choice(
        [a.value for a in [Action.CROSS, Action.CIRCLE, Action.TRIANGLE, Action.SQUARE, Combo.HIT]]
    )
    return BattleEvent(
        eid=from_id if isinstance(action, Combo) else from_id + 1,
        action=action,
        side=side,
    )
