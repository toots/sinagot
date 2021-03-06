# coding=utf-8

import inspect
import pandas as pd
from sinagot.models import Model
from sinagot.utils import StepStatus, LOG_STEP_LABEL, LOG_STEP_STATUS


class Step(Model):

    _REPR_ATTRIBUTES = ["scope", "task", "modality", "label"]
    _MODEL_TYPE = "step"
    label = None
    id = None

    def __init__(self, script, model):

        self.model = model
        self.task = model.task
        self.modality = model.modality
        super().__init__(model.dataset)

        if inspect.isclass(script):
            script_class = script
            self.label = script.__class__.__name__
        elif isinstance(script, str):
            script_class = self._get_module("Script", self.modality, script)
            self.label = script
        else:
            raise AttributeError("Type {} is not valid for script".format(type(script)))

        if model._MODEL_TYPE == "record":
            self.id = model.id

        self.script_class = script_class
        self.script = script_class(
            data_path=self.dataset._data_path,
            id_=self.id,
            task=self.task,
            logger_namespace=self.logger.name,
        )

    def status(self):
        if self.script.path.output.exists():
            return StepStatus.DONE
        try:
            logs = self.logs()
            status = logs[logs[LOG_STEP_STATUS].notna()].iloc[0][LOG_STEP_STATUS]
        except:
            status = None
        if status == StepStatus.PROCESSING:
            return StepStatus.PROCESSING
        if self.script.path.input.exists():
            return StepStatus.DATA_READY
        else:
            return StepStatus.INIT

    def run(self):
        self.model.run()

    def logs(self):
        try:
            return self.model.logs().query(
                "{} == '{}'".format(LOG_STEP_LABEL, self.label)
            )
        except:
            return pd.DataFrame()
