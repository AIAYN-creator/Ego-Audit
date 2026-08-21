from ego_audit.sandbox.config import (
    filesystem_args,
    full_run_args,
    hardening_args,
    network_args,
    resource_limit_args,
)


def test_network_args_blocks_all_network():
    assert network_args() == ["--network", "none"]


def test_resource_limit_args_sets_cpu_memory_and_pids():
    args = resource_limit_args(cpus=2.0, memory_mb=256)
    assert "--cpus" in args and "2.0" in args
    assert "--memory" in args and "256m" in args
    assert "--pids-limit" in args


def test_filesystem_args_is_read_only_with_mounted_work_dir():
    args = filesystem_args("/host/work")
    assert "--read-only" in args
    assert any("/host/work" in a for a in args)


def test_hardening_args_drops_all_capabilities_and_pins_nonroot_user():
    args = hardening_args()
    assert "--cap-drop" in args and "ALL" in args
    assert "--user" in args and "1000:1000" in args


def test_full_run_args_includes_every_isolation_layer():
    args = full_run_args("/host/work")
    assert "--network" in args
    assert "--read-only" in args
    assert "--cap-drop" in args
    assert "ego-audit-sandbox:latest" in args
    assert args[-1] == "/work/runner.py"


def test_full_run_args_includes_container_name_when_given():
    args = full_run_args("/host/work", container_name="my-container")
    assert "--name" in args
    assert "my-container" in args


def test_full_run_args_omits_name_flag_when_not_given():
    args = full_run_args("/host/work")
    assert "--name" not in args
