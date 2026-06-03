from leveltodo.domain.tasks.rules import Reward, compute_reward


def test_override_overrides_everything():
    assert compute_reward(elapsed_seconds=9999, override=20) == Reward(xp=20, points=20)


def test_time_based_one_per_minute():
    assert compute_reward(elapsed_seconds=120, override=None) == Reward(xp=2, points=2)


def test_short_timer_still_gives_at_least_one():
    # 20 saniye yuvarlanınca 0 eder ama en az 1 verilir.
    assert compute_reward(elapsed_seconds=20, override=None).xp == 1


def test_untimed_completion_gives_flat_default():
    assert compute_reward(elapsed_seconds=0, override=None) == Reward(xp=5, points=5)
