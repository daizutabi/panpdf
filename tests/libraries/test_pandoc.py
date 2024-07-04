import subprocess


def test_math():
    text = "a\n$$a$$\nb"
    args = ["pandoc", "--from", "markdown", "--to", "latex"]
    out = subprocess.check_output(args, input=text, text=True)
    assert out.strip() == r"a \[a\] b"
