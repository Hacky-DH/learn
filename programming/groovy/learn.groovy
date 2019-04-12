/*
www.groovy-lang.org

Starting Groovysh
    docker run -it --rm groovy
Running a Groovy script
    docker run --rm -v "$PWD":/home/groovy/scripts -w /home/groovy/scripts groovy groovy <script> <script-args>
Or pre start a container
    docker run -d --rm groovy sleep 1d
    docker cp a.groovy 10aad6cd5430:/home/groovy/
    docker exec 10aad6cd5430 groovy a.groovy

https://learnxinyminutes.com/docs/groovy
*/

println("Hello Groovy")

//Variables
def x = 8 
println(x)
x = new java.util.Date()
println(x)

//Collections
def arr = ["java", "groovy"]
arr.add("scala")
arr << "kotlin"
println(arr)
arr.each { println("$it") }
arr.eachWithIndex { it,i -> println("$i: $it") }
arr.contains("groovy")
println('groovy' in arr)
println(arr*.toUpperCase())

//maps
def map = [:] 
map = ['name':'groovy','type':'lang']
map.put('age', 16)
assert map.containsKey('name')
assert map.containsValue('lang')
println(map)

//classes
class Foo {
    final def type = 'lang'
    String name = 'groovy'
    def meta
}

// if same as java
x = 0
for (i in 1..20) {
    x += i
}
println(x)

//Closures
def sum = { a, b -> println(a+b) }
sum(5, 8)

