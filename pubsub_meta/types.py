from dataclasses import dataclass


@dataclass
class SubscriptionParsed:
    project_id: str
    subscription_id: str

    @staticmethod
    def from_subscription(sub: str):
        [_, project_id, _, subscription_id] = sub.split("/")
        return SubscriptionParsed(
            project_id=project_id,
            subscription_id=subscription_id,
        )
