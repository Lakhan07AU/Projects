"""Notification abstraction. Only configured providers are used."""
import logging

from app.core.config import settings
from app.models import Notification, User

logger = logging.getLogger("healthsphere.notify")


def notify(db, user: User, title: str, body: str | None = None) -> None:
    """Create in-app notification; send email if SMTP is configured."""
    db.add(Notification(user_id=user.id, channel="in_app", title=title[:255], body=body))
    if settings.email_provider == "smtp" and user.email:
        _send_email(user.email, title, body or "")


def _send_email(to: str, subject: str, body: str) -> None:
    import smtplib
    from email.mime.text import MIMEText

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = settings.email_from
        msg["To"] = to
        with smtplib.SMTP(settings.smtp_host or "", settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password or "")
            server.sendmail(settings.email_from, [to], msg.as_string())
    except Exception:
        logger.warning("Email delivery failed for %s", to)


def get_map_provider():
    if settings.map_provider == "google" and settings.map_api_key:
        return GoogleMapsProvider()
    return MockHealthcareProvider()


class HealthcareLocationProvider:
    def nearby(self, lat: float, lon: float, kind: str, radius_km: float) -> list[dict]:
        raise NotImplementedError


class GoogleMapsProvider(HealthcareLocationProvider):
    """Google Places Nearby Search (new). Requires MAP_API_KEY."""

    KIND_MAP = {"hospital": "hospital", "clinic": "doctor", "lab": "hospital", "pharmacy": "pharmacy"}

    def nearby(self, lat: float, lon: float, kind: str, radius_km: float) -> list[dict]:
        import httpx

        resp = httpx.post(
            "https://places.googleapis.com/v1/places:searchNearby",
            headers={
                "X-Goog-Api-Key": settings.map_api_key or "",
                "X-Goog-FieldMask": (
                    "places.displayName,places.formattedAddress,"
                    "places.internationalPhoneNumber,places.location,"
                    "places.rating,places.currentOpeningHours"
                ),
            },
            json={
                "includedTypes": [self.KIND_MAP.get(kind, "hospital")],
                "maxResultCount": 12,
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": lat, "longitude": lon},
                        "radius": min(radius_km, 50) * 1000,
                    }
                },
            },
            timeout=10,
        )
        resp.raise_for_status()
        places = resp.json().get("places", [])
        results = []
        for p in places:
            loc = p.get("location", {})
            results.append({
                "name": p.get("displayName", {}).get("text", ""),
                "address": p.get("formattedAddress"),
                "phone": p.get("internationalPhoneNumber"),
                "distance_km": round(_haversine(lat, lon, loc.get("latitude"), loc.get("longitude")), 2),
                "opening_hours": None,
                "services": kind,
            })
        results.sort(key=lambda r: r["distance_km"])
        return results


class MockHealthcareProvider(HealthcareLocationProvider):
    """Deterministic demo provider — clearly labelled as sample data."""

    def nearby(self, lat: float, lon: float, kind: str, radius_km: float) -> list[dict]:
        base = [
            ("City General Hospital", "hospital", "12 MG Road", "+91-80-4000-1234", 1.8),
            ("Sunrise Family Clinic", "clinic", "44 Lake View Street", "+91-80-4000-5678", 2.4),
            ("MediCare Diagnostics Lab", "lab", "9 Station Road", "+91-80-4000-9012", 3.1),
            ("GreenCross Pharmacy", "pharmacy", "23 Market Lane", "+91-80-4000-3456", 0.7),
        ]
        results = [
            {
                "name": name,
                "kind": k,
                "address": addr,
                "phone": phone,
                "distance_km": dist,
                "opening_hours": "Mon-Sat 08:00-20:00",
                "services": k,
                "note": "Sample location data for development.",
            }
            for name, k, addr, phone, dist in base
            if kind in ("all", k)
        ]
        results.sort(key=lambda r: r["distance_km"])
        return results


def _haversine(lat1, lon1, lat2, lon2) -> float:
    from math import radians, sin, cos, asin, sqrt

    if None in (lat1, lon1, lat2, lon2):
        return 0.0
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))
