def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# TODO semaine 6: ajouter des tests sur app/core/tools/registry.py
# (validation des schémas, gestion des scopes de permission) et sur
# app/core/memory.py (sauvegarde/relecture de l'historique court terme).
