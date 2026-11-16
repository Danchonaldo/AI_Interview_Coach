from metrics import agreement, all_criteria_within_1, stability


def test_agreement():
    a = agreement([(3, 3), (4, 2), (5, 4), (1, 2)])
    assert a["n"] == 4 and a["within_1"] == 0.75 and a["exact"] == 0.25
    assert a["mae"] == 1.0 and a["bias"] == 0.5
    assert agreement([])["within_1"] is None


def test_stability():
    s = stability([[3, 3, 3], [2, 4, 3], [5]])
    assert s["n"] == 2 and s["identical"] == 0.5 and s["max_spread_le_1"] == 0.5 and s["mean_spread"] == 1.0


def test_all_criteria_within_1():
    h = {"relevance": 3, "structure": 3, "specificity": 3}
    items = [{"human": h, "ai": {"relevance": 4, "structure": 2, "specificity": 3}},
             {"human": h, "ai": {"relevance": 5, "structure": 3, "specificity": 3}}]
    assert all_criteria_within_1(items) == 0.5
