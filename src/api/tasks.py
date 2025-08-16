from .celery_app import celery_app
from ..optimisation import run_policy_optimisation
from ..microsim import load_parameters
import pandas as pd
import os

@celery_app.task
def run_optimisation_task(opt_config: dict, base_year: str, dataset_path: str):
    """
    A Celery task to run a policy optimisation.
    """
    if not os.path.exists(dataset_path):
        # This should be handled before calling the task, but as a safeguard.
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    df = pd.read_csv(dataset_path)

    # The metrics functions need to be defined here or be importable.
    # For now, let's define a simple one. A more robust solution would
    # be to have a registry of metrics.
    def total_tax_revenue(df: pd.DataFrame) -> float:
        return df["tax_liability"].sum()

    metrics = {
        "total_tax_revenue": total_tax_revenue
    }

    study = run_policy_optimisation(
        base_df=df,
        base_year=base_year,
        opt_config=opt_config,
        metrics=metrics
    )

    # We need to return JSON-serializable results.
    # The full study object is not serializable.
    return {
        "best_trial_number": study.best_trial.number,
        "best_value": study.best_value,
        "best_params": study.best_params,
        "all_trials": [
            {
                "trial_number": t.number,
                "value": t.value,
                "params": t.params,
                "user_attrs": t.user_attrs,
            }
            for t in study.trials
        ]
    }
