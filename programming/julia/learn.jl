module learn
# using import export include

# parse the cmdline args
for x in ARGS
	println(x)
end

sum = 0
for i = 1:5
	# if no global, sum in for will throw UndefVarError
	global sum
    sum += i
end
println(sum) # 15

let sum = sum
	sum = 100
	println(sum) # 100
end
println(sum) # 15

const A = 8

# 'do' will auto close the open file
open("outfile", "w") do io
    write(io, "Hello Julia")
end
rm("outfile")

end

baremodule recordLib
using Base

struct point
    x::Float64
    y::Float64
end
function hyp(p::point)
    hypot(p.x, p.y)
end
p = point(3.2, 4.8)
println(hyp(p))

end

module net
using Sockets
@async begin
   server = listen(2000)
   while true
       sock = accept(server)
       println("Hello World\n")
       @async while true
         write(sock,readline(sock))
       end
   end
end
client = connect(2000)
#readline(client)
end

module parallel
# Given Channels c1 and c2,
c1 = Channel(32)
c2 = Channel(32)

# and a function `foo` which reads items from c1, processes the item read
# and writes a result to c2,
function foo()
    while true
        data = take!(c1)
        result = data
        put!(c2, result)    # write out result
    end
end

# we can schedule `n` instances of `foo` to be active concurrently.
for _ in 1:3
    @async foo()
end
end