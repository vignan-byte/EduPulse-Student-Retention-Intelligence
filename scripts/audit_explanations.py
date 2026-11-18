"""Executed explanation integration audit against the release model."""
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from src.ml import load_data, stage_features
from src.registry import verified_load
from src.explain import explain_shap, explain_lime, global_shap
bundle, metrics = verified_load('artifacts')
df = load_data()
X = stage_features(df, bundle['stage'])
train, test = train_test_split(X, test_size=.2, random_state=42, stratify=df.Target)
record = test.iloc[[0]]
a = explain_shap(bundle['model'], train, record)
b = explain_lime(bundle['model'], train, record)
g = global_shap(bundle['model'], train, test, max_rows=3)
Path('evidence').mkdir(exist_ok=True)
a.to_csv('evidence/local_shap.csv', index=False)
b.to_csv('evidence/local_lime.csv', index=False)
g.to_csv('evidence/global_shap_sample.csv', index=False)
Path('evidence/explanations.json').write_text(json.dumps({'shap':a.attrs,'lime_terms':len(b),'global_sample_rows':3,'limitation':'LIME surrogate and SHAP may disagree; neither is causal.'},indent=2))
print('SHAP additivity, local LIME and sampled global SHAP executed')
