import os
import pytest
from config import Config, ENV_CONFIG_FILE


def test_default():
    c = Config()
    assert_default_config(c)

def test_invalid_config():
    c = Config()
    with pytest.raises(AttributeError) as e:
        c.service.no
    assert "has no attribute 'no'" in str(e.value)


def test_not_support_config(tmpdir):
    path = tmpdir.mkdir("config").join("test.toml")
    path.write("""[globals]
other = "boor"

[foo]
bar = 4
haa = {yoo="kaa"}
""")
    c = Config().reload(str(path))
    assert_default_config(c)
    assert c.globals.other == "boor"
    assert c.foo.bar == 4
    assert c.foo.haa == {"yoo":"kaa"}


def assert_default_config(c: Config):
    assert c.service.port == 8000
    assert c.service.debug == False
    assert c.service.workers is None
    assert c.globals.env == "develop"
    assert c.log.path is None
    assert c.log.level == "INFO"
   

DEFAULT_CONFIG = """[globals]
id = "test_id"
env = "develop"

[service]
name = "test name"
port = 8000
debug = false
disable_trace = false
not_check_output = false

[log]
path = "service.log"
level = "INFO"
"""


def assert_config(c: Config):
    assert c.service.name == "test name"
    assert c.service.port == 8000
    assert c.service.debug == False
    assert c.service.disable_trace == False
    assert c.service.not_check_output == False
    assert c.globals.id == "test_id"
    assert c.globals.env == "develop"
    assert c.log.path == "service.log"
    assert c.log.level == "INFO"


def test_file(tmpdir):
    path = tmpdir.mkdir("config").join("test.toml")
    path.write(DEFAULT_CONFIG)
    c = Config()
    c.read_and_set_config()
    c.reload(str(path))
    assert_config(c)
    c.dump_config(str(path))


def test_env(tmpdir):
    path = tmpdir.mkdir("config").join("test.toml")
    path.write(DEFAULT_CONFIG)
    os.environ[ENV_CONFIG_FILE] = str(path)
    c = Config().reload()
    assert_config(c)


def test_only_env(tmpdir):
    path = tmpdir.mkdir("config").join("test.toml")
    path.write(DEFAULT_CONFIG)
    os.environ[ENV_CONFIG_FILE] = str(path)
    os.environ["MOCK"] = "1"
    c = Config().reload()
    assert_config(c)
    assert c.globals.resource_mock == "1"


def test_both_env_and_file(tmpdir):
    path = tmpdir.mkdir("config").join("test.toml")
    path.write("""[globals]
id = "test_id"

[service]
name = {value="test name from file", overwrite_env=true}
port = {value=8000, overwrite_env=false}
disable_trace = {value=true, overwrite_env=false}
not_check_output = {value=1, overwrite_env=true}
debug = {overwrite_env=true}
""")
    os.environ[ENV_CONFIG_FILE] = str(path)
    os.environ["ID"] = "id_from_env"
    os.environ["DISABLE_TRACE"] = "false"
    os.environ["SERVICE_NAME"] = "test name from env"
    os.environ["SERVICE_PORT"] = "9000"
    c = Config().reload()
    assert c.service.name == "test name from file"
    assert c.service.port == 9000
    assert c.service.debug == False
    assert c.service.not_check_output == True
    assert c.service.disable_trace == False
    assert c.globals.id == "test_id"
