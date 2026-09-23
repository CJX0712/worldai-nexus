"""WorldAI Nexus - 错误类型层级。

作者: 晨星
"""


class WorldAIError(Exception):
    """所有领域错误的基类。"""


class ConfigError(WorldAIError):
    """配置或环境变量错误。"""


class ProviderError(WorldAIError):
    """LLM / 嵌入 / 向量库等外部提供方调用失败。"""


class IngestionError(WorldAIError):
    """文档加载或切分失败。"""


class RetrievalError(WorldAIError):
    """检索阶段失败。"""
