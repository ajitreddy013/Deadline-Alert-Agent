from typing import Optional
try:
    from pync import Notifier
except Exception:  # pragma: no cover
    Notifier = None


def notify(title: str, message: str, subtitle: Optional[str] = None):
    if Notifier is None:
        # Fallback: print to console
        print(f"[NOTIFY] {title} - {message}")
        return
    kwargs = {"title": title, "message": message}
    if subtitle:
        kwargs["subtitle"] = subtitle
    try:
        Notifier.notify(message, title=title, subtitle=subtitle or "Deadline Reminder")
    except Exception as e:  # pragma: no cover
        print(f"Notification error: {e}")
