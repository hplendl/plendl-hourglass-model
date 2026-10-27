import datetime as dt, math
from hourglass.model import Trend, run, paradigm_shift, ols

def test_identity_and_debt_step():
    t = Trend(D0=40.0, r0=3.0, R0=5.0, s0=0.2, gR=0.04, bs=0.0, dr=0.0, months=24)
    rows = run(t)
    assert math.isclose(rows[0]["I"], 1.2)                       # I = D x r
    assert math.isclose(rows[1]["D"], 40 + (1.2 + 0.2 * 5) / 12)  # D += (I + sR)/12
    assert math.isclose(rows[12]["R"], 5 * 1.04, rel_tol=1e-9)    # R compounds at g_R

def test_paradigm_shift_rising_rate_vs_flat():
    base = dict(D0=40.0, r0=3.0, R0=5.0, s0=0.2, gR=0.04, bs=0.0, months=480)
    assert paradigm_shift(run(Trend(dr=0.4, **base))) is not None
    assert paradigm_shift(run(Trend(dr=-0.1, **base))) is None

def test_ols():
    a, b, r2 = ols([0, 1, 2, 3], [1, 3, 5, 7])
    assert math.isclose(b, 2) and math.isclose(r2, 1)
