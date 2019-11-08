#include<iostream>
#include<thread>
#include<mutex>
#include<condition_variable>
#define P(str) std::cout<<str<<std::endl

// compile g++ cv.cpp -std=c++11
// functor/std::funtions problem
// use condition_variable in functor
// <this> is different with <&a>
// so done is always false, and always wait ...
// use ref done1 to update
struct A {
    A(bool &d):done(false),done1(d){}
    void operator() (){
        P("this= "<<(void*)this);
        {
            std::unique_lock<std::mutex> lk(m);
            done = true;
            done1 = true;
        }
        cv.notify_one();
    }
    static std::mutex m;
    static std::condition_variable cv;
    bool done;
    bool &done1;
};

std::mutex A::m;
std::condition_variable A::cv;

void fun(std::function<void(void)> cb) {
    cb();
}

void functor() {
    bool done=false;
    A a(done);
    fun(a);
    {
        P("&a= "<<(void*)&a);
        std::unique_lock<std::mutex> lk(a.m);
        //a.cv.wait(lk, [&]{return a.done;}); // not works !!!
        a.cv.wait(lk, [&]{return a.done1;});
    }
}

// use std::ref wrap
// instance a will be same, using done is OK
void functor_ref() {
    bool done=false;
    A a(done);
    fun(std::ref(a));
    {
        P("&a= "<<(void*)&a);
        std::unique_lock<std::mutex> lk(a.m);
        a.cv.wait(lk, [&]{return a.done;});
    }
}

// use condition_variable in lambda
// works
void lmd() {
    std::mutex m;
    std::condition_variable cv;
    bool done = false;
    auto cb = [&](){
        {
            std::unique_lock<std::mutex> lk(m);
            done = true;
        }
        cv.notify_one();
    };
    fun(cb);
    {
        std::unique_lock<std::mutex> lk(m);
        cv.wait(lk, [&]{return done;});
    }
}

int main() {
    lmd();
    functor();
    functor_ref();
}
