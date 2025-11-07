"""
로깅 설정 모듈
모든 로그 설정을 한 곳에서 관리합니다.
"""
import logging
import logging.config
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

# 로그 디렉토리 생성 (없으면 자동 생성)
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 로깅 설정 딕셔너리
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "access": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "app_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": str(LOG_DIR / "app.log"),
            "when": "midnight",
            "backupCount": 30,  # 30일치 보관
            "encoding": "utf-8"
        },
        "access_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": str(LOG_DIR / "access.log"),
            "when": "midnight",
            "backupCount": 30,
            "encoding": "utf-8"
        },
        "error_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "ERROR",
            "formatter": "standard",
            "filename": str(LOG_DIR / "error.log"),
            "when": "midnight",
            "backupCount": 30,
            "encoding": "utf-8"
        }
    },
    "loggers": {
        # 애플리케이션 로거 (일반 로그)
        "app": {
            "handlers": ["console", "app_file"],
            "level": "INFO",
            "propagate": False
        },
        # 접근 로그 (요청/응답 로그)
        "access": {
            "handlers": ["access_file"],
            "level": "INFO",
            "propagate": False
        },
        # 에러 로그
        "error": {
            "handlers": ["console", "error_file"],
            "level": "ERROR",
            "propagate": False
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO"
    }
}


def setup_logging():
    """
    로깅 설정을 초기화합니다.
    애플리케이션 시작 시 한 번만 호출하면 됩니다.
    """
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger("app")
    logger.info("로깅 설정이 초기화되었습니다.")
    return logger


# 접근 로그용 로거 (미들웨어에서 사용)
def get_access_logger():
    """접근 로그를 기록하는 로거를 반환합니다."""
    return logging.getLogger("access")


# 에러 로그용 로거
def get_error_logger():
    """에러 로그를 기록하는 로거를 반환합니다."""
    return logging.getLogger("error")