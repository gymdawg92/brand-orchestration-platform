def _create_brand(client, slug="auxo", config=None):
    body = {
        "slug": slug,
        "name": slug.title(),
        "api_key": f"bop-{slug}-testkey",
    }
    if config is not None:
        body["config"] = config
    r = client.post("/brands", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_tech_stack_returns_project_refs_and_stack(client):
    config = {
        "vertical": "ai-fitness",
        "project_refs": [
            {
                "type": "claude_code",
                "id": "auxo-ios-placeholder",
                "label": "Auxo iOS",
                "repo_url": None,
            }
        ],
        "tech_stack": {
            "languages": ["swift"],
            "frameworks": ["swiftui", "uikit"],
            "data": ["oracle"],
            "distribution": ["app_store"],
            "notes": "iOS-native app.",
        },
    }
    _create_brand(client, slug="auxo", config=config)

    r = client.get("/brands/auxo/tech-stack")
    assert r.status_code == 200
    body = r.json()
    assert body["project_refs"] == config["project_refs"]
    assert body["tech_stack"] == config["tech_stack"]
    assert "updated_at" in body


def test_tech_stack_defaults_when_config_missing_keys(client):
    _create_brand(client, slug="bare", config={"vertical": "media"})

    r = client.get("/brands/bare/tech-stack")
    assert r.status_code == 200
    body = r.json()
    assert body["project_refs"] == []
    assert body["tech_stack"] == {}


def test_tech_stack_404_for_unknown_brand(client):
    r = client.get("/brands/does-not-exist/tech-stack")
    assert r.status_code == 404
    assert r.json()["detail"] == "Brand not found"
