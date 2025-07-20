# 规则2：编码规范与风格指南

## 1. 日志记录

-   在所有关键操作（如API请求、文件操作、状态变更）前后，使用`logger.info()`、`logger.warning()`或`logger.error()`记录详细日志。
-   日志信息应清晰、简洁，并包含关键上下文信息（如`chat_id`、`model_id`、`file_path`等）。
-   使用`logger.debug()`记录详细的请求载荷（payload）等调试信息。

## 2. 类型提示

-   所有函数和方法的参数及返回值都必须有明确的类型提示（Type Hinting）。
-   使用`typing`模块中的`Optional`, `List`, `Dict`, `Tuple`等来精确描述数据结构。

## 3. 异常处理

-   在进行API请求或文件I/O等可能失败的操作时，必须使用`try...except`块进行异常处理。
-   优先捕获具体的异常类型（如`requests.exceptions.RequestException`, `json.JSONDecodeError`, `KeyError`），避免宽泛的`except Exception`。
-   在`except`块中，必须使用`logger.error()`记录详细的错误信息，包括异常本身和相关上下文。

## 4. 命名与代码风格

-   遵循PEP 8编码规范。
-   内部辅助方法（不应由用户直接调用）应使用单个下划线前缀（如`_ask`、`_upload_file`）。
-   常量和配置项应在`__init__`方法中初始化并作为实例属性（如`self.base_url`）。
-   优先使用f-string进行字符串格式化。
