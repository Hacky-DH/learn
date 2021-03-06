package main

import (
	"fmt"
	"net/http"
	"regexp"
	"strings"
)

func main() {
	reso := newPathResolver()
	reso.Add("GET /hello", hello)
	reso.Add("(GET|HEAD) /goodbye(/?[A-Za-z0-9]*)?", goodbye)
	http.ListenAndServe(":8080", reso)
}

type regexpResolver struct {
	handlers map[string]http.HandlerFunc
	cache    map[string]*regexp.Regexp
}

func newPathResolver() *regexpResolver {
	return &regexpResolver{
		handlers: make(map[string]http.HandlerFunc),
		cache:    make(map[string]*regexp.Regexp),
	}
}

func (r *regexpResolver) Add(regex string, hander http.HandlerFunc) {
	r.handlers[regex] = hander
	cache, _ := regexp.Compile(regex)
	r.cache[regex] = cache
}

func (r *regexpResolver) ServeHTTP(res http.ResponseWriter, req *http.Request) {
	check := req.Method + " " + req.URL.Path
	for pattern, handlerFunc := range r.handlers {
		if r.cache[pattern].MatchString(check) {
			handlerFunc(res, req)
			return
		}
	}
	http.NotFound(res, req)
}

func hello(res http.ResponseWriter, req *http.Request) {
	query := req.URL.Query()
	name := query.Get("name")
	if name == "" {
		name = "webserver from go"
	}
	fmt.Fprint(res, "Hello ", name)
}

func goodbye(res http.ResponseWriter, req *http.Request) {
	path := req.URL.Path
	parts := strings.Split(path, "/")
	name := ""
	if len(parts) > 2 {
		name = parts[2]
	}
	if name == "" {
		name = "webserver from go"
	}
	fmt.Fprint(res, "Goodbye ", name)
}
