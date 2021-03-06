"""Test record log file un JSON"""

import pandas as pd
from sinagot.utils import StepStatus, LOG_STEP_STATUS


def test_log_no_empty(record):

    assert isinstance(record.logs(), pd.DataFrame)
    assert len(record.logs()) == 0


def test_log_all(record):

    record.run()
    logs = record.logs()
    assert set(logs.scope.unique()) == {"record"}
    assert set(logs.task.unique()) == set(record.config["tasks"])
    assert set(logs.modality.unique()) == set(record.config["modalities"]) - {
        "clinical"
    }


def test_log_subscope(record):

    record.run()

    # Task
    logs = record.HDC.logs()
    assert set(logs.task.unique()) == {"HDC"}
    assert set(logs.modality.unique()) == {"EEG", "behavior"}

    # Modality
    logs = record.EEG.logs()
    assert set(logs.task.unique()) == {"HDC", "MMN", "RS"}
    assert set(logs.modality.unique()) == {"EEG"}

    # Unit
    logs = record.HDC.EEG.logs()
    assert set(logs.task.unique()) == {"HDC"}
    assert set(logs.modality.unique()) == {"EEG"}


def test_log_status(record):

    assert len(record.logs()) == 0
    record.run()
    assert StepStatus.PROCESSING in list(record.logs()[LOG_STEP_STATUS].unique())
    assert StepStatus.DONE in list(record.logs()[LOG_STEP_STATUS].unique())
