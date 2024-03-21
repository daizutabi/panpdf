import asyncio


def test_get_pandoc_path():
    from panpdf.tools import PANDOC_PATH, get_pandoc_path

    PANDOC_PATH.clear()
    path = get_pandoc_path()
    assert path
    assert PANDOC_PATH[0] is path


def test_get_pandoc_version():
    from panpdf.tools import get_pandoc_version

    assert get_pandoc_version().startswith("3.")


def test_get_data_dir():
    from panpdf.tools import get_data_dir

    assert get_data_dir().name == "pandoc"


def test_run():
    from panpdf.tools import run

    args = ["python", "-c" "print(1);1/0"]

    out: list[str] = []
    err: list[str] = []

    def stdout(output: str) -> None:
        out.append(output)

    def stderr(output: str) -> None:
        err.append(output)

    asyncio.run(run(args, stdout, stderr))
    assert out[0].strip() == "1"
    assert err[0].strip().startswith("Traceback")


def test_progress():
    from panpdf.tools import progress

    args = ["python", "-c" "print(1);1/0"]

    assert progress(args)

    args = ["python", "--version"]

    assert not progress(args)
