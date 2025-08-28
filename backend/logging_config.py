import json, logging, sys, time, uuid
from flask import request, g

class JsonFormatter(logging.Formatter):
    def format(self, record):
        base = {
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
        }
        if hasattr(record, "extra"):
            base.update(record.extra)
        return json.dumps(base, ensure_ascii=False)

def init_json_logging(app):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    app.logger.handlers = [handler]
    app.logger.setLevel(logging.INFO)

    @app.before_request
    def _start_timer():
        g._start = time.time()
        g.request_id = str(uuid.uuid4())

    @app.after_request
    def _log(response):
        duration = round(time.time() - g.get("_start", time.time()), 4)
        app.logger.info(
            "request",
            extra={
                "extra": {
                    "request_id": g.get("request_id"),
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "duration_s": duration,
                    "ip": request.remote_addr,
                }
            },
        )
        response.headers["X-Request-ID"] = g.get("request_id", "")
        return response
