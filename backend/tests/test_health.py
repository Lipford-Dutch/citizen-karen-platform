def test_backend_dependencies_importable():
    import fastapi
    import httpx

    assert fastapi.__version__
    assert httpx.__version__
