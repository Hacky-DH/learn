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
		println(f"${s} ${retio}%.2f") // hello scala 0.80

		var pattern = "[0-9]+".r
		println(pattern.findFirstIn(s)) //None, may return Option Some/None

		implicit class StringU(s:String) {
			def add = s.map(c=>(c+1).toChar)
			def toIntw(radix:Int) = Integer.parseInt(s, radix)
		}
		println(s.add) // real magic!!!  ifmmp!tdbmb
		println("345".toInt)
		println("f0f0".toIntw(16)) // 61680
		println("10101".toIntw(2)) // 21
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
		//hehe 8

		import util.control.Breaks._
		breakable {
			for (i <- 1 to 10) {
				if (i > 4) break
			}
		}
	}
}

object classTest {
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

	// generic type
	trait Pair[A, B] {
		def getKey: A
		def getValue: B
	}

	def randomElement[A](seq :Seq[A]) = {
		seq(util.Random.nextInt(seq.length))
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
		println(classOf[Person]) //class classTest$Person
		println(classOf[String]) //class java.lang.String
		println(e.getClass)//class classTest$Employee

		println(randomElement(Seq("scala","java","python")))
		println(randomElement(List(5,8,7)))
	}
}

object funcTest {
	// function is object
	// Function1[Int, Int]
	// Function1 ~ Function22
	object AddOne extends (Int => Int) {
	  def apply(m: Int): Int = m + 1
	}

	import scala.util.{Try, Success, Failure}
	def readText(file :String) :Try[List[String]] = {
		Try(io.Source.fromFile(file).getLines.toList)
	}

	def toInt(s :String): Option[Int] = {
		try {
			Some(Integer.parseInt(s.trim))
		} catch {
			case e: Exception => None
		}
	}
	def optionTest(){
		readText("LICENSE") match {
			case Success(lines) => lines.foreach(println)
			case Failure(f) => println(f)
		}
		val bag = List("8", "6", "foo", "9", "bar", "5a")
		println(bag.map(toInt)) // List(Some(8), Some(6), None, Some(9), None, None)
		// flatten or flatMap remove the None
		println(bag.map(toInt).flatten) // List(8, 6, 9)
		println(bag.flatMap(toInt)) // List(8, 6, 9)
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

		optionTest()
	}
}

object collectTest {
	// scala collections
	// Array var rw (index)
	// List val ro
	// Set no order
	// Tuple based-1
	// Map Map(1 -> 2) Map.get return Option
	// Option isDefined get getOrElse
	val numbers = Array(1, 2, 3, 4)
	val list = List(1, 2, 3)
	val hostPort = ("localhost", 80)

	// Functional Combinators
	// map foreach filter zip partition find drop dropWhile
	// foldLeft foldRight flatten flatMap
	def test() {
		numbers(3) = 8
		println(numbers(3)) //8
		println(list(2)) // 3
		println(hostPort._1) // localhost

		numbers
			.filter((i: Int) => i % 2 == 0)
			.map((i: Int) => i * 2)
			.foreach(println)

		numbers.partition(_ % 2 == 0)
		numbers.dropWhile(_ % 2 != 0)
		println(numbers.foldLeft(0)((m: Int, n: Int) => m + n)) //14

		val nestedNumbers = List(List(1, 2), List(3, 4))
		nestedNumbers.flatMap(x => x.map(_ * 2)).foreach(println)

		val extensions = Map("steve" -> 100, "bob" -> 101, "joe" -> 201)
		extensions.filter({case (name, extension) => extension < 200})
	}
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
		case "cls" => classTest.cls()
		case "func" => funcTest.func()
		case "col" => collectTest.test()
		case opps => println(s"unsupport $opps, <str|ctl|cls|func|col>")
	}
}
