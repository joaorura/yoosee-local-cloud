from yoosee_local.cli import parse_args


def test_parse_args_defaults():
    args = parse_args([])
    assert args.host == "0.0.0.0"
    assert args.http_port == 8080
    assert 32100 in args.udp_ports
    assert not args.reply_ack


def test_parse_args_custom():
    args = parse_args(
        [
            "--host",
            "127.0.0.1",
            "--http-port",
            "80",
            "--https-port",
            "443",
            "--udp-ports",
            "18443",
            "18800",
            "--reply-ack",
            "-v",
        ]
    )
    assert args.host == "127.0.0.1"
    assert args.http_port == 80
    assert args.https_port == 443
    assert args.udp_ports == [18443, 18800]
    assert args.reply_ack is True
    assert args.verbose is True
