"""Fetch logged data from Weights & Biases runs and return as a pandas DataFrame."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd
import wandb
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn

_DEFAULT_CACHE_DIR = Path.home() / ".cache" / "get_wandb_data"

_console = Console()


def _cache_path(cache_dir: Path, run_id: str) -> Path:
    """Return the parquet cache file path for a run."""
    return cache_dir / f"{run_id}.parquet"


def get_wandb_data(
    run_ids: Sequence[str],
    keys: Sequence[str],
    entity: str | None = None,
    project: str | None = None,
    cache_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Fetch specified logged data from multiple W&B runs.

    Parameters
    ----------
    run_ids:
        List of W&B run IDs to fetch data from.
    keys:
        List of logged metric/data names to retrieve
        (e.g. ``["loss", "accuracy"]``).
    entity:
        W&B entity (user or team name).  If ``None``, uses the default
        entity configured in the current environment.
    project:
        W&B project name.  If ``None``, uses the default project
        configured in the current environment.
    cache_dir:
        Directory for the local cache.  Defaults to
        ``~/.cache/get_wandb_data``.  Each run is stored as a parquet
        file keyed by run ID; subsequent calls skip the W&B fetch.

    Returns
    -------
    pd.DataFrame
        A DataFrame where each row corresponds to one logged step of
        one run.  Columns include:

        - ``run_id`` – the run ID
        - ``run_name`` – the human-readable run name
        - ``tags`` – list of tags attached to the run
        - ``_step`` – the logging step number
        - one column per requested key
    """
    cdir = Path(cache_dir) if cache_dir is not None else _DEFAULT_CACHE_DIR
    cdir.mkdir(parents=True, exist_ok=True)

    api: wandb.Api | None = None  # lazy init — only created when needed

    frames: list[pd.DataFrame] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        console=_console,
    ) as progress:
        task = progress.add_task("Fetching runs", total=len(run_ids))

        for run_id in run_ids:
            cached = _cache_path(cdir, run_id)

            if cached.exists():
                progress.update(task, description=f"[dim]cached[/dim]  {run_id}")
                history = pd.read_parquet(cached)
            else:
                progress.update(task, description=f"[bold]fetch[/bold]   {run_id}")
                if api is None:
                    api = wandb.Api()
                path = "/".join(filter(None, [entity, project, run_id]))
                run = api.run(path)

                # Always include _step so it appears in the resulting DataFrame.
                fetch_keys = list(dict.fromkeys(["_step", *keys]))
                rows = list(run.scan_history(keys=fetch_keys))
                if not rows:
                    progress.advance(task)
                    continue

                history = pd.DataFrame(rows)
                history["run_id"] = run.id
                history["run_name"] = run.name
                history["tags"] = [run.tags] * len(history)

                # Save to local cache.
                history.to_parquet(cached, index=False)

            frames.append(history)
            progress.advance(task)

    if not frames:
        columns = ["run_id", "run_name", "tags", "_step"] + list(keys)
        return pd.DataFrame(columns=columns)

    df = pd.concat(frames, ignore_index=True)

    # Reorder columns: metadata first, then _step, then requested keys.
    leading = ["run_id", "run_name", "tags"]
    rest = [c for c in df.columns if c not in leading]
    df = df[leading + rest]

    _console.print(
        f"[green]Done:[/green] {len(df)} rows from {len(run_ids)} run(s)"
    )

    return df
