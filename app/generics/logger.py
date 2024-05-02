import uuid
import json
import logging
from pytz import timezone
from .settings import settings
from datetime import datetime
from pythonjsonlogger import jsonlogger


TZ = timezone('Asia/Bangkok')


class ModelJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


class CustomFilter(logging.Filter):
    def filter(self, record):
        record.level = record.levelname
        record.time = datetime.now(TZ).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        record.caller = f'{record.pathname}:{record.lineno}'
        record.funcName = record.funcName
        return True


class JsonLogFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        if not log_record.get("timestamp"):
            now = datetime.utcnow().isoformat()
            log_record["timestamp"] = now
        log_record['env'] = settings.ENVIRONMENT
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname
        
        log_record['caller'] = f'{record.pathname}:{record.lineno}'
        log_record['funcName'] = record.funcName


class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.env = settings.ENVIRONMENT
        return super().format(record)