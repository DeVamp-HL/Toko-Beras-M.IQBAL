/*
 * jam_geser.c — pemalsu jam JVM Firebase Emulator untuk GLADI TUTUP BUKU (runner GitHub saja, .github/workflows/gladi-tutup-buku.yml).
 *
 * Rules v7 menilai berita acara tutup buku, pintu tutup buku & kunci periode dengan JAM SERVER (request.time). Halaman gladi berjam palsu
 * (31 Des 2026 / 1 Jan / 5 Jan 2027), runner berjam Okt 2026 → jam JVM emulator digeser GLADI_GESER_JAM detik ("+N", dari
 * gladi_tutup_buku.py --geser-jam). Dipasang lewat LD_PRELOAD oleh pembungkus `java` di depan PATH, HANYA untuk JVM emulator.
 *
 * Kenapa bukan libfaketime: run 7 Okt — libfaketimeMT dan libfaketime.so.1 sama-sama membuat emulator ±9,5× lebih lambat (150 commit: 2,05 →
 * 19,4 dtk), LANJUTKAN arsip tidak selesai dalam 47 menit. Di sini hanya jam DINDING yang digeser (CLOCK_REALTIME*, gettimeofday, time); jam
 * monoton & jam CPU utas/proses diteruskan apa adanya, tanpa kunci, tanpa membaca berkas — satu perbandingan & satu penjumlahan per panggilan.
 * Jam yang dihasilkan DIUKUR, bukan dipercaya: gladi_tutup_buku.py --cek-jam (transform REQUEST_TIME) + perbandingan kecepatan dengan emulator biasa.
 *
 *   gcc -O2 -shared -fPIC -o libjamgeser.so alat-uji/jam_geser.c -ldl
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdlib.h>
#include <sys/time.h>
#include <time.h>

/* jam dinding = yang digeser; CLOCK_REALTIME_COARSE hanya ada di Linux */
#ifdef CLOCK_REALTIME_COARSE
#define DINDING(j) ((j) == CLOCK_REALTIME || (j) == CLOCK_REALTIME_COARSE)
#else
#define DINDING(j) ((j) == CLOCK_REALTIME)
#endif

static long long geser = 0;
static int (*asli_clock_gettime)(clockid_t, struct timespec *) = 0;
static int (*asli_gettimeofday)(struct timeval *, void *) = 0;

__attribute__((constructor)) static void mulai(void) {
  const char *g = getenv("GLADI_GESER_JAM");
  geser = g ? atoll(g) : 0;
  asli_clock_gettime = (int (*)(clockid_t, struct timespec *))dlsym(RTLD_NEXT, "clock_gettime");
  asli_gettimeofday = (int (*)(struct timeval *, void *))dlsym(RTLD_NEXT, "gettimeofday");
}

int clock_gettime(clockid_t jam, struct timespec *t) {
  if (!asli_clock_gettime) mulai();
  int r = asli_clock_gettime(jam, t);
  if (r == 0 && t && DINDING(jam)) t->tv_sec += geser;
  return r;
}

int gettimeofday(struct timeval *tv, void *tz) {
  if (!asli_gettimeofday) mulai();
  int r = asli_gettimeofday(tv, tz);
  if (r == 0 && tv) tv->tv_sec += geser;
  return r;
}

time_t time(time_t *t) {
  struct timespec ts;
  if (clock_gettime(CLOCK_REALTIME, &ts) != 0) return (time_t)-1;
  if (t) *t = ts.tv_sec;
  return ts.tv_sec;
}
