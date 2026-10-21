/* time() 만 FIXT 환경 변수 값(유닉스 초)으로 고정 — LD_PRELOAD 용 */
#include <time.h>
#include <stdlib.h>
time_t time(time_t *t) { static time_t v = 0; if (!v) { const char *e = getenv("FIXT"); v = e ? (time_t)atoll(e) : 1700000000; } if (t) *t = v; return v; }
