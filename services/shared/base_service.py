"""
Base service class for all Nexova domain services.

Provides common patterns:
- CRUD operations against PostgreSQL
- Event publishing for cross-domain communication
- Observability (logging, metrics)
- Error handling
"""

import logging
from typing import Generic, TypeVar, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceError(Exception):
    """Base exception for service-layer errors."""
    def __init__(self, message: str, code: str = "SERVICE_ERROR", details: Optional[dict] = None):
        self.code = code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(ServiceError):
    def __init__(self, entity: str, entity_id: str):
        super().__init__(
            message=f"{entity} with id '{entity_id}' not found",
            code="NOT_FOUND",
            details={"entity": entity, "entity_id": entity_id},
        )


class ValidationError(ServiceError):
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message=message, code="VALIDATION_ERROR", details=details)


class BaseService(Generic[T]):
    """
    Generic base service with common CRUD patterns.
    Subclasses define their own domain model and data access.
    """

    def __init__(self, domain: str):
        self.domain = domain
        self.logger = logging.getLogger(f"service.{domain}")

    def _log(self, action: str, entity_id: Optional[str] = None, details: Optional[dict] = None):
        """Structured logging for observability."""
        self.logger.info(
            f"[{self.domain}] {action}",
            extra={
                "domain": self.domain,
                "action": action,
                "entity_id": entity_id,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def _publish_event(self, event_type: str, payload: dict):
        """
        Publish a domain event for cross-domain communication.
        In a real implementation, this would push to a message broker (Redis Pub/Sub, Kafka, etc.).
        """
        self._log("event_published", details={"event_type": event_type, "payload": payload})
        # TODO: Integrate with message broker
        # Example: redis.publish(f"nexova.{self.domain}.{event_type}", json.dumps(payload))

    def _validate_id(self, entity_id: str, entity_name: str = "Entity"):
        if not entity_id or not entity_id.strip():
            raise ValidationError(f"{entity_name} ID is required")