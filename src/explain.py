"""Optional local SHAP and LIME explanations for fitted tabular pipelines.

Both explain the model prediction, not causal relationships or student destiny.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def explain_shap(model, background: pd.DataFrame, record: pd.DataFrame, max_background=30):
    """Model-agnostic SHAP for a single row, returned as per-feature contributions.

    Computationally expensive; use only for one research record at a time.
    """
    import shap
    if len(record) != 1:
        raise ValueError("One student row required")
    columns = list(background.columns)
    sample = background[columns].sample(n=min(max_background, len(background)), random_state=42)
    reference = sample.iloc[0]

    def predict_from_array(values):
        frame = pd.DataFrame(values, columns=columns)
        for c in columns:
            frame[c] = pd.to_numeric(frame[c], errors="coerce")
        return model.predict_proba(frame)

    explainer = shap.Explainer(predict_from_array, sample, algorithm="permutation")
    explanation = explainer(record[columns], max_evals=max(2 * len(columns) + 1, 101))
    dropout_index = list(model.classes_).index("Dropout")
    effects = explanation.values[0, :, dropout_index]
    result = pd.DataFrame({"feature": columns, "shap_effect": effects}).sort_values(
        "shap_effect", key=abs, ascending=False)
    predicted = float(model.predict_proba(record[columns])[0, dropout_index])
    reconstructed = float(explanation.base_values[0, dropout_index] + effects.sum())
    result.attrs['additivity_error'] = abs(predicted - reconstructed)
    result.attrs['prediction'] = predicted
    if result.attrs['additivity_error'] > 1e-5:
        raise ValueError('SHAP reconstruction failed consistency check')
    return result


def explain_lime(model, background: pd.DataFrame, record: pd.DataFrame):
    """Local surrogate on raw numeric-coded UCI features, with readable names."""
    from lime.lime_tabular import LimeTabularExplainer
    from .ml import CAT_COLS
    names = list(background.columns)
    training = background[names].apply(pd.to_numeric, errors="coerce")
    medians = training.median().fillna(0)
    training = training.fillna(medians)
    instance = record[names].apply(pd.to_numeric, errors="coerce").fillna(medians)

    def predict(values):
        return model.predict_proba(pd.DataFrame(values, columns=names))

    categorical_indices = [i for i, col in enumerate(names) if col in CAT_COLS]
    explainer = LimeTabularExplainer(training.to_numpy(dtype=float), feature_names=names,
                                     class_names=list(model.classes_), mode="classification",
                                     categorical_features=categorical_indices,
                                     discretize_continuous=True, random_state=42)
    index = list(model.classes_).index("Dropout")
    result = explainer.explain_instance(instance.to_numpy(dtype=float)[0], predict,
                                        labels=[index], num_features=12)
    return pd.DataFrame(result.as_list(label=index), columns=["condition", "lime_weight"])


def global_shap(model, background, records, max_rows=10):
    """Mean absolute local contributions on a bounded, explicitly sampled cohort."""
    rows = records.sample(min(max_rows, len(records)), random_state=42)
    values = [explain_shap(model, background, rows.iloc[[i]]).set_index('feature').shap_effect.abs()
              for i in range(len(rows))]
    return pd.concat(values, axis=1).mean(axis=1).sort_values(ascending=False).rename('mean_absolute_shap').reset_index()


def plot_shap_figure(shap_df: pd.DataFrame, top_n: int = 12):
    """Generate an intuitive divergence Plotly bar chart for SHAP contributions toward Dropout."""
    import plotly.graph_objects as go
    top = shap_df.head(top_n).iloc[::-1]
    colors = ["#E63946" if val > 0 else "#2A9D8F" for val in top["shap_effect"]]

    fig = go.Figure(go.Bar(
        x=top["shap_effect"],
        y=top["feature"],
        orientation="h",
        marker=dict(color=colors, line=dict(width=1, color="rgba(0,0,0,0.15)")),
        text=[f"{val:+.3f}" for val in top["shap_effect"]],
        textposition="outside",
        hoverinfo="y+x"
    ))
    fig.update_layout(
        title=dict(text="<b>SHAP Feature Attribution (Impact on Dropout Probability)</b><br><sup>Red = Increases Dropout Risk | Green = Protective / Reduces Risk</sup>", font=dict(size=14)),
        xaxis=dict(title="SHAP Value", zeroline=True, zerolinecolor="rgba(100,100,100,0.4)", zerolinewidth=1.5),
        yaxis=dict(title=""),
        margin=dict(l=10, r=40, t=55, b=30),
        height=380,
        template="plotly_white"
    )
    return fig


def plot_lime_figure(lime_df: pd.DataFrame, top_n: int = 10):
    """Generate an intuitive Plotly horizontal bar chart for LIME local surrogate weights."""
    import plotly.graph_objects as go
    top = lime_df.head(top_n).iloc[::-1]
    colors = ["#E63946" if val > 0 else "#2A9D8F" for val in top["lime_weight"]]

    fig = go.Figure(go.Bar(
        x=top["lime_weight"],
        y=top["condition"],
        orientation="h",
        marker=dict(color=colors, line=dict(width=1, color="rgba(0,0,0,0.15)")),
        text=[f"{val:+.3f}" for val in top["lime_weight"]],
        textposition="outside",
        hoverinfo="y+x"
    ))
    fig.update_layout(
        title=dict(text="<b>LIME Local Surrogate Rule Weights</b><br><sup>Red = Pushes towards Dropout | Green = Pushes towards Non-Dropout</sup>", font=dict(size=14)),
        xaxis=dict(title="Local Weight", zeroline=True, zerolinecolor="rgba(100,100,100,0.4)", zerolinewidth=1.5),
        yaxis=dict(title=""),
        margin=dict(l=10, r=40, t=55, b=30),
        height=380,
        template="plotly_white"
    )
    return fig
