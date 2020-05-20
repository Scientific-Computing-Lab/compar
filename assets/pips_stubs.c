#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
  int x;
} omp_lock_t;

typedef struct {
  int x;
} omp_nest_lock_t;

typedef enum omp_sched_t { x = 1 } omp_sched_t;

void omp_set_num_threads(int num_threads);
int omp_get_num_threads();
int omp_get_max_threads();
int omp_get_thread_num();
int omp_get_thread_limit();
int omp_get_num_procs();
int omp_in_parallel();
void omp_set_dynamic(int dynamic_threads);
int omp_get_dynamic();
void omp_set_nested(int nested);
int omp_get_nested();
void omp_set_schedule(omp_sched_t kind, int modifier);
void omp_get_schedule(omp_sched_t *kind, int *modifier);
void omp_set_max_active_levels(int max_levels);
int omp_get_max_active_levels();
int omp_get_level();
int omp_get_ancestor_thread_num(int level);
int omp_get_team_size(int level);
int omp_get_active_level();
int omp_in_final();
void omp_init_lock(omp_lock_t *lock);
void omp_init_nest_lock(omp_nest_lock_t *lock);
void omp_destroy_lock(omp_lock_t *lock);
void omp_destroy_nest_lock(omp_nest_lock_t *lock);
void omp_set_lock(omp_lock_t *lock);
void omp_set_nest__lock(omp_nest_lock_t *lock);
void omp_unset_lock(omp_lock_t *lock);
void omp_unset_nest__lock(omp_nest_lock_t *lock);
int omp_test_lock(omp_lock_t *lock);
int omp_test_nest__lock(omp_nest_lock_t *lock);
double omp_get_wtime();
double omp_get_wtick();

void omp_set_num_threads(int num_threads) { return; }
int omp_get_num_threads() { return rand(); }
int omp_get_max_threads() { return rand(); }
int omp_get_thread_num() { return rand(); }
int omp_get_thread_limit() { return rand(); }
int omp_get_num_procs() { return rand(); }
int omp_in_parallel() { return rand(); }
void omp_set_dynamic(int dynamic_threads) { return; }
int omp_get_dynamic() { return rand(); }
void omp_set_nested(int nested) { return; }
int omp_get_nested() { return rand(); }
void omp_set_schedule(omp_sched_t kind, int modifier) { return; }
void omp_get_schedule(omp_sched_t *kind, int *modifier) { return; }
void omp_set_max_active_levels(int max_levels) { return; }
int omp_get_max_active_levels() { return rand(); }
int omp_get_level() { return rand(); }
int omp_get_ancestor_thread_num(int level) { return rand(); }
int omp_get_team_size(int level) { return rand(); }
int omp_get_active_level() { return rand(); }
int omp_in_final() { return rand(); }
void omp_init_lock(omp_lock_t *lock) { return; }
void omp_init_nest_lock(omp_nest_lock_t *lock) { return; }
void omp_destroy_lock(omp_lock_t *lock) { return; }
void omp_destroy_nest_lock(omp_nest_lock_t *lock) { return; }
void omp_set_lock(omp_lock_t *lock) { return; }
void omp_set_nest__lock(omp_nest_lock_t *lock) { return; }
void omp_unset_lock(omp_lock_t *lock) { return; }
void omp_unset_nest__lock(omp_nest_lock_t *lock) { return; }
int omp_test_lock(omp_lock_t *lock) { return rand(); }
int omp_test_nest__lock(omp_nest_lock_t *lock) { return rand(); }
double omp_get_wtime() { return (double)rand(); }
double omp_get_wtick() { return (double)rand(); }
