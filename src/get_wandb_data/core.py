"""Fetch logged data from Weights & Biases runs and return as a pandas DataFrame."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd
import wandb


# W&B media types that contain a downloadable file via the ``path`` key.
_MEDIA_TYPES = frozenset(
    {
        "image-file",
        "images/separated",
        "video-file",
        "audio-file",
        "html-file",
        "table-file",
        "object3D-file",
    }
)


def _is_media_cell(value: object) -> bool:
    """Return True if *value* is a W&B media reference dict."""
    return (
        isinstance(value, dict)
        and value.get("_type") in _MEDIA_TYPES
        and "path" in value
    )


def _download_media(
    run: wandb.apis.public.Run,
    media_path: str,
    dest_dir: Path,
) -> str:
    """Download a single media file and return the local path."""
    run_dir = dest_dir / run.id
    run_dir.mkdir(parents=True, exist_ok=True)
    try:
        f = run.file(media_path)
        f.download(root=str(run_dir), replace=True)
        return str(run_dir / media_path)
    except Exception:
        # If download fails, return the original W&B path as-is.
        return media_path


def get_wandb_data(
    run_ids: Sequence[str],
    keys: Sequence[str],
    entity: str | None = None,
    project: str | None = None,
    download_media: bool = False,
    media_dir: str | Path = "wandb_media",
) -> pd.DataFrame:
    """Fetch specified logged data from multiple W&B runs.

    Parameters
    ----------
    run_ids:
        List of W&B run IDs to fetch data from.
    keys:
        List of logged metric/data names to retrieve
        (e.g. ``["loss", "accuracy"]``).
        Media keys (images, videos, audio, etc.) are also supported —
        set *download_media* to ``True`` to download the actual files.
    entity:
        W&B entity (user or team name).  If ``None``, uses the default
        entity configured in the current environment.
    project:
        W&B project name.  If ``None``, uses the default project
        configured in the current environment.
    download_media:
        If ``True``, detect media columns (``wandb.Image``,
        ``wandb.Video``, ``wandb.Audio``, etc.) and download the files
        to *media_dir*.  The corresponding DataFrame cells are replaced
        with local file paths.
    media_dir:
        Directory to save downloaded media files.  A subdirectory per
        run ID is created automatically.  Defaults to ``"wandb_media"``
        in the current working directory.

    Returns
    -------
    pd.DataFrame
        A DataFrame where each row corresponds to one logged step of
        one run.  Columns include:

        - ``run_id`` – the run ID
        - ``run_name`` – the human-readable run name
        - ``tags`` – list of tags attached to the run
        - ``_step`` – the logging step number
        - one column per requested key (scalar value or local file path)
    """
    api = wandb.Api()
    dest = Path(media_dir)

    frames: list[pd.DataFrame] = []

    for run_id in run_ids:
        path = "/".join(filter(None, [entity, project, run_id]))
        run = api.run(path)

        # scan_history returns an iterator over *all* logged rows
        # (run.history() only returns a 500-row sample by default).
        rows = list(run.scan_history(keys=list(keys)))

        if not rows:
            continue

        history = pd.DataFrame(rows)

        # Download media files when requested.
        if download_media:
            for key in keys:
                if key not in history.columns:
                    continue
                history[key] = history[key].apply(
                    lambda cell, _run=run: (
                        _download_media(_run, cell["path"], dest)
                        if _is_media_cell(cell)
                        else cell
                    )
                )

        # Attach run metadata to every row.
        history["run_id"] = run.id
        history["run_name"] = run.name
        history["tags"] = [run.tags] * len(history)

        frames.append(history)

    if not frames:
        columns = ["run_id", "run_name", "tags", "_step"] + list(keys)
        return pd.DataFrame(columns=columns)

    df = pd.concat(frames, ignore_index=True)

    # Reorder columns: metadata first, then _step, then requested keys.
    leading = ["run_id", "run_name", "tags"]
    rest = [c for c in df.columns if c not in leading]
    df = df[leading + rest]

    return df
