from enum import Enum


class AssetType(str, Enum):
    """
    Supported asset types defined in the assessment.
    """

    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    IP_ADDRESS = "ip_address"
    SERVICE = "service"
    CERTIFICATE = "certificate"
    TECHNOLOGY = "technology"


class AssetStatus(str, Enum):
    """
    Asset lifecycle status.
    """

    ACTIVE = "active"
    STALE = "stale"
    ARCHIVED = "archived"


class RelationType(str, Enum):
    """
    Relationship types between assets.
    """

    PARENT = "parent"
    COVERS = "covers"
    RESOLVES_TO = "resolves_to"
    HOSTED_ON = "hosted_on"
    POWERED_BY = "powered_by"

class AIIntent(str, Enum):
    """
    Supported AI operations.
    """

    QUERY = "query"

    RISK = "risk"

    REPORT = "report"

    ENRICHMENT = "enrichment"