#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <iostream>
#include <cstdio>
#include <cstdlib>

void redirect1() {
    std::cout<<"redirect using dup"<<std::endl;
    auto oldout = dup(STDOUT_FILENO);
    auto devnull = open("/dev/null", O_WRONLY);
    dup2(devnull, STDOUT_FILENO);
    std::cout<<"stdout to dev null"<<std::endl;
    std::cerr<<"stderr is ok"<<std::endl;
    // restore
    dup2(oldout, STDOUT_FILENO);
    std::cout<<"stdout is ok again"<<std::endl;
}

//  use freopen
void redirect2() {
    std::cout<<"redirect using freopen"<<std::endl;
    std::cout<<"stdout is ok"<<std::endl;
    freopen("/dev/null", "w", stdout);
    std::cout<<"stdout to dev null"<<std::endl;
    std::cerr<<"stderr is ok"<<std::endl;
    // restore
    fclose(stdout);
    stdout = fdopen(STDOUT_FILENO, "w");
    std::cout<<"stdout is ok again"<<std::endl;
}

int main() {
    redirect1();
    redirect2();
    return 0;
}
