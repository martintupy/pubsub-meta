from datetime import datetime, timedelta

from google.cloud.monitoring_v3 import ListTimeSeriesRequest, TimeInterval
from google.protobuf.timestamp_pb2 import Timestamp
from pubsub_meta.client import Client
from pubsub_meta.config import Config
from pubsub_meta.logger import Logger


class MetricsService:
    def __init__(self, client: Client, logger: Logger) -> None:
        self.client = client
        self.logger = logger

    def undelivered_messages(self, project_id: str, subscription_id: str, now: datetime) -> tuple[list, list]:
        start = Timestamp()
        start.FromDatetime(dt=now - timedelta(minutes=30))
        end = Timestamp()
        end.FromDatetime(dt=now)
        interval = TimeInterval({"start_time": start, "end_time": end})
        request = {
            "name": f"projects/{project_id}",
            "filter": f"""
                    metric.type = "pubsub.googleapis.com/subscription/num_undelivered_messages" AND 
                    resource.labels.subscription_id = "{subscription_id}"
                """,
            "interval": interval,
            "view": ListTimeSeriesRequest.TimeSeriesView.FULL,
        }
        self.logger.info(request)
        results = self.client.metrics_client.list_time_series(request)
        points = []
        dates = []
        for result in results:
            self.logger.info(result)
            points.append(result)
            for point in result.points:
                points.append(point.value.int64_value)
                dates.append(point.interval.end_time)
        return dates, points
