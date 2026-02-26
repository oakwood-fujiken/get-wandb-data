"""Fetch logged data from Weights & Biases runs and return as a pandas DataFrame."""

from __future__ import annotations

from typing import Sequence

import pandas as pd
import wandb


def get_wandb_data(
    run_ids: Sequence[str],
    keys: Sequence[str],
    entity: str | None = None,
    project: str | None = None,
) -> pd.DataFrame:
    """Fetch specified logged data from multiple W&B runs.

    Parameters
    ----------
    run_ids:
        List of W&B run IDs to fetch data from.
    keys:
        List of logged metric/data names to retrieve (e.g. ``["loss", "accuracy"]``).
    entity:
        W&B entity (user or team name). If ``None``, uses the default entity
        configured in the current environment.
    project:
        W&B project name. If ``None``, uses the default project configured in
        the current environment.

    Returns
    -------
    pd.DataFrame
        A DataFrame where each row corresponds to one logged step of one run.
        Columns include:

        - ``run_id`` – the run ID
        - ``run_name`` – the human-readable run name
        - ``tags`` – list of tags attached to the run
        - ``_step`` – the logging step number
        - one column per requested key
    """
    api = wandb.Api()

    frames: list[pd.DataFrame] = []

    for run_id in run_ids:
        path = "/".join(filter(None, [entity, project, run_id]))
        run = api.run(path)

        # Fetch the history rows for the requested keys
        # Always include _step so we have an index column.
        history = run.history(keys=list(keys))

        if history.empty:
            continue

        # Attach run metadata to every row
        history["run_id"] = run.id
        history["run_name"] = run.name
        history["tags"] = [run.tags] * len(history)

        frames.append(history)

    if not frames:
        # Return an empty DataFrame with the expected columns
        columns = ["run_id", "run_name", "tags", "_step"] + list(keys)
        return pd.DataFrame(columns=columns)

    df = pd.concat(frames, ignore_index=True)

    # Reorder columns: metadata first, then _step, then requested keys
    leading = ["run_id", "run_name", "tags"]
    rest = [c for c in df.columns if c not in leading]
    df = df[leading + rest]

    return df
