/* Optional host compatibility only. Lean 4.19 asks for /proc/<getpid()>/exe.
 * Some containers expose the semantically identical /proc/self/exe only.
 * Redirect exactly the current process path, never other process paths.
 * No proof-checker or mathematical operation is changed. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
ssize_t readlink(const char *path, char *buf, size_t size) {
  static ssize_t (*real_readlink)(const char*,char*,size_t) = NULL;
  if (!real_readlink) real_readlink = dlsym(RTLD_NEXT, "readlink");
  char own[64];
  snprintf(own,sizeof(own),"/proc/%d/exe",getpid());
  return real_readlink(strcmp(path,own)==0 ? "/proc/self/exe" : path,buf,size);
}
