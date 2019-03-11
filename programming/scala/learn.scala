/**
 * MIT License
 *
 * Copyright (c) 2019 DHacky
 */

//scala stdlib
//https://www.scala-lang.org/api/current/scala/

// scala school
// https://twitter.github.io/scala_school/zh_cn/

// Effective Scala
// https://twitter.github.io/effectivescala/index-cn.html

// use pure functions no side effect
// EOP expression oriented programming

// see how the scala is compiling
//1. scala -Xprint:parse learn.scala
//2. scalac learn.scala && javap learn

object learn {
	def str() {
		// scala strings
		// String StringOps StringLike
		var s = "hello scala"
		for ( c <- s) println(c) // implement by foreach
		s.foreach(println)
		s.getBytes().foreach(println)
		println(s.filter(_!='l')) //heo scaa
		println(s.drop(6).take(5).capitalize) //Scala
		println(s.map(_.toUpper))

		var num = 886
		println(s"${s} $num")
		var retio = 0.8
		println(f"${s} ${retio}%.2f")

		var pattern = "[0-9]+".r
		println(pattern.findFirstIn(s)) //None, may return Option Some/None

		implicit class StringU(s:String) {
			def add = s.map(c=>(c+1).toChar)
			def toIntw(radix:Int) = Integer.parseInt(s, radix)
		}
		println(s.add) // real magic!!!
		println("345".toInt)
		println("f0f0".toIntw(16))
		println("10101".toIntw(2))
	}

	def control() {
		var x = if (1<3) 4 else 5
		println(x)
		for ((v, i) <- (1 to 10).zipWithIndex) {
			println(s"$i is $v")
		}
		val mm = Map(23->"one", 45->"two")
		for ((k, v) <- mm) println(s"$k $v")
		for (i <- 1 to 10 if i%2==0) println(i)

		var i = 8
		i match {
			case 1 => println(1)
			case 2 | 3 | 4 => println(s"haha $i")
			case a if 5 to 10 contains a => println(s"hehe $i")
			case _ => println("unexpected")
		}

		import util.control.Breaks._
		breakable {
			for (i <- 1 to 10) {
				if (i > 4) break
			}
		}
	}

	def cls() {
		val p = new Person(1, "scala")
		p.age = 15
		println(p)
		var pp = People("scala")
		println(pp)
		val e = new Employee("James", "main")
		println(e)
		println(e.hello)
		println(e.getInfo)
		e.work("step1", "step6")

		//class
		println(classOf[Person])
		println(classOf[String])
		println(e.getClass)
	}

	def func() {
		// Partial application or function binding
		def adder(a:Int ,b :Int) = a + b
		val add8 = adder(_, 8)
		println(add8(7))
		// curry
		def multiply(m: Int)(n: Int): Int = m * n
		println(multiply(8)(9))
		val timesTwo = multiply(2)_
		println(timesTwo(8))
		println(AddOne(7))
	}
}

// trait like Interface in java, but can be implement
trait Human {
	def printHome
	def hello = "Human"
}

trait Cache[K, V] {
  def get(key: K): V
  def put(key: K, value: V)
  def delete(key: K)
}

class Person(val id:Int, var name:String, var race:String="yellow") extends Human {
	var age = 18
	private val HOME = System.getProperty("user.home")
	// name and age have getter and setter
	// id has getter no setter
	// HOME has no getter and setter

	// auxiliary constructor
	def this(name :String) {
		//call the main constructor
		this(Person.ID, name) // weird! I prefer this.ID
	}
	override def printHome { println(s"This is my home $HOME") }
	printHome
	override def toString = s"$name is #$id, $race race, and $age years old"
	override def hello = "Person"
}

// companion object
// like static members
object Person {
	val ID = 1
}

class Employee(name :String, var role :String) extends Person(name) {
	override def toString = s"${super.toString}, role is $role"
	override def hello = "Employee"

	// return multi value tuples (tuple1 to tuple22)
	// val (name, age, role) = getInfo
	def getInfo() = (name, age, role)

	// varargs 0 or more
	// use list:_* pass a collection
	def work(params :String*): this.type = {
		println(params.getClass)
		params.foreach(println)
		// method chaining
		// return this.type
		this
	}
}

// default attributes is read only (val)
// default functions: toString unapply equals hashCode copy
case class People(var name :String)

// function is object
// Function1[Int, Int]
// Function1 ~ Function22
object AddOne extends (Int => Int) {
  def apply(m: Int): Int = m + 1
}

// object learn is singleton
object learn extends App {
	//try Command Line Interface tools
	//https://github.com/jstrachan/scopt
	//https://github.com/backuity/clist
	var cmd = if (args.length < 1) "null" else args(0)
	cmd match {
		case "str" => learn.str()
		case "ctl" => learn.control()
		case "cls" => learn.cls()
		case "func" => learn.func()
		case opps => println(s"unsupport $opps, <str|ctl|cls>")
	}
}
