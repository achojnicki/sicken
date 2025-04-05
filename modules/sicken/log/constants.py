from colored import fg

LEVEL_DEBUG=0
LEVEL_INFO=1
LEVEL_WARNING=2
LEVEL_ERROR=3
LEVEL_FATAL=4
LEVEL_SUCCESS=5

LOG_LEVELS=['DEBUG','INFO','WARNING','ERROR','FATAL','SUCCESS']
MSG_FORMAT="{project_name} {datetime} {log_level}:{filename}:{line_number} {function} PID:{pid} PPID:{ppid} CWD:{cwd} {message}\n"
TERMINAL_COLORS=[fg(248),fg(255),fg(227),fg(124),fg(9),fg(10)]
