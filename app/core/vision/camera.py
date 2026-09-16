"""Capacité caméra — capture d'une image depuis la webcam.

Implémente le port Capability (app/core/ports/capability.py) : s'enregistre
sous le nom "vision" dans app/core/capabilities/registry.py si une caméra
répond (cf. app/core/bootstrap.py). N'importe quel autre bloc peut alors
faire `registry.get("vision")` sans jamais importer ce module directement —
et si aucune caméra n'est branchée, Jarvis démarre quand même, juste sans
cette capacité (cf. app/core/tools/registry.py qui n'ajoute l'outil
`look_at_workspace` que si "vision" est enregistrée).

Semaine 19 de la roadmap. Nécessite `opencv-python-headless` et un accès
caméra — ne fonctionnera pas dans un conteneur sans device monté.
"""
import base64

import cv2

from app.core.ports.capability import Capability


class CameraCapability(Capability):
    name = "vision"

    def __init__(self, device_index: int = 0) -> None:
        self._device_index = device_index

    def is_available(self) -> bool:
        cap = cv2.VideoCapture(self._device_index)
        try:
            return cap.isOpened()
        except Exception:  # noqa: BLE001 — idem : health check caméra, jamais d'exception qui remonte
            return False
        finally:
            cap.release()

    def capture_frame_base64(self) -> str:
        """Capture une image et la retourne encodée en base64 (JPEG)."""
        cap = cv2.VideoCapture(self._device_index)
        try:
            if not cap.isOpened():
                raise RuntimeError(f"Impossible d'ouvrir la caméra (index {self._device_index}).")
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError("Échec de capture de la frame.")
            ok, buffer = cv2.imencode(".jpg", frame)
            if not ok:
                raise RuntimeError("Échec d'encodage JPEG.")
            return base64.b64encode(buffer).decode("utf-8")
        finally:
            cap.release()
