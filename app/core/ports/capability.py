"""Port générique pour un "bloc" optionnel de Jarvis.

C'est ce qui rend le projet modulaire au sens où Alexis l'entend : la
caméra, la RAG, ou tout futur capteur (micro, GPS...) implémentent cette
interface minimale et s'enregistrent dans app/core/capabilities/registry.py.
Aucun autre bloc n'a besoin d'importer le module concret — il demande juste
"est-ce que 'vision' est disponible ?" au registre.

Conséquences concrètes :
- retirer un bloc (ou son service externe est down) -> le projet continue
  de tourner, avec juste une capacité en moins (cf. app/core/bootstrap.py).
- ajouter un bloc -> tout bloc qui sait déjà interroger le registre en
  profite immédiatement, sans être modifié.
"""
from abc import ABC, abstractmethod


class Capability(ABC):
    name: str

    @abstractmethod
    def is_available(self) -> bool:
        """Health check — jamais d'exception ici, retourner False si indisponible."""
        raise NotImplementedError
