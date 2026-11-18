from io import BytesIO
import pandas as pd
import pytest
from src.safety import read_anonymous_record
from src.ml import stage_features, load_data
from src.case_store import DemoCaseStore, AuthorizationError
from src.intelligence import recommendations

@pytest.mark.parametrize('value', ['inf', '-inf', 'hello', '=1+1'])
def test_unsafe_numeric_csv(value):
    with pytest.raises(ValueError):
        read_anonymous_record(BytesIO(f'Course\n{value}\n'.encode()), ['Course'])

def test_batch_bounds_and_extra_columns():
    assert len(read_anonymous_record(BytesIO(b'Course\n1\n2\n'), ['Course'], 2)) == 2
    with pytest.raises(ValueError):
        read_anonymous_record(BytesIO(b'Course,secret\n1,2\n'), ['Course'], 2)

def test_unknown_outcome_feature_rejected():
    with pytest.raises(ValueError):
        stage_features(pd.DataFrame({'graduation_date':[2026]}), 'Admission')

def test_all_stage_features_exclude_future():
    df = load_data()
    assert not any('sem' in c for c in stage_features(df, 'Admission'))
    assert not any('2nd sem' in c for c in stage_features(df, 'After semester 1'))

def test_contextual_recommendations():
    r = recommendations(pd.DataFrame({'Debtor':[1], 'Curricular units 1st sem (enrolled)':[6], 'Curricular units 1st sem (approved)':[1]}))
    assert len(r) == 2
    assert '1/6' in r.iloc[0].evidence

def test_followup_access_and_deletion(tmp_path):
    store = DemoCaseStore(tmp_path/'demo.db')
    store.create_user('admin', 'long-password123', 'admin')
    for name in ('advisor1', 'advisor2'):
        store.create_user(name, 'long-password123', 'advisor', 'admin', 'long-password123')
    store.save_case('advisor1', 'DEMO-1', 'advisor1', 'Needs assessment', [])
    with pytest.raises(AuthorizationError):
        store.record_followup('advisor2', 'DEMO-1', '2026-12-01', 'Pending')
    store.record_followup('advisor1', 'DEMO-1', '2026-12-01', 'Contacted')
    assert store.list_followups('advisor2') == []
    assert len(store.list_followups('admin')) == 1
    store.delete_case('advisor1', 'DEMO-1')
    assert store.list_followups('admin') == []

def test_release_training_artifact_and_batch():
    from pathlib import Path
    if not Path('artifacts/manifest.json').exists():
        pytest.skip('Run documented training first for release integration')
    import numpy as np
    from src.registry import verified_load
    from src.intelligence import screen_cohort
    b, m = verified_load('artifacts')
    X = stage_features(load_data().head(8), b['stage'])
    p = b['model'].predict_proba(X)
    assert np.allclose(p.sum(axis=1), 1)
    r = screen_cohort(b, m, X)
    assert len(r) == 8
    assert r.dropout_probability.between(0, 1).all()
    assert len(m['model_comparison']) in (3, 7, 8)
    if m.get('hyperparameter_search'):
        assert m['hyperparameter_search']['trials']
