import os
import toml
from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Any, Optional

ENV_CONFIG_FILE = "SERVICE_CONFIG_FILE"

def singleton(cls):
    instances = {}

    def _singleton(*args, **kwargs):
        key = str(cls) + str(os.getpid())
        if key not in instances:
            instances[key] = cls(*args, **kwargs)
        return instances[key]

    return _singleton


@singleton
class Config(BaseModel):
    """支持从配置文件，环境变量获取配置

    配置文件是可选的，没有时使用SUPPORT_CONFIGS中的默认配置

    >>> c = Config()
    >>> c.service.name
    """
    model_config = ConfigDict(extra='allow')
    config_file: Optional[str] = Field(default=None)
    configs: Optional[dict[str, Any]] = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def read_and_set_config(self):
        if self.configs is not None:
            return self
        if self.config_file:
            raw_configs = self.load_config(self.config_file)
        elif ENV_CONFIG_FILE in os.environ:
            config_file = os.environ[ENV_CONFIG_FILE]
            raw_configs = self.load_config(config_file)
        else:
            raw_configs = {}
        self.configs = {}
        for ns, config in SUPPORT_CONFIGS.items():
            for k, v in config.items():
                config_value = None
                if ns in raw_configs and k in raw_configs[ns]:
                    config_value = raw_configs[ns][k]
                if ns not in self.configs:
                    self.configs[ns] = {}
                self.configs[ns][k] = ConfigItem(
                    key_=k,
                    env_key_=v["env_key"],
                    value_=config_value,
                    value_type=v.get("type", "str"),
                    default_value_=v["default_value"])
            setattr(self, ns, ConfigCollection(configs=self.configs[ns]))
        # 处理不在SUPPORT_CONFIGS中的configs
        for ns, config in raw_configs.items():
            if hasattr(self, ns):
                collection_configs = getattr(self, ns).configs
                for k, v in config.items():
                    if k not in collection_configs:
                        collection_configs[k] = ConfigItem(key_=k, value_=v)
                    else:
                        pass #上面已经处理过
            else:
                if ns not in self.configs:
                    self.configs[ns] = {}
                for k, v in config.items():
                    self.configs[ns][k] = ConfigItem(key_=k, value_=v)
                setattr(self, ns, ConfigCollection(configs=self.configs[ns]))
        return self

    def reload(self, config_file: str | None = None):
        self.config_file = config_file
        self.configs = None
        return self.read_and_set_config()

    @staticmethod
    def load_config(config_file: str):
        try:
            if os.path.exists(config_file):
                return toml.load(config_file)
        except Exception as e:  # pragma: no cover
            raise ValueError(f"配置文件格式错误: {e}") from None

    def dump_config(self, config_file: str):
        config_dict = {}
        for ns, config in self.configs.items():
            config_dict[ns] = {}
            for k, _ in config.items():
                config_dict[ns][k] = getattr(getattr(self, ns), k)
        with open(config_file, "w") as f:
            toml.dump(config_dict, f)


class ConfigItem(BaseModel):
    model_config = ConfigDict(extra='allow')
    key_: str  # toml中的key, name
    env_key_: Optional[str] = None
    # 环境变量中的key
    value_: Optional[Any] = None  # 一般是来自文件
    value_type: Optional[str] = None  #支持str, int, bool, float
    # 可以配置成dict {value=..., overwrite_env=true}
    default_value_: Optional[Any] = None

    @model_validator(mode="after")
    def set_config(self):
        """
        value取value_和环境变量的值：
        1. 都没设置时，使用default_value
        2. 都设置时，如果value_是dict并overwrite_env=true取value_的值,默认是true
            value_中没有value时取default_value
        3. 只有一个设置，那取那个值
        """
        if hasattr(self, self.key_):
            return self
        # import traceback
        # traceback.print_stack()
        final_value = None
        env_value = os.getenv(self.env_key_) if self.env_key_ else None
        if env_value is not None and self.value_ is not None:
            final_value = self._get_overwrite_value(env_value)
        elif self.value_ is not None:
            final_value = self._get_overwrite_value(self.default_value_)
        elif env_value is not None:
            final_value = env_value
        else:
            final_value = self.default_value_
        setattr(self, self.key_, self._convert_value(final_value))
        return self

    def _get_overwrite_value(self, env_value: Any):
        if isinstance(self.value_, dict) and "overwrite_env" in self.value_:
            if self.value_["overwrite_env"]:
                if "value" in self.value_:
                    return self.value_["value"]
                else:
                    return self.default_value_
            else:
                return env_value
        return self.value_

    def _convert_value(self, value: Any) -> Any:
        if self.value_type is None:
            return value
        elif self.value_type == "int":
            return int(value) if value is not None else value
        elif self.value_type == "bool":
            if isinstance(value, bool):
                return value
            elif isinstance(value, str):
                return value.lower() in ["true", "1", "t", "yes", "y"]
            return bool(value) if value is not None else value
        elif self.value_type == "float":
            return float(
                value) if value is not None else value  # pragma: no cover
        else:
            return str(value) if value is not None else value


class ConfigCollection(BaseModel):
    configs: dict[str, ConfigItem]

    def __getattr__(self, name: str) -> Any:
        if name in self.configs:
            return getattr(self.configs[name], name)
        return super().__getattr__(name)


# 默认支持的配置，设置了对应配置的环境变量，默认值和类型，默认类型是str
SUPPORT_CONFIGS = {
    "service": {
        "name": {
            "env_key": "SERVICE_NAME",
            "default_value": "service"
        },
        "port": {
            "env_key": "SERVICE_PORT",
            "default_value": 8000,
            "type": "int"
        },
        "debug": {
            "env_key": "DEBUG",
            "default_value": False,
            "type": "bool"
        }
    },
    "globals": {
        "env": {
            "env_key": "ENV",
            "default_value": "develop"
        }
    },
    "log": {
        "path": {
            "env_key": "LOG_PATH",
            "default_value": None
        },
        "level": {
            "env_key": "LOG_LEVEL",
            "default_value": "INFO"
        }
    }
}
